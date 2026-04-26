# ============================================================
#  ml/preprocessing.py — RetinaGuard Image Preprocessing
#
#  Key upgrade over the original:
#  1. CLAHE (Contrast Limited Adaptive Histogram Equalization)
#     → dramatically improves visibility of microaneurysms,
#       haemorrhages and exudates in retinal images.
#  2. Rich augmentation pipeline (train) vs clean pipeline (screening)
#  3. Fully composable — swap transforms without touching model code
# ============================================================

import cv2
import numpy as np
from PIL import Image
import torchvision.transforms as T

from ml.config import (
    IMAGE_SIZE, NORM_MEAN, NORM_STD,
    CLAHE_CLIP_LIMIT, CLAHE_TILE_GRID,
    AUG_HFLIP_PROB, AUG_VFLIP_PROB,
    AUG_ROTATE_DEG, AUG_BRIGHTNESS,
    AUG_CONTRAST, AUG_SATURATION, AUG_HUE,
)


# ── CLAHE helper ─────────────────────────────────────────────

def apply_clahe(pil_image: Image.Image) -> Image.Image:
    """
    Apply CLAHE to each channel of an RGB PIL image.
    Returns an enhanced PIL image ready for further transforms.
    CLAHE boosts local contrast, making DR lesions more visible.
    """
    img_np = np.array(pil_image)

    # Convert to LAB colour space; apply CLAHE only on L channel
    lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
    l_ch, a_ch, b_ch = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=CLAHE_CLIP_LIMIT,
        tileGridSize=CLAHE_TILE_GRID,
    )
    l_eq = clahe.apply(l_ch)

    lab_eq = cv2.merge([l_eq, a_ch, b_ch])
    img_enhanced = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2RGB)
    return Image.fromarray(img_enhanced)


class CLAHETransform:
    """Torchvision-compatible wrapper around apply_clahe."""
    def __call__(self, img: Image.Image) -> Image.Image:
        return apply_clahe(img)


# ── Transform pipelines ──────────────────────────────────────

def get_train_transforms() -> T.Compose:
    """
    Augmented pipeline for training.
    Order: CLAHE → resize → spatial augs → colour jitter → tensor → normalise
    """
    return T.Compose([
        CLAHETransform(),
        T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        T.RandomHorizontalFlip(p=AUG_HFLIP_PROB),
        T.RandomVerticalFlip(p=AUG_VFLIP_PROB),
        T.RandomRotation(degrees=AUG_ROTATE_DEG),
        T.ColorJitter(
            brightness=AUG_BRIGHTNESS,
            contrast=AUG_CONTRAST,
            saturation=AUG_SATURATION,
            hue=AUG_HUE,
        ),
        T.ToTensor(),
        T.Normalize(mean=NORM_MEAN, std=NORM_STD),
    ])


def get_val_transforms() -> T.Compose:
    """
    Clean pipeline for validation / inference.
    CLAHE is still applied so the model sees the same contrast enhancement.
    """
    return T.Compose([
        CLAHETransform(),
        T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        T.ToTensor(),
        T.Normalize(mean=NORM_MEAN, std=NORM_STD),
    ])


def load_image(path: str) -> Image.Image:
    """Load an image from disk as an RGB PIL Image."""
    return Image.open(path).convert("RGB")
