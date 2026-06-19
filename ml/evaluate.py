# ============================================================
#  ml/evaluate.py — RetinaGuard Held-Out Evaluation
#
#  Run AFTER training, on the held-out test split:
#      python -m ml.evaluate \
#          --images_dir path/to/images \
#          --csv_path   backend/weights/test_split.csv
#
#  Produces (in --out_dir, default: docs/results/):
#    • metrics.json          — every headline number, machine-readable
#    • report.md             — human-readable results table
#    • confusion_matrix.png  — raw counts
#    • confusion_matrix_normalized.png
#    • roc_curves.png        — one-vs-rest ROC for all 5 grades
#
#  All numbers come from real model predictions on images the model
#  never saw during training. Nothing here is fabricated.
# ============================================================

import argparse
import os
import json
import logging
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score, f1_score, precision_recall_fscore_support,
    cohen_kappa_score, confusion_matrix, roc_auc_score, roc_curve,
    classification_report,
)
from sklearn.preprocessing import label_binarize

from ml.config import BEST_MODEL_PATH, NUM_CLASSES, CLASS_NAMES
from ml.model import load_trained_model, get_device
from ml.preprocessing import get_val_transforms
from ml.train import RetinalDataset  # reuse the exact dataset loader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_LABELS = list(range(NUM_CLASSES))
_NAMES = [CLASS_NAMES[i] for i in _LABELS]


# ── Inference over the test set ──────────────────────────────
def _collect_predictions(model, loader, device):
    all_probs, all_labels = [], []
    model.eval()
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            logits = model(images)
            probs = F.softmax(logits, dim=1)
            all_probs.append(probs.cpu().numpy())
            all_labels.extend(labels.numpy().tolist())
    return np.concatenate(all_probs, axis=0), np.array(all_labels)


# ── Plot helpers ─────────────────────────────────────────────
def _plot_confusion(cm, out_path, normalize=False):
    data = cm.astype(float)
    if normalize:
        row_sums = data.sum(axis=1, keepdims=True)
        data = np.divide(data, row_sums, out=np.zeros_like(data), where=row_sums != 0)
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(data, cmap="Blues")
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=np.arange(NUM_CLASSES), yticks=np.arange(NUM_CLASSES),
           xticklabels=_NAMES, yticklabels=_NAMES,
           ylabel="True grade", xlabel="Predicted grade",
           title="Confusion Matrix" + (" (row-normalized)" if normalize else ""))
    plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
    thresh = data.max() / 2.0 if data.max() > 0 else 0.5
    for i in range(NUM_CLASSES):
        for j in range(NUM_CLASSES):
            val = data[i, j]
            txt = format(val, ".2f") if normalize else str(int(cm[i, j]))
            ax.text(j, i, txt, ha="center", va="center",
                    color="white" if val > thresh else "black", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _plot_roc(y_true_bin, probs, aucs, out_path):
    fig, ax = plt.subplots(figsize=(7, 6))
    for i in _LABELS:
        if y_true_bin[:, i].sum() == 0:
            continue
        fpr, tpr, _ = roc_curve(y_true_bin[:, i], probs[:, i])
        ax.plot(fpr, tpr, label=f"{_NAMES[i]} (AUC={aucs[i]:.3f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.4)
    ax.set(xlabel="False Positive Rate", ylabel="True Positive Rate",
           title="One-vs-Rest ROC Curves")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ── Main ─────────────────────────────────────────────────────
def evaluate(images_dir, csv_path, weights_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    device = get_device()
    logger.info("Device: %s", device)

    if not os.path.exists(weights_path):
        raise FileNotFoundError(
            f"No checkpoint at {weights_path}. Train first (python -m ml.train ...)."
        )

    df = pd.read_csv(csv_path)
    ds = RetinalDataset(df, images_dir, transform=get_val_transforms())
    loader = DataLoader(ds, batch_size=16, shuffle=False, num_workers=2, pin_memory=True)

    model = load_trained_model(weights_path, device)
    probs, y_true = _collect_predictions(model, loader, device)
    y_pred = probs.argmax(axis=1)

    # ── Headline metrics ──
    acc        = accuracy_score(y_true, y_pred)
    f1_macro   = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1_weight  = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    qwk        = cohen_kappa_score(y_true, y_pred, weights="quadratic")

    prec, rec, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=_LABELS, zero_division=0)

    # ── AUC (one-vs-rest) ──
    y_true_bin = label_binarize(y_true, classes=_LABELS)
    per_class_auc = {}
    for i in _LABELS:
        try:
            per_class_auc[i] = roc_auc_score(y_true_bin[:, i], probs[:, i]) \
                if y_true_bin[:, i].sum() > 0 else None
        except ValueError:
            per_class_auc[i] = None
    valid_aucs = [v for v in per_class_auc.values() if v is not None]
    try:
        macro_auc = roc_auc_score(y_true_bin, probs, average="macro", multi_class="ovr")
    except ValueError:
        macro_auc = float(np.mean(valid_aucs)) if valid_aucs else None

    cm = confusion_matrix(y_true, y_pred, labels=_LABELS)

    # ── Assemble metrics.json ──
    metrics = {
        "n_test_samples": int(len(y_true)),
        "checkpoint": os.path.basename(weights_path),
        "overall": {
            "accuracy": round(float(acc), 4),
            "f1_macro": round(float(f1_macro), 4),
            "f1_weighted": round(float(f1_weight), 4),
            "quadratic_weighted_kappa": round(float(qwk), 4),
            "macro_auc_ovr": round(float(macro_auc), 4) if macro_auc is not None else None,
        },
        "per_class": {
            CLASS_NAMES[i]: {
                "precision": round(float(prec[i]), 4),
                "recall": round(float(rec[i]), 4),
                "f1": round(float(f1[i]), 4),
                "auc_ovr": round(float(per_class_auc[i]), 4) if per_class_auc[i] is not None else None,
                "support": int(support[i]),
            } for i in _LABELS
        },
        "confusion_matrix": cm.tolist(),
        "confusion_matrix_labels": _NAMES,
    }

    with open(os.path.join(out_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    _plot_confusion(cm, os.path.join(out_dir, "confusion_matrix.png"), normalize=False)
    _plot_confusion(cm, os.path.join(out_dir, "confusion_matrix_normalized.png"), normalize=True)
    _plot_roc(y_true_bin, probs, per_class_auc, os.path.join(out_dir, "roc_curves.png"))

    _write_report(metrics, out_dir)

    logger.info("Done. Artifacts in %s", out_dir)
    logger.info("Accuracy=%.4f  QWK=%.4f  macroAUC=%s",
                acc, qwk, f"{macro_auc:.4f}" if macro_auc is not None else "n/a")
    print("\n" + classification_report(y_true, y_pred, labels=_LABELS,
                                        target_names=_NAMES, zero_division=0))
    return metrics


def _write_report(m, out_dir):
    o = m["overall"]
    lines = [
        "# RetinaGuard — Evaluation Results",
        "",
        f"Held-out test set: **{m['n_test_samples']} images** the model never saw "
        f"during training. Checkpoint: `{m['checkpoint']}`.",
        "",
        "## Headline metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Accuracy | {o['accuracy']:.4f} |",
        f"| Quadratic Weighted Kappa | {o['quadratic_weighted_kappa']:.4f} |",
        f"| Macro F1 | {o['f1_macro']:.4f} |",
        f"| Weighted F1 | {o['f1_weighted']:.4f} |",
        f"| Macro AUC (OvR) | {o['macro_auc_ovr']} |",
        "",
        "## Per-class performance",
        "",
        "| Grade | Precision | Recall | F1 | AUC | Support |",
        "|---|---|---|---|---|---|",
    ]
    for name, c in m["per_class"].items():
        lines.append(
            f"| {name} | {c['precision']:.3f} | {c['recall']:.3f} | "
            f"{c['f1']:.3f} | {c['auc_ovr']} | {c['support']} |"
        )
    lines += [
        "",
        "## Confusion matrix",
        "",
        "![Confusion matrix](confusion_matrix.png)",
        "",
        "![Confusion matrix (normalized)](confusion_matrix_normalized.png)",
        "",
        "## ROC curves (one-vs-rest)",
        "",
        "![ROC curves](roc_curves.png)",
        "",
    ]
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RetinaGuard on a held-out set")
    parser.add_argument("--images_dir", required=True)
    parser.add_argument("--csv_path", required=True,
                        help="CSV of held-out samples (id_code,diagnosis). "
                             "Use backend/weights/test_split.csv from training.")
    parser.add_argument("--weights_path", default=BEST_MODEL_PATH)
    parser.add_argument("--out_dir", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "docs", "results"))
    args = parser.parse_args()
    evaluate(args.images_dir, args.csv_path, args.weights_path, args.out_dir)
