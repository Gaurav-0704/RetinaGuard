# ============================================================
#  backend/routes/patients.py — Patient Profile Management
# ============================================================

from datetime import datetime, date
from flask import (Blueprint, render_template, redirect,
                   url_for, flash, request, jsonify)
from flask_login import login_required, current_user
from backend.database import db
from backend.models.user import User

patients_bp = Blueprint("patients", __name__, url_prefix="/profile")


@patients_bp.route("/", methods=["GET"])
@login_required
def view_profile():
    return render_template("profile.html", user=current_user)


@patients_bp.route("/complete", methods=["GET", "POST"])
@login_required
def complete_profile():
    """First-time profile completion after registration."""
    if request.method == "POST":
        _update_user_from_form(current_user, request.form)
        db.session.commit()
        flash("Profile saved successfully!", "success")
        return redirect(url_for("dashboard.home"))
    return render_template("profile.html", user=current_user, first_time=True)


@patients_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        _update_user_from_form(current_user, request.form)
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("patients.view_profile"))
    return render_template("profile.html", user=current_user, editing=True)


@patients_bp.route("/api/me", methods=["GET"])
@login_required
def api_me():
    return jsonify(current_user.to_dict())


# ── Helper ────────────────────────────────────────────────────
def _update_user_from_form(user: User, form):
    user.full_name         = form.get("full_name", user.full_name).strip()
    user.phone             = form.get("phone", "").strip() or None
    user.address           = form.get("address", "").strip() or None
    user.gender            = form.get("gender") or None
    user.diabetes_type     = form.get("diabetes_type") or None
    user.medications       = form.get("medications", "").strip() or None
    user.notes             = form.get("notes", "").strip() or None

    dob_str = form.get("date_of_birth", "")
    if dob_str:
        try:
            user.date_of_birth = date.fromisoformat(dob_str)
        except ValueError:
            pass

    dur = form.get("diabetes_duration", "")
    if dur.isdigit():
        user.diabetes_duration = int(dur)

    hba1c_str = form.get("hba1c", "")
    try:
        user.hba1c = float(hba1c_str) if hba1c_str else None
    except ValueError:
        pass

    user.blood_pressure = form.get("blood_pressure", "").strip() or None
