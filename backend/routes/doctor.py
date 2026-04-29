# ============================================================
#  backend/routes/doctor.py — Doctor Portal
#
#  Accessible only by users with role = 'doctor' or 'admin'
#  Provides:
#    /doctor/               — overview: stats, high-risk alerts
#    /doctor/patients        — full patient list with search/filter
#    /doctor/patients/<id>   — individual patient deep-dive
#    /doctor/api/patients    — JSON list for filtering
#    /doctor/api/assign      — assign/unassign a patient
# ============================================================

from datetime import datetime
from functools import wraps
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify, abort)
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from backend.database import db
from backend.models.user import User
from backend.models.scan import Scan
from ml.config import CLASS_NAMES, SEVERITY_COLORS

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")


# ── Access guard ──────────────────────────────────────────────
def doctor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role not in ("doctor", "admin"):
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── Doctor Dashboard ──────────────────────────────────────────
@doctor_bp.route("/")
@doctor_required
def dashboard():
    stats    = _portal_stats(current_user.id, current_user.role)
    patients = _get_patients(current_user.id, current_user.role, limit=5, sort="recent")
    high_risk = _get_high_risk_patients(current_user.id, current_user.role, limit=10)
    return render_template(
        "doctor_dashboard.html",
        stats=stats,
        recent_patients=patients,
        high_risk_patients=high_risk,
        severity_colors=SEVERITY_COLORS,
        class_names=CLASS_NAMES,
    )


# ── Patient List ──────────────────────────────────────────────
@doctor_bp.route("/patients")
@doctor_required
def patient_list():
    query_str  = request.args.get("q", "").strip()
    grade_filter = request.args.get("grade", "")
    sort       = request.args.get("sort", "recent")
    page       = request.args.get("page", 1, type=int)
    per_page   = 12

    q = _base_patient_query(current_user.id, current_user.role)

    if query_str:
        like = f"%{query_str}%"
        q = q.filter(
            db.or_(User.full_name.ilike(like), User.email.ilike(like))
        )

    patients_raw = q.all()

    # Enrich with scan data
    enriched = []
    for p in patients_raw:
        latest = p.scans.order_by(Scan.created_at.desc()).first()
        if grade_filter != "" and (latest is None or str(latest.predicted_class) != grade_filter):
            continue
        enriched.append({
            "user":       p,
            "latest":     latest,
            "scan_count": p.scan_count,
            "high_risk":  latest and latest.predicted_class is not None and latest.predicted_class >= 3,
        })

    # Sort
    if sort == "risk":
        enriched.sort(key=lambda x: (x["latest"].predicted_class if x["latest"] and x["latest"].predicted_class is not None else -1), reverse=True)
    elif sort == "name":
        enriched.sort(key=lambda x: x["user"].full_name.lower())
    else:  # recent
        enriched.sort(key=lambda x: x["latest"].created_at if x["latest"] else datetime.min, reverse=True)

    # Manual pagination
    total    = len(enriched)
    start    = (page - 1) * per_page
    end      = start + per_page
    items    = enriched[start:end]
    pages    = (total + per_page - 1) // per_page

    return render_template(
        "doctor_patients.html",
        patients=items,
        total=total,
        page=page,
        pages=pages,
        per_page=per_page,
        query_str=query_str,
        grade_filter=grade_filter,
        sort=sort,
        severity_colors=SEVERITY_COLORS,
        class_names=CLASS_NAMES,
    )


# ── Single Patient Detail ─────────────────────────────────────
@doctor_bp.route("/patients/<int:patient_id>")
@doctor_required
def patient_detail(patient_id: int):
    patient = User.query.get_or_404(patient_id)
    if patient.role not in ("patient",) and current_user.role != "admin":
        abort(404)

    scans = (Scan.query
             .filter_by(user_id=patient_id)
             .order_by(Scan.created_at.desc())
             .all())

    # Grade distribution for this patient
    grade_dist = {}
    for s in scans:
        if s.predicted_class is not None:
            grade_dist[s.predicted_class] = grade_dist.get(s.predicted_class, 0) + 1

    # Trend data
    trend = [
        {"date": s.created_at.strftime("%Y-%m-%d"), "grade": s.predicted_class,
         "label": s.class_name, "color": s.severity_color, "scan_id": s.id}
        for s in reversed(scans) if s.predicted_class is not None
    ]

    high_risk = any(s.predicted_class is not None and s.predicted_class >= 3 for s in scans)

    return render_template(
        "doctor_patient_detail.html",
        patient=patient,
        scans=scans,
        grade_dist=grade_dist,
        trend=trend,
        high_risk=high_risk,
        severity_colors=SEVERITY_COLORS,
        class_names=CLASS_NAMES,
    )


# ── API: Save doctor note on any scan ────────────────────────
@doctor_bp.route("/scans/<int:scan_id>/notes", methods=["POST"])
@doctor_required
def add_note(scan_id: int):
    scan = Scan.query.get_or_404(scan_id)
    scan.doctor_notes = request.json.get("notes", "")
    scan.reviewed_by  = current_user.full_name
    scan.reviewed_at  = datetime.utcnow()
    db.session.commit()
    return jsonify({"status": "saved"})


# ── API: Assign patient to current doctor ─────────────────────
@doctor_bp.route("/api/assign", methods=["POST"])
@doctor_required
def assign_patient():
    patient_id = request.json.get("patient_id")
    action     = request.json.get("action", "assign")   # 'assign' | 'unassign'
    patient    = User.query.get_or_404(patient_id)

    if action == "assign":
        patient.assigned_doctor_id = current_user.id
        msg = f"Patient {patient.full_name} assigned to you."
    else:
        patient.assigned_doctor_id = None
        msg = f"Patient {patient.full_name} unassigned."

    db.session.commit()
    return jsonify({"status": "ok", "message": msg})


# ── API: JSON list ────────────────────────────────────────────
@doctor_bp.route("/api/patients")
@doctor_required
def api_patients():
    patients = _base_patient_query(current_user.id, current_user.role).all()
    result = []
    for p in patients:
        latest = p.scans.order_by(Scan.created_at.desc()).first()
        result.append({
            "id":         p.id,
            "full_name":  p.full_name,
            "email":      p.email,
            "age":        p.age,
            "scan_count": p.scan_count,
            "latest_class": latest.predicted_class if latest else None,
            "latest_class_name": latest.class_name if latest else "No scans",
            "latest_color": latest.severity_color if latest else "#6c757d",
            "latest_date":  latest.created_at.isoformat() if latest else None,
        })
    return jsonify(result)


# ── Helpers ───────────────────────────────────────────────────
def _base_patient_query(doctor_id, role):
    """
    Admins see all patients.
    Doctors see: their assigned patients + any unassigned patients.
    """
    q = User.query.filter(User.role == "patient", User.is_active_acc == True)
    if role != "admin":
        q = q.filter(
            db.or_(
                User.assigned_doctor_id == doctor_id,
                User.assigned_doctor_id == None,
            )
        )
    return q


def _get_patients(doctor_id, role, limit=5, sort="recent"):
    patients = _base_patient_query(doctor_id, role).all()
    enriched = []
    for p in patients:
        latest = p.scans.order_by(Scan.created_at.desc()).first()
        enriched.append({"user": p, "latest": latest})
    if sort == "recent":
        enriched.sort(key=lambda x: x["latest"].created_at if x["latest"] else datetime.min, reverse=True)
    return enriched[:limit]


def _get_high_risk_patients(doctor_id, role, limit=10):
    """Return patients whose latest scan is grade >= 3."""
    patients = _base_patient_query(doctor_id, role).all()
    high = []
    for p in patients:
        latest = p.scans.order_by(Scan.created_at.desc()).first()
        if latest and latest.predicted_class is not None and latest.predicted_class >= 3:
            high.append({"user": p, "latest": latest})
    high.sort(key=lambda x: x["latest"].predicted_class, reverse=True)
    return high[:limit]


def _portal_stats(doctor_id, role):
    patients = _base_patient_query(doctor_id, role).all()
    total_patients = len(patients)

    all_latest_scans = []
    for p in patients:
        s = p.scans.order_by(Scan.created_at.desc()).first()
        if s:
            all_latest_scans.append(s)

    high_risk_count  = sum(1 for s in all_latest_scans if s.predicted_class is not None and s.predicted_class >= 3)
    total_scans      = sum(p.scan_count for p in patients)
    unreviewed_count = Scan.query.filter(
        Scan.user_id.in_([p.id for p in patients]),
        Scan.doctor_notes == None
    ).count()

    return {
        "total_patients":  total_patients,
        "high_risk_count": high_risk_count,
        "total_scans":     total_scans,
        "unreviewed_count": unreviewed_count,
    }
