# ============================================================
#  ml/model.py — RetinaGuard Model Architecture
#
#  Upgrade summary vs original (ResNet-34):
#  ┌─────────────────┬──────────────────────────────────────┐
#  │ Original        │ RetinaGuard Upgrade                  │
#  ├─────────────────┼──────────────────────────────────────┤
#  │ ResNet-34       │ EfficientNet-B4 (pre-trained)        │
#  │ Fixed head      │ Adaptive avg pool + custom head      │
#  │ Dropout 0.2/0.5 │ Dropout 0.4 (tuned)                 │
#  │ SGD optimizer   │ AdamW + CosineAnnealingLR            │
#  │ Fixed 45 epochs │ Early stopping + LR scheduling       │
#  └─────────────────┴──────────────────────────────────────┘
#
#  EfficientNet-B4 was chosen because it:
#  • Has ~19M params (vs ResNet-34's 21M) but higher accuracy
#  • Compound scaling (depth + width + resolution simultaneously)
#  • Consistently wins DR grading benchmarks on Kaggle
# ============================================================

import torch
import torch.nn as nn

try:
    # torchvision >= 0.13
    from torchvision.models import efficientnet_b4, EfficientNet_B4_Weights
    _USE_NEW_API = True
except ImportError:
    from torchvision.models import efficientnet_b4
    _USE_NEW_API = False

from ml.config import NUM_CLASSES, DROPOUT_RATE


def build_model(pretrained: bool = True) -> nn.Module:
    """
    Build and return the RetinaGuard classifier.

    Architecture:
        EfficientNet-B4 backbone (ImageNet pre-trained)
        └── AdaptiveAvgPool2d (built-in)
        └── Dropout(0.4)
        └── Linear(1792, 512)
        └── SiLU activation
        └── Dropout(0.4)
        └── Linear(512, NUM_CLASSES)

    Returns
    -------
    nn.Module  –  model on CPU (move to device in calling code)
    """
    if _USE_NEW_API and pretrained:
        weights = EfficientNet_B4_Weights.IMAGENET1K_V1
        model = efficientnet_b4(weights=weights)
    else:
        model = efficientnet_b4(pretrained=pretrained)

    # EfficientNet-B4 classifier is:  Dropout → Linear(1792, 1000)
    in_features = model.classifier[1].in_features   # 1792

    model.classifier = nn.Sequential(
        nn.Dropout(p=DROPOUT_RATE),
        nn.Linear(in_features, 512),
        nn.SiLU(),
        nn.Dropout(p=DROPOUT_RATE),
        nn.Linear(512, NUM_CLASSES),
    )

    return model


def load_trained_model(weights_path: str, device: torch.device) -> nn.Module:
    """
    Load a previously saved RetinaGuard model checkpoint.

    Parameters
    ----------
    weights_path : str  –  path to the .pth checkpoint file
    device       : torch.device

    Returns
    -------
    nn.Module  –  model in eval mode on the given device
    """
    model = build_model(pretrained=False)
    checkpoint = torch.load(weights_path, map_location=device)

    # Support both raw state_dict and wrapped {"model_state": ...} saves
    if isinstance(checkpoint, dict) and "model_state" in checkpoint:
        model.load_state_dict(checkpoint["model_state"])
    else:
        model.load_state_dict(checkpoint)

    model.to(device)
    model.eval()
    return model


def get_device() -> torch.device:
    """Return CUDA device if available, else CPU."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")
