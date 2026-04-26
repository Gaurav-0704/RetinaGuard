# backend/app.py -- Flask Application Factory

import os
from flask import Flask, send_from_directory
from backend.config import config_map
from backend.database import db, login_manager
from backend.models.user import User


def create_app(env="default"):
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "static"),
    )
    app.config.from_object(config_map[env])

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from backend.routes.auth import auth_bp
    from backend.routes.patients import patients_bp
    from backend.routes.scans import scans_bp
    from backend.routes.dashboard import dashboard_bp
    from backend.routes.doctor import doctor_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(scans_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(doctor_bp)

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app
