# backend/models/user.py -- Patient/User database model

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20), default="patient")  # patient | doctor | admin

    # Doctor assignment (for patients)
    assigned_doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    assigned_doctor    = db.relationship("User", remote_side="User.id",
                                         foreign_keys="User.assigned_doctor_id")

    # Personal details
    full_name     = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender        = db.Column(db.String(20), nullable=True)
    phone         = db.Column(db.String(30), nullable=True)
    address       = db.Column(db.Text, nullable=True)

    # Medical details
    diabetes_type     = db.Column(db.String(30), nullable=True)
    diabetes_duration = db.Column(db.Integer, nullable=True)
    hba1c             = db.Column(db.Float, nullable=True)
    blood_pressure    = db.Column(db.String(20), nullable=True)
    medications       = db.Column(db.Text, nullable=True)
    notes             = db.Column(db.Text, nullable=True)

    # Meta
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_login    = db.Column(db.DateTime, nullable=True)
    is_active_acc = db.Column(db.Boolean, default=True)

    # Relationships
    scans = db.relationship("Scan", backref="patient", lazy="dynamic",
                            cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def age(self):
        if self.date_of_birth:
            today = datetime.utcnow().date()
            dob   = self.date_of_birth
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return None

    @property
    def latest_scan(self):
        from backend.models.scan import Scan
        return self.scans.order_by(Scan.created_at.desc()).first()

    @property
    def scan_count(self):
        return self.scans.count()

    def to_dict(self):
        return {
            "id":               self.id,
            "email":            self.email,
            "full_name":        self.full_name,
            "role":             self.role,
            "date_of_birth":    self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender":           self.gender,
            "phone":            self.phone,
            "address":          self.address,
            "diabetes_type":    self.diabetes_type,
            "diabetes_duration": self.diabetes_duration,
            "hba1c":            self.hba1c,
            "blood_pressure":   self.blood_pressure,
            "medications":      self.medications,
            "notes":            self.notes,
            "age":              self.age,
            "scan_count":       self.scan_count,
            "created_at":       self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<User {self.email}>"
