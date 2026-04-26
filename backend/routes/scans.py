# ============================================================
#  backend/routes/scans.py — Scan Upload, Screening & History
# ============================================================

import os
import uuid
from datetime import datetime
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify, current_app, abort)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from backend.database import db
from backend.models.scan import Scan
from ml.predict import predict

scans_bp = Blueprint("scans", __name__, url_prefix="/scans")


def _allowed_file(filename: str) -> bool:
    allowed = current_app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


# ── New Scan page ─────────────────────────────────────────────
@scans_bp.route("/new", methods=["GET"])
@login_required
def new_scan():
    return render_template("scan.html")


@scans_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    """
    Accepts a retinal image upload, runs screening analysis, saves to DB.
    Returns JSON — the frontend fetches this endpoint via JS.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image provided."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use PNG, JPG, JPEG, TIFF or BMP."}), 400

    # Save with a UUID filename to avoid collisions
    ext          = file.filename.rsplit(".", 1)[1].lower()
    unique_name  = f"{uuid.uuid4().hex}.{ext}"
    save_path    = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file.save(save_path)

    # Run screening analysis
    result = predict(save_path)

    # Persist to database
    scan = Scan(
        user_id         = current_user.id,
        filename        = unique_name,
        original_name   = secure_filename(file.filename),
        eye_side        = request.form.get("eye_side") or None,
        predicted_class = result["predicted_class"],
        class_name      = result["class_name"],
        confidence      = result["confidence"],
        severity_color  = result["severity_color"],
        advice          = result["advice"],
        gradcam_image   = result.get("gradcam_image"),
        demo_mode       = result.get("demo_mode", False),
    )
    scan.probabilities = result["probabilities"]

    db.session.add(scan)
    db.session.commit()

    return jsonify({
        "scan_id":        scan.id,
        "predicted_class": result["predicted_class"],
        "class_name":      result["class_name"],
        "confidence":      result["confidence"],
        "probabilities":   result["probabilities"],
        "class_names":     result["class_names"],
        "severity_color":  result["severity_color"],
        "advice":          result["advice"],
        "gradcam_image":   result.get("gradcam_image"),
        "demo_mode":       result.get("demo_mode", False),
        "created_at":      scan.created_at.isoformat(),
    })


# ── Scan Result page ──────────────────────────────────────────
@scans_bp.route("/<int:scan_id>", methods=["GET"])
@login_required
def result(scan_id: int):
    scan = Scan.query.get_or_404(scan_id)
    if scan.user_id != current_user.id and current_user.role not in ("doctor", "admin"):
        abort(403)
    return render_template("result.html", scan=scan)


# ── History page ──────────────────────────────────────────────
@scans_bp.route("/history", methods=["GET"])
@login_required
def history():
    page     = request.args.get("page", 1, type=int)
    per_page = 10
    scans    = (Scan.query
                .filter_by(user_id=current_user.id)
                .order_by(Scan.created_at.desc())
                .paginate(page=page, per_page=per_page, error_out=False))
    return render_template("history.html", scans=scans)


# ── Delete a scan ─────────────────────────────────────────────
@scans_bp.route("/<int:scan_id>/delete", methods=["POST"])
@login_required
def delete_scan(scan_id: int):
    scan = Scan.query.get_or_404(scan_id)
    if scan.user_id != current_user.id:
        abort(403)

    # Remove image file
    img_path = os.path.join(current_app.config["UPLOAD_FOLDER"], scan.filename)
    if os.path.exists(img_path):
        os.remove(img_path)

    db.session.delete(scan)
    db.session.commit()
    flash("Scan deleted.", "info")
    return redirect(url_for("scans.history"))


# ── Doctor Notes API ──────────────────────────────────────────
@scans_bp.route("/<int:scan_id>/notes", methods=["POST"])
@login_required
def add_notes(scan_id: int):
    scan = Scan.query.get_or_404(scan_id)
    if current_user.role not in ("doctor", "admin") and scan.user_id != current_user.id:
        abort(403)
    scan.doctor_notes = request.json.get("notes", "")
    scan.reviewed_by  = current_user.full_name
    scan.reviewed_at  = datetime.utcnow()
    db.session.commit()
    return jsonify({"status": "saved"})


# ── API: all scans for current user (JSON) ───────────────────
@scans_bp.route("/api/mine", methods=["GET"])
@login_required
def api_mine():
    scans = (Scan.query
             .filter_by(user_id=current_user.id)
             .order_by(Scan.created_at.desc())
             .all())
    return jsonify([s.to_dict() for s in scans])
