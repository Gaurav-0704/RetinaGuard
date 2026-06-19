# RetinaGuard — Model Results

> **Status:** _PLACEHOLDER — fill after your training run._
> Run `notebooks/train_retinaguard_colab.ipynb`, then replace the bracketed
> values below with the numbers from `docs/results/metrics.json` (the evaluation
> script also writes a ready-made `docs/results/report.md` you can paste in).
> **Do not invent numbers here.** Every value must come from a real evaluation
> on the held-out test split.

## Methodology

- **Dataset:** APTOS 2019 Blindness Detection (Kaggle), ~3,662 labeled fundus
  images, 5 DR grades (0 = No DR … 4 = Proliferative DR).
- **Split:** stratified train / validation / **held-out test**. The test set is
  separated before training and never seen by the model. Split is reproducible
  (`SEED = 42`) and saved to `backend/weights/test_split.csv`.
- **Model:** EfficientNet-B4 (ImageNet-pretrained) with a custom 2-layer head,
  dropout 0.4.
- **Training:** AdamW + CosineAnnealingLR, class-balanced WeightedRandomSampler,
  CLAHE + augmentation. Best checkpoint selected by **validation quadratic
  weighted kappa** (the official DR-grading metric), with early stopping.
- **Evaluation:** all metrics below computed on the held-out test split via
  `python -m ml.evaluate`.

## Headline metrics

| Metric | Value |
|---|---|
| Test samples | _[n]_ |
| Accuracy | _[0.xxxx]_ |
| Quadratic Weighted Kappa | _[0.xxxx]_ |
| Macro F1 | _[0.xxxx]_ |
| Weighted F1 | _[0.xxxx]_ |
| Macro AUC (one-vs-rest) | _[0.xxxx]_ |

## Per-class performance

| Grade | Precision | Recall | F1 | AUC | Support |
|---|---|---|---|---|---|
| No DR | _[ ]_ | _[ ]_ | _[ ]_ | _[ ]_ | _[ ]_ |
| Mild DR | _[ ]_ | _[ ]_ | _[ ]_ | _[ ]_ | _[ ]_ |
| Moderate DR | _[ ]_ | _[ ]_ | _[ ]_ | _[ ]_ | _[ ]_ |
| Severe DR | _[ ]_ | _[ ]_ | _[ ]_ | _[ ]_ | _[ ]_ |
| Proliferative DR | _[ ]_ | _[ ]_ | _[ ]_ | _[ ]_ | _[ ]_ |

## Confusion matrix

![Confusion matrix](results/confusion_matrix.png)

![Confusion matrix (normalized)](results/confusion_matrix_normalized.png)

## ROC curves (one-vs-rest)

![ROC curves](results/roc_curves.png)

## Honest notes

- Minority grades (Severe, Proliferative) are under-represented in APTOS, so
  their recall is typically lower and their per-class metrics noisier — report
  them honestly rather than hiding them.
- These results are on the APTOS test split only. Cross-dataset generalization
  (e.g. to EyePACS) is **not** claimed unless separately evaluated.
- For a portfolio/demo context, a single-model APTOS result in the
  QWK 0.88-0.91 / accuracy ~0.82-0.85 range is strong and defensible.
