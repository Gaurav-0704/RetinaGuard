"""
Tests for the ml.predict inference wrapper.
I test demo mode (no weights) separately from the real-model path so these
tests run anywhere without a GPU or trained checkpoint.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from ml.predict import _demo_predict, _build_result, predict


FAKE_PATH = "/tmp/fake_retina_image.png"


class TestDemoPredict:
    def test_returns_required_keys(self):
        result = _demo_predict(FAKE_PATH)
        required = {
            "predicted_class", "class_name", "confidence",
            "probabilities", "class_names", "severity_color",
            "advice", "gradcam_image", "demo_mode",
        }
        assert required.issubset(result.keys())

    def test_demo_mode_flag_is_true(self):
        result = _demo_predict(FAKE_PATH)
        assert result["demo_mode"] is True

    def test_gradcam_is_none_in_demo(self):
        result = _demo_predict(FAKE_PATH)
        assert result["gradcam_image"] is None

    def test_probabilities_sum_to_one(self):
        result = _demo_predict(FAKE_PATH)
        total = sum(result["probabilities"])
        assert abs(total - 1.0) < 1e-4

    def test_predicted_class_matches_max_prob(self):
        result = _demo_predict(FAKE_PATH)
        probs = result["probabilities"]
        assert result["predicted_class"] == probs.index(max(probs))

    def test_confidence_within_range(self):
        result = _demo_predict(FAKE_PATH)
        assert 0.0 <= result["confidence"] <= 100.0

    def test_five_classes_returned(self):
        result = _demo_predict(FAKE_PATH)
        assert len(result["probabilities"]) == 5
        assert len(result["class_names"]) == 5

    def test_deterministic_per_filename(self):
        r1 = _demo_predict("/tmp/image_a.png")
        r2 = _demo_predict("/tmp/image_a.png")
        r3 = _demo_predict("/tmp/image_b.png")
        assert r1["predicted_class"] == r2["predicted_class"]
        assert r1["probabilities"] == r2["probabilities"]
        # Different filename should (almost certainly) produce different probs
        # — we just verify it runs without error for a second path
        assert isinstance(r3["predicted_class"], int)


class TestPredictDispatch:
    def test_predict_uses_demo_when_no_weights(self, tmp_path):
        """predict() should fall back to demo mode when no .pth file exists."""
        fake_image = tmp_path / "retina.png"
        fake_image.write_bytes(b"\x89PNG\r\n\x1a\n")  # minimal PNG header

        with patch("ml.predict._get_model", return_value=(None, "cpu")):
            result = predict(str(fake_image))

        assert result["demo_mode"] is True

    def test_predict_falls_back_to_demo_on_model_error(self, tmp_path):
        """If real inference throws, predict() must not crash — demo result instead."""
        fake_image = tmp_path / "retina.png"
        fake_image.write_bytes(b"\x89PNG\r\n\x1a\n")

        mock_model = MagicMock(side_effect=RuntimeError("CUDA OOM"))
        with patch("ml.predict._get_model", return_value=(mock_model, "cpu")):
            result = predict(str(fake_image))

        assert result["demo_mode"] is True
        assert "predicted_class" in result
