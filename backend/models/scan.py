# ============================================================
#  backend/models/scan.py — Scan / Report database model
# ============================================================

import json
from datetime import datetime
from backend.database import db


class Scan(db.Model):
    __tablename__ = "scans"

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Image file
    filename        = db.Column(db.String(255), nullable=False)
    original_name   = db.Column(db.String(255), nullable=True)
    eye_side        = db.Column(db.String(10), nullable=True)  # 'left' | 'right'

    # Screening result
    predicted_class = db.Column(db.Integer, nullable=True)
    class_name      = db.Column(db.String(50), nullable=True)
    confidence      = db.Column(db.Float, nullable=True)
    _probabilities  = db.Column("probabilities", db.Text, nullable=True)
    severity_color  = db.Column(db.String(10), nullable=True)
    advice          = db.Column(db.Text, nullable=True)
    gradcam_image   = db.Column(db.Text, nullable=True)   # base64 PNG
    demo_mode       = db.Column(db.Boolean, default=False)

    # Clinical
    doctor_notes    = db.Column(db.Text, nullable=True)
    reviewed_by     = db.Column(db.String(120), nullable=True)
    reviewed_at     = db.Column(db.DateTime, nullable=True)

    # Meta
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    # ── Probabilities as list ─────────────────────────────────
    @property
    def probabilities(self):
        if self._probabilities:
            return json.loads(self._probabilities)
        return []

    @probabilities.setter
    def probabilities(self, value):
        self._probabilities = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "user_id":          self.user_id,
            "filename":         self.filename,
            "original_name":    self.original_name,
            "eye_side":         self.eye_side,
            "predicted_class":  self.predicted_class,
            "class_name":       self.class_name,
            "confidence":       self.confidence,
            "probabilities":    self.probabilities,
            "severity_color":   self.severity_color,
            "advice":           self.advice,
            "gradcam_image":    self.gradcam_image,
            "demo_mode":        self.demo_mode,
            "doctor_notes":     self.doctor_notes,
            "reviewed_by":      self.reviewed_by,
            "reviewed_at":      self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at":       self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<Scan {self.id} user={self.user_id} class={self.class_name}>"
