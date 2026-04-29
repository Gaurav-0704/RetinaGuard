# ============================================================
#  backend/routes/dashboard.py — Dashboard & Stats
# ============================================================

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from backend.database import db
from backend.models.scan import Scan
from ml.config import CLASS_NAMES, SEVERITY_COLORS

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/", methods=["GET"])
@login_required
def home():
    stats = _get_stats(current_user.id)
    recent_scans = (Scan.query
                    .filter_by(user_id=current_user.id)
                    .order_by(Scan.created_at.desc())
                    .limit(5).all())
    return render_template("dashboard.html",
                           stats=stats,
                           recent_scans=recent_scans,
                           class_names=CLASS_NAMES,
                           severity_colors=SEVERITY_COLORS)


@dashboard_bp.route("/api/stats", methods=["GET"])
@login_required
def api_stats():
    return jsonify(_get_stats(current_user.id))


@dashboard_bp.route("/api/trend", methods=["GET"])
@login_required
def api_trend():
    """Return severity over time for the current user (for charts)."""
    scans = (Scan.query
             .filter_by(user_id=current_user.id)
             .order_by(Scan.created_at.asc())
             .all())
    data = [
        {
            "date":  s.created_at.strftime("%Y-%m-%d"),
            "grade": s.predicted_class,
            "label": s.class_name,
            "color": s.severity_color,
        }
        for s in scans if s.predicted_class is not None
    ]
    return jsonify(data)


# ── Helper ─────────────────────────────────────────────────────
def _get_stats(user_id: int) -> dict:
    total = Scan.query.filter_by(user_id=user_id).count()

    # Grade distribution
    rows = (db.session.query(Scan.predicted_class, func.count(Scan.id))
            .filter(Scan.user_id == user_id)
            .group_by(Scan.predicted_class)
            .all())
    distribution = {int(r[0]): r[1] for r in rows if r[0] is not None}

    # Latest scan
    latest = (Scan.query.filter_by(user_id=user_id)
              .order_by(Scan.created_at.desc()).first())

    # Risk flag — any scan grade >= 3
    high_risk = any(g >= 3 for g in distribution.keys() if distribution.get(g, 0) > 0)

    return {
        "total_scans":      total,
        "grade_distribution": distribution,
        "latest_class":     latest.predicted_class if latest else None,
        "latest_class_name": latest.class_name if latest else "No scans yet",
        "latest_color":     latest.severity_color if latest else "#6c757d",
        "latest_date":      latest.created_at.strftime("%b %d, %Y") if latest else None,
        "high_risk":        high_risk,
    }
