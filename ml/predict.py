# ============================================================
#  ml/predict.py — RetinaGuard Screening Engine + Diagnostic Focus Mapping
#
#  Two modes:
#  1. REAL MODE  — uses a trained .pth checkpoint
#  2. DEMO MODE  — returns realistic simulated results
#     (active when no weights file is found; lets you run the
#      full web app before training is complete)
#
#  Diagnostic focus mapping: produces a colour overlay on the retinal image
#  showing WHICH region influenced the severity assessment most.
#  This is critical for clinical trust and explainability.
# ============================================================

import os
import io
import base64
import logging
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
import cv2

from ml.config import (
    BEST_MODEL_PATH, CLASS_NAMES, SEVERITY_COLORS, SEVERITY_ADVICE,
    NORM_MEAN, NORM_STD, IMAGE_SIZE,
)
from ml.model import build_model, load_trained_model, get_device
from ml.preprocessing import get_val_transforms, apply_clahe

logger = logging.getLogger(__name__)

# ── Module-level singletons (load once per process) ──────────
_model = None
_device = None


def _get_model():
    global _model, _device
    if _model is None:
        _device = get_device()
        os.makedirs(os.path.dirname(BEST_MODEL_PATH), exist_ok=True)
        if os.path.exists(BEST_MODEL_PATH):
            logger.info("Loading trained RetinaGuard weights from %s", BEST_MODEL_PATH)
            _model = load_trained_model(BEST_MODEL_PATH, _device)
        else:
            logger.warning(
                "No trained weights found at %s — running in DEMO mode.", BEST_MODEL_PATH
            )
            _model = None  # signals demo mode
    return _model, _device


# ── Diagnostic Focus Mapping ──────────────────────────────────

class GradCAM:
    """
    Diagnostic focus mapping for the screening engine.
    Hooks the last feature block to capture region-level activation weights.
    """

    def __init__(self, model: torch.nn.Module):
        self.model = model
        self.activations = None
        self.gradients = None
        self._register_hooks()

    def _register_hooks(self):
        # Target: last block of EfficientNet features
        target_layer = self.model.features[-1]

        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()

        target_layer.register_forward_hook(forward_hook)
        target_layer.register_full_backward_hook(backward_hook)

    def generate(self, input_tensor: torch.Tensor, class_idx: int) -> np.ndarray:
        """
        Returns a normalised (0–1) CAM as a 2-D numpy array.
        """
        self.model.zero_grad()
        output = self.model(input_tensor)
        output[0, class_idx].backward()

        # Global average pool the gradients
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = cam.squeeze().cpu().numpy()

        # Normalise
        cam -= cam.min()
        if cam.max() > 0:
            cam /= cam.max()
        return cam


def _overlay_heatmap(original_pil: Image.Image, cam: np.ndarray) -> str:
    """
    Overlay a diagnostic focus map on the original retinal image.
    Returns a base64-encoded PNG string for embedding in HTML.
    """
    orig_np = np.array(original_pil.resize((IMAGE_SIZE, IMAGE_SIZE)))
    cam_resized = cv2.resize(cam, (IMAGE_SIZE, IMAGE_SIZE))
    heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    overlay = cv2.addWeighted(orig_np, 0.55, heatmap, 0.45, 0)
    overlay_pil = Image.fromarray(overlay)

    buf = io.BytesIO()
    overlay_pil.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# ── Demo mode ────────────────────────────────────────────────

def _demo_predict(image_path: str) -> dict:
    """
    Simulate a realistic prediction when no model weights are available.
    Probabilities are seeded from the image filename for reproducibility.
    """
    import hashlib, random
    seed = int(hashlib.md5(image_path.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)

    raw = [rng.random() for _ in range(5)]
    total = sum(raw)
    probs = [round(r / total, 4) for r in raw]
    pred_class = probs.index(max(probs))
    confidence = round(max(probs) * 100, 1)

    return _build_result(pred_class, probs, confidence, None, image_path, demo=True)


# ── Real prediction ──────────────────────────────────────────

def predict(image_path: str) -> dict:
    """
    Run screening analysis on a retinal fundus image.

    Parameters
    ----------
    image_path : str  –  absolute path to the uploaded image

    Returns
    -------
    dict with keys:
        predicted_class   int
        class_name        str
        confidence        float  (0-100)
        probabilities     list[float]  length 5
        severity_color    str  (hex)
        advice            str
        gradcam_image     str  (base64 PNG) or None
        demo_mode         bool
    """
    model, device = _get_model()
    if model is None:
        return _demo_predict(image_path)

    try:
        original_pil = Image.open(image_path).convert("RGB")
        transforms = get_val_transforms()
        input_tensor = transforms(original_pil).unsqueeze(0).to(device)

        cam_gen = GradCAM(model)
        model.eval()

        with torch.set_grad_enabled(True):
            output = model(input_tensor)
            probs_tensor = F.softmax(output, dim=1)[0]
            pred_class = probs_tensor.argmax().item()
            probs = [round(p, 4) for p in probs_tensor.cpu().tolist()]
            confidence = round(probs[pred_class] * 100, 1)

        # Diagnostic focus map
        cam = cam_gen.generate(input_tensor, pred_class)
        gradcam_b64 = _overlay_heatmap(original_pil, cam)

        return _build_result(pred_class, probs, confidence, gradcam_b64, image_path, demo=False)

    except Exception as exc:
        logger.error("Screening analysis failed: %s", exc, exc_info=True)
        return _demo_predict(image_path)


def _build_result(pred_class, probs, confidence, gradcam_b64, image_path, demo):
    return {
        "predicted_class": pred_class,
        "class_name":      CLASS_NAMES[pred_class],
        "confidence":      confidence,
        "probabilities":   probs,
        "class_names":     list(CLASS_NAMES.values()),
        "severity_color":  SEVERITY_COLORS[pred_class],
        "advice":          SEVERITY_ADVICE[pred_class],
        "gradcam_image":   gradcam_b64,
        "demo_mode":       demo,
    }
