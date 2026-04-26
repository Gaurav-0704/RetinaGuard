# ============================================================
#  ml/config.py — RetinaGuard ML Configuration
#  All hyperparameters and paths in one place.
#  Edit this file to tune training without touching other code.
# ============================================================

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Model ────────────────────────────────────────────────────
MODEL_NAME        = "efficientnet_b4"   # backbone identifier
NUM_CLASSES       = 5                   # DR grades 0-4
IMAGE_SIZE        = 512                 # pixels (H = W)
DROPOUT_RATE      = 0.4

# ── Training ─────────────────────────────────────────────────
BATCH_SIZE        = 16
NUM_EPOCHS        = 60
LEARNING_RATE     = 1e-4
WEIGHT_DECAY      = 1e-5
LR_PATIENCE       = 5                  # ReduceLROnPlateau patience
EARLY_STOP_PATIENCE = 12
SEED              = 42
TRAIN_SPLIT       = 0.80               # 80 % train, 20 % val

# ── Augmentation ─────────────────────────────────────────────
AUG_HFLIP_PROB    = 0.5
AUG_VFLIP_PROB    = 0.3
AUG_ROTATE_DEG    = 30
AUG_BRIGHTNESS    = 0.2
AUG_CONTRAST      = 0.2
AUG_SATURATION    = 0.2
AUG_HUE           = 0.05
CLAHE_CLIP_LIMIT  = 2.0
CLAHE_TILE_GRID   = (8, 8)

# ── ImageNet normalisation (used for pretrained backbone) ────
NORM_MEAN         = (0.485, 0.456, 0.406)
NORM_STD          = (0.229, 0.224, 0.225)

# ── Paths ─────────────────────────────────────────────────────
WEIGHTS_DIR       = os.path.join(BASE_DIR, "..", "backend", "weights")
BEST_MODEL_PATH   = os.path.join(WEIGHTS_DIR, "retinoguard_best.pth")

# ── Class labels ─────────────────────────────────────────────
CLASS_NAMES = {
    0: "No DR",
    1: "Mild DR",
    2: "Moderate DR",
    3: "Severe DR",
    4: "Proliferative DR",
}

SEVERITY_COLORS = {
    0: "#28a745",   # green
    1: "#ffc107",   # yellow
    2: "#fd7e14",   # orange
    3: "#dc3545",   # red
    4: "#6f1d1b",   # dark red
}

SEVERITY_ADVICE = {
    0: "No signs of diabetic retinopathy detected. Maintain regular check-ups annually.",
    1: "Mild non-proliferative DR. Monitor closely; revisit in 9–12 months.",
    2: "Moderate non-proliferative DR. Refer to ophthalmologist; revisit in 6 months.",
    3: "Severe non-proliferative DR. Urgent ophthalmologist referral recommended.",
    4: "Proliferative DR. Immediate specialist intervention required.",
}
