#!/usr/bin/env python
# ============================================================
#  setup_db.py — Initialize the RetinaGuard database
#
#  Run once before first launch:
#    python setup_db.py
#
#  Optionally create a demo admin account:
#    python setup_db.py --demo
# ============================================================

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app
from backend.database import db
from backend.models.user import User


def setup(create_demo: bool = False):
    app = create_app("development")
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✓ Database tables created.")

        if create_demo:
            from datetime import date
            doctor = User(
                full_name="Dr. Admin",
                email="admin@retinoguard.com",
                role="doctor",
            )
            doctor.set_password("admin1234")
            db.session.add(doctor)
            db.session.flush()  # get doctor.id before commit

            demo = User(
                full_name="Demo Patient",
                email="demo@retinoguard.com",
                role="patient",
                diabetes_type="Type 2",
                hba1c=7.5,
                date_of_birth=date(1985, 6, 15),
                gender="Male",
                assigned_doctor_id=doctor.id,
            )
            demo.set_password("demo1234")
            db.session.add(demo)

            db.session.commit()
            print("✓ Demo accounts created:")
            print("  Patient — demo@retinoguard.com  / demo1234")
            print("  Doctor  — admin@retinoguard.com / admin1234")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Create demo accounts")
    args = parser.parse_args()
    setup(create_demo=args.demo)
    print("\nRetinaGuard database setup complete. Run: python run.py")
