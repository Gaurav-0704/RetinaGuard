# ============================================================
#  ml/train.py — RetinaGuard Training Script
#
#  Run from the RetinaGuard root folder:
#      python -m ml.train --images_dir path/to/images \
#                         --csv_path   path/to/labels.csv
#
#  CSV format:  id_code,diagnosis
#  Images:      <images_dir>/<id_code>.png  (or .jpg)
#
#  Upgrades vs original:
#  ✓ EfficientNet-B4 backbone
#  ✓ AdamW + CosineAnnealingLR
#  ✓ Early stopping
#  ✓ Best checkpoint auto-saved
#  ✓ Rich augmentation (CLAHE + flips + rotation + colour jitter)
#  ✓ Proper class-balanced WeightedRandomSampler
#  ✓ Reproducible seed
# ============================================================

import argparse
import os
import random
import logging
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from sklearn.model_selection import train_test_split
from sklearn.metrics import cohen_kappa_score, classification_report
from PIL import Image

from ml.config import (
    BATCH_SIZE, NUM_EPOCHS, LEARNING_RATE, WEIGHT_DECAY,
    LR_PATIENCE, EARLY_STOP_PATIENCE, SEED, TRAIN_SPLIT,
    BEST_MODEL_PATH, NUM_CLASSES, CLASS_NAMES,
)
from ml.model import build_model, get_device
from ml.preprocessing import get_train_transforms, get_val_transforms

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# ── Reproducibility ──────────────────────────────────────────
def set_seed(seed: int = SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ── Dataset ──────────────────────────────────────────────────
class RetinalDataset(Dataset):
    def __init__(self, df: pd.DataFrame, images_dir: str, transform=None):
        self.df = df.reset_index(drop=True)
        self.images_dir = images_dir
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        # Try common extensions
        for ext in [".png", ".jpg", ".jpeg", ""]:
            path = os.path.join(self.images_dir, str(row["id_code"]) + ext)
            if os.path.exists(path):
                break
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        label = int(row["diagnosis"])
        return img, label


# ── Training utilities ────────────────────────────────────────
def make_sampler(labels):
    """WeightedRandomSampler to handle class imbalance."""
    class_counts = np.bincount(labels, minlength=NUM_CLASSES).astype(float)
    class_weights = 1.0 / np.where(class_counts > 0, class_counts, 1)
    sample_weights = class_weights[labels]
    return WeightedRandomSampler(
        weights=torch.DoubleTensor(sample_weights),
        num_samples=len(sample_weights),
        replacement=True,
    )


def run_epoch(model, loader, criterion, optimizer, device, train: bool):
    model.train() if train else model.eval()
    total_loss, correct, total = 0.0, 0, 0

    ctx = torch.enable_grad() if train else torch.no_grad()
    with ctx:
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            if train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += images.size(0)

    return total_loss / total, correct / total


# ── Main training loop ────────────────────────────────────────
def train(images_dir: str, csv_path: str):
    set_seed()
    device = get_device()
    logger.info("Device: %s", device)

    # Load labels
    df = pd.read_csv(csv_path)
    train_df, val_df = train_test_split(
        df, test_size=1 - TRAIN_SPLIT, stratify=df["diagnosis"], random_state=SEED
    )
    logger.info("Train: %d | Val: %d", len(train_df), len(val_df))

    train_ds = RetinalDataset(train_df, images_dir, transform=get_train_transforms())
    val_ds   = RetinalDataset(val_df,   images_dir, transform=get_val_transforms())

    sampler    = make_sampler(train_df["diagnosis"].values)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, sampler=sampler,  num_workers=2, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,    num_workers=2, pin_memory=True)

    model = build_model(pretrained=True).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS)

    os.makedirs(os.path.dirname(BEST_MODEL_PATH), exist_ok=True)
    best_val_loss = float("inf")
    epochs_no_improve = 0
    history = []

    for epoch in range(1, NUM_EPOCHS + 1):
        tr_loss, tr_acc = run_epoch(model, train_loader, criterion, optimizer, device, train=True)
        vl_loss, vl_acc = run_epoch(model, val_loader,   criterion, optimizer, device, train=False)
        scheduler.step()

        history.append({"epoch": epoch, "tr_loss": tr_loss, "tr_acc": tr_acc,
                         "vl_loss": vl_loss, "vl_acc": vl_acc})
        logger.info(
            "Epoch %3d/%d | Train Loss %.4f Acc %.4f | Val Loss %.4f Acc %.4f",
            epoch, NUM_EPOCHS, tr_loss, tr_acc, vl_loss, vl_acc,
        )

        if vl_loss < best_val_loss:
            best_val_loss = vl_loss
            epochs_no_improve = 0
            torch.save({"model_state": model.state_dict(), "epoch": epoch,
                        "val_loss": vl_loss, "val_acc": vl_acc}, BEST_MODEL_PATH)
            logger.info("  ✓ Best model saved (val_loss=%.4f)", vl_loss)
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= EARLY_STOP_PATIENCE:
                logger.info("Early stopping at epoch %d.", epoch)
                break

    logger.info("Training complete. Best val_loss=%.4f", best_val_loss)
    return history


# ── CLI entry point ───────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train RetinaGuard")
    parser.add_argument("--images_dir", required=True)
    parser.add_argument("--csv_path",   required=True)
    args = parser.parse_args()
    train(args.images_dir, args.csv_path)
