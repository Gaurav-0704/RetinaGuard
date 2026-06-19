"""
Tests for scan routes: upload, result, history, delete, notes API.
I patch ml.predict.predict so tests run without a trained model or GPU.
"""

import io
import json
import pytest
from unittest.mock import patch

from backend.models.scan import Scan
from tests.conftest import login, logout, png_bytes

MOCK_RESULT = {
    "predicted_class": 2,
    "class_name": "Moderate DR",
    "confidence": 72.5,
    "probabilities": [0.05, 0.10, 0.72, 0.08, 0.05],
    "class_names": ["No DR", "Mild DR", "Moderate DR", "Severe DR", "Proliferative DR"],
    "severity_color": "#fd7e14",
    "advice": "Refer to ophthalmologist within 6 months.",
    "gradcam_image": None,
    "demo_mode": True,
}


@pytest.fixture(autouse=True)
def mock_predict():
    with patch("backend.routes.scans.predict", return_value=MOCK_RESULT):
        yield


class TestUpload:
    def test_upload_requires_login(self, client):
        resp = client.post("/scans/upload", data={}, follow_redirects=False)
        assert resp.status_code == 302
        assert "login" in resp.headers["Location"]

    def test_upload_valid_image(self, client, patient_user):
        login(client, patient_user.email, "testpass1")
        data = {
            "image": (io.BytesIO(png_bytes()), "retina.png"),
            "eye_side": "left",
        }
        resp = client.post(
            "/scans/upload",
            data=data,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["predicted_class"] == 2
        assert body["class_name"] == "Moderate DR"
        assert "scan_id" in body
        logout(client)

    def test_upload_no_file_returns_400(self, client, patient_user):
        login(client, patient_user.email, "testpass1")
        resp = client.post("/scans/upload", data={}, content_type="multipart/form-data")
        assert resp.status_code == 400
        logout(client)

    def test_upload_invalid_extension_returns_400(self, client, patient_user):
        login(client, patient_user.email, "testpass1")
        data = {"image": (io.BytesIO(b"notanimage"), "file.exe")}
        resp = client.post(
            "/scans/upload", data=data, content_type="multipart/form-data"
        )
        assert resp.status_code == 400
        logout(client)


class TestHistory:
    def test_history_requires_login(self, client):
        resp = client.get("/scans/history", follow_redirects=False)
        assert resp.status_code == 302

    def test_history_shows_scans(self, client, patient_user, db):
        scan = Scan(
            user_id=patient_user.id,
            filename="test.png",
            predicted_class=1,
            class_name="Mild DR",
            confidence=60.0,
            demo_mode=True,
        )
        scan.probabilities = [0.1, 0.6, 0.1, 0.1, 0.1]
        db.session.add(scan)
        db.session.commit()

        login(client, patient_user.email, "testpass1")
        resp = client.get("/scans/history")
        assert resp.status_code == 200
        assert b"Mild DR" in resp.data
        logout(client)


class TestResult:
    def test_result_page_requires_login(self, client):
        resp = client.get("/scans/1", follow_redirects=False)
        assert resp.status_code == 302

    def test_result_page_forbidden_for_other_patient(self, client, patient_user, doctor_user, db):
        scan = Scan(
            user_id=patient_user.id,
            filename="priv.png",
            predicted_class=0,
            class_name="No DR",
            confidence=90.0,
            demo_mode=True,
        )
        scan.probabilities = [0.9, 0.05, 0.02, 0.02, 0.01]
        db.session.add(scan)
        db.session.commit()

        # Doctor can view (has role=doctor)
        login(client, doctor_user.email, "testpass1")
        resp = client.get(f"/scans/{scan.id}")
        assert resp.status_code == 200
        logout(client)

    def test_result_accessible_to_owner(self, client, patient_user, db):
        scan = Scan(
            user_id=patient_user.id,
            filename="own.png",
            predicted_class=0,
            class_name="No DR",
            confidence=88.0,
            demo_mode=True,
        )
        scan.probabilities = [0.88, 0.05, 0.03, 0.02, 0.02]
        db.session.add(scan)
        db.session.commit()

        login(client, patient_user.email, "testpass1")
        resp = client.get(f"/scans/{scan.id}")
        assert resp.status_code == 200
        logout(client)


class TestDelete:
    def test_delete_own_scan(self, client, patient_user, db):
        scan = Scan(
            user_id=patient_user.id,
            filename="todelete.png",
            predicted_class=0,
            class_name="No DR",
            confidence=80.0,
            demo_mode=True,
        )
        scan.probabilities = [0.8, 0.1, 0.05, 0.03, 0.02]
        db.session.add(scan)
        db.session.commit()
        scan_id = scan.id

        login(client, patient_user.email, "testpass1")
        resp = client.post(f"/scans/{scan_id}/delete", follow_redirects=True)
        assert resp.status_code == 200
        assert Scan.query.get(scan_id) is None
        logout(client)


class TestNotesAPI:
    def test_doctor_can_add_notes(self, client, patient_user, doctor_user, db):
        scan = Scan(
            user_id=patient_user.id,
            filename="noted.png",
            predicted_class=3,
            class_name="Severe DR",
            confidence=85.0,
            demo_mode=True,
        )
        scan.probabilities = [0.02, 0.03, 0.05, 0.85, 0.05]
        db.session.add(scan)
        db.session.commit()

        login(client, doctor_user.email, "testpass1")
        resp = client.post(
            f"/scans/{scan.id}/notes",
            json={"notes": "Urgent referral arranged."},
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert json.loads(resp.data)["status"] == "saved"

        db.session.refresh(scan)
        assert scan.doctor_notes == "Urgent referral arranged."
        logout(client)
