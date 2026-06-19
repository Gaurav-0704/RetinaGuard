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
#  Pipeline:
#  ✓ EfficientNet-B4 backbone (ImageNet pre-trained)
#  ✓ AdamW + CosineAnnealingLR
#  ✓ Early stopping on val QWK (the DR competition metric)
#  ✓ Stratified train / val / TEST split — the test split is held
#    out entirely and never seen during training, so evaluate.py
#    reports honest, unbiased metrics.
#  ✓ Best checkpoint auto-saved
#  ✓ Class-balanced WeightedRandomSampler
#  ✓ Reproducible seed
#  ✓ history.json + test_split.csv written next to the checkpoint
# ============================================================

import argparse
import os
import json
import random
import logging
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from sklearn.model_selection import train_test_split
from sklearn.metrics import cohen_kappa_score
from PIL import Image

from ml.config import (
    BATCH_SIZE, NUM_EPOCHS, LEARNING_RATE, WEIGHT_DECAY,
    EARLY_STOP_PATIENCE, SEED, TRAIN_SPLIT,
    BEST_MODEL_PATH, NUM_CLASSES, CLASS_NAMES,
)
from ml.model import build_model, get_device
from ml.preprocessing import get_train_transforms, get_val_transforms

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Derived paths (siblings of the checkpoint)
_WEIGHTS_DIR     = os.path.dirname(BEST_MODEL_PATH)
HISTORY_PATH     = os.path.join(_WEIGHTS_DIR, "history.json")
TEST_SPLIT_PATH  = os.path.join(_WEIGHTS_DIR, "test_split.csv")


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
        path = None
        for ext in [".png", ".jpg", ".jpeg", ""]:
            cand = os.path.join(self.images_dir, str(row["id_code"]) + ext)
            if os.path.exists(cand):
                path = cand
                break
        if path is None:
            raise FileNotFoundError(
                f"No image for id_code={row['id_code']} in {self.images_dir}"
            )
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, int(row["diagnosis"])


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
    all_preds, all_labels = [], []

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
            all_preds.extend(preds.cpu().numpy().tolist())
            all_labels.extend(labels.cpu().numpy().tolist())

    qwk = cohen_kappa_score(all_labels, all_preds, weights="quadratic") if total else 0.0
    return total_loss / total, correct / total, qwk


# ── Main training loop ────────────────────────────────────────
def train(images_dir: str, csv_path: str):
    set_seed()
    device = get_device()
    logger.info("Device: %s", device)

    df = pd.read_csv(csv_path)
    if not {"id_code", "diagnosis"}.issubset(df.columns):
        raise ValueError("CSV must contain columns: id_code, diagnosis")

    # Stratified 3-way split:  train / val / test.
    # First peel off the held-out TEST set (never used in training),
    # then split the remainder into train / val.
    test_frac = (1 - TRAIN_SPLIT) / 2          # e.g. 0.10 test
    val_frac  = (1 - TRAIN_SPLIT) / 2          # e.g. 0.10 val
    trainval_df, test_df = train_test_split(
        df, test_size=test_frac, stratify=df["diagnosis"], random_state=SEED
    )
    val_relative = val_frac / (1 - test_frac)
    train_df, val_df = train_test_split(
        trainval_df, test_size=val_relative,
        stratify=trainval_df["diagnosis"], random_state=SEED,
    )

    os.makedirs(_WEIGHTS_DIR, exist_ok=True)
    test_df.to_csv(TEST_SPLIT_PATH, index=False)
    logger.info("Train: %d | Val: %d | Test (held out): %d",
                len(train_df), len(val_df), len(test_df))
    logger.info("Held-out test split saved -> %s", TEST_SPLIT_PATH)

    train_ds = RetinalDataset(train_df, images_dir, transform=get_train_transforms())
    val_ds   = RetinalDataset(val_df,   images_dir, transform=get_val_transforms())

    sampler      = make_sampler(train_df["diagnosis"].values)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, sampler=sampler, num_workers=2, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,   num_workers=2, pin_memory=True)

    model = build_model(pretrained=True).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS)

    best_val_qwk = -1.0
    epochs_no_improve = 0
    history = []

    for epoch in range(1, NUM_EPOCHS + 1):
        tr_loss, tr_acc, tr_qwk = run_epoch(model, train_loader, criterion, optimizer, device, train=True)
        vl_loss, vl_acc, vl_qwk = run_epoch(model, val_loader,   criterion, optimizer, device, train=False)
        scheduler.step()

        history.append({"epoch": epoch,
                        "tr_loss": tr_loss, "tr_acc": tr_acc, "tr_qwk": tr_qwk,
                        "vl_loss": vl_loss, "vl_acc": vl_acc, "vl_qwk": vl_qwk,
                        "lr": optimizer.param_groups[0]["lr"]})
        logger.info(
            "Epoch %3d/%d | Train Loss %.4f Acc %.4f QWK %.4f | Val Loss %.4f Acc %.4f QWK %.4f",
            epoch, NUM_EPOCHS, tr_loss, tr_acc, tr_qwk, vl_loss, vl_acc, vl_qwk,
        )

        # Select the best model by validation QWK (DR competition metric).
        if vl_qwk > best_val_qwk:
            best_val_qwk = vl_qwk
            epochs_no_improve = 0
            torch.save({"model_state": model.state_dict(), "epoch": epoch,
                        "val_loss": vl_loss, "val_acc": vl_acc, "val_qwk": vl_qwk,
                        "class_names": CLASS_NAMES}, BEST_MODEL_PATH)
            logger.info("  ✓ Best model saved (val_qwk=%.4f)", vl_qwk)
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= EARLY_STOP_PATIENCE:
                logger.info("Early stopping at epoch %d.", epoch)
                break

    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)
    logger.info("History saved -> %s", HISTORY_PATH)
    logger.info("Training complete. Best val_qwk=%.4f", best_val_qwk)
    logger.info("Next: python -m ml.evaluate --images_dir %s --csv_path %s",
                images_dir, TEST_SPLIT_PATH)
    return history


# ── CLI entry point ───────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train RetinaGuard")
    parser.add_argument("--images_dir", required=True)
    parser.add_argument("--csv_path",   required=True)
    args = parser.parse_args()
    train(args.images_dir, args.csv_path)
