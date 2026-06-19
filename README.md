# RetinaGuard

> **Diabetic Retinopathy Screening & Patient Management Platform**
>
> Copyright (c) 2024 **Gaurav Singh Thakur, Niharika Raghunandan** — All Rights Reserved.
> See [LICENSE](LICENSE) for usage restrictions.

---

> ### ⚠️ Demo / Portfolio Project — No Trained Weights Included
>
> I built RetinaGuard as a full-stack portfolio project demonstrating clinical-grade UI,
> role-based access control, and a production-ready PyTorch inference pipeline.
> **No trained model weights ship with this repository.** The app runs in
> Simulation Mode by default, generating deterministic placeholder results from image
> filenames. All screening output shown in demos is simulated — it carries no
> diagnostic validity and should not be interpreted as clinical output.
> **To produce real weights + verifiable metrics**, run
> [`notebooks/train_retinaguard_colab.ipynb`](notebooks/train_retinaguard_colab.ipynb)
> (free Colab T4, APTOS 2019, ~30-60 min). It trains, evaluates on a held-out
> test split, and emits accuracy, per-class precision/recall/F1, one-vs-rest AUC,
> quadratic weighted kappa, a confusion matrix and ROC curves into `docs/results/`.
> Drop the resulting checkpoint at `backend/weights/retinoguard_best.pth` and the
> app switches from Simulation Mode to real inference automatically.

---

<!-- ========================================================================
     AFTER you complete a training run, DELETE the Simulation-Mode warning
     block above and UNCOMMENT the section below, pasting in the real numbers
     from docs/results/report.md. Do NOT fill these in by hand from memory.
     ------------------------------------------------------------------------
## Model Results (APTOS 2019, held-out test split)

| Metric | Value |
|---|---|
| Accuracy | 0.xxxx |
| Quadratic Weighted Kappa | 0.xxxx |
| Macro AUC (OvR) | 0.xxxx |

Full per-class table, confusion matrix and ROC curves: see
[docs/RESULTS.md](docs/RESULTS.md).

---
======================================================================== -->


## Overview

I built RetinaGuard as a two-sided clinical web platform for automated diabetic
retinopathy (DR) severity screening, longitudinal patient monitoring, and
doctor–patient management. Patients upload retinal fundus images and track their
eye health history; clinicians get a complete dashboard with high-risk alerts,
severity trends across visits, and inline annotation tools. The five-level DR
grading follows the International Clinical Diabetic Retinopathy Severity Scale.

The screening engine is an EfficientNet-B4 with Grad-CAM diagnostic focus mapping —
when real weights are loaded it produces a colour overlay that highlights which
retinal regions drove each severity grade, which I designed for clinical
explainability rather than pure accuracy.

---

## Features

| Feature | Description |
|---|---|
| **5-Level DR Grading** | Classifies retinal images as No DR / Mild / Moderate / Severe / Proliferative |
| **Diagnostic Focus Map** | Grad-CAM heatmap overlay identifying which retinal regions drive each severity grade |
| **Patient Portal** | Secure login, profile, scan upload, full history, clinical advice per result |
| **Doctor Portal** | Patient list, high-risk alerts, severity trend charts, inline notes per scan |
| **Longitudinal Tracking** | Severity trend charts across all visits for every patient |
| **Doctor–Patient Assignment** | Doctors are linked to specific patients; admins see all |
| **Screening Confidence** | Confidence percentage and per-grade probability distribution for each result |
| **Role-Based Access** | Three roles: `patient`, `doctor`, `admin` with separate views and permissions |
| **Simulation Mode** | Full app runs without trained weights — placeholder results for demonstration |
| **Public Landing Page** | Marketing-grade front page with feature overview and grading reference |

---

## Technology Stack

### Backend
| Component | Technology |
|---|---|
| Web framework | Flask 3.0 |
| Database ORM | Flask-SQLAlchemy + SQLite |
| Authentication | Flask-Login + Werkzeug password hashing |
| Image serving | Flask static/upload routes |

### Screening Engine (`ml/`)
| Component | Technology |
|---|---|
| Framework | PyTorch |
| Architecture | EfficientNet-B4 (transfer learning) |
| Preprocessing | CLAHE contrast enhancement + augmentation pipeline |
| Region analysis | Gradient-weighted class activation mapping (Grad-CAM) |
| Training | AdamW + CosineAnnealingLR + early stopping |

### Frontend
| Component | Technology |
|---|---|
| UI framework | Bootstrap 5.3 |
| Icons | Bootstrap Icons 1.11 |
| Charts | Chart.js 4.4 |
| Fonts | Inter (Google Fonts) |

---

## Project Structure

```
RetinaGuard/
│
├── ml/                          # Screening engine
│   ├── config.py                # All hyperparameters and class definitions
│   ├── model.py                 # EfficientNet-B4 architecture & loader
│   ├── preprocessing.py         # CLAHE + train/val transform pipelines
│   ├── predict.py               # Inference engine + diagnostic focus mapping
│   └── train.py                 # Full training script with early stopping
│
├── backend/                     # Flask application
│   ├── app.py                   # Application factory (blueprint registration)
│   ├── config.py                # Flask config classes (dev / prod)
│   ├── database.py              # SQLAlchemy + LoginManager instances
│   ├── models/
│   │   ├── user.py              # Patient/Doctor/Admin user model
│   │   └── scan.py              # Scan result & report model
│   └── routes/
│       ├── auth.py              # Login, register, logout, landing page
│       ├── patients.py          # Patient profile view & edit
│       ├── scans.py             # Upload, inference, history, delete
│       ├── dashboard.py         # Patient dashboard stats & trend API
│       └── doctor.py            # Doctor portal — patient list, detail, notes
│
├── frontend/
│   ├── templates/               # Jinja2 HTML templates
│   └── static/
│       ├── css/style.css
│       └── js/
│           ├── main.js
│           ├── scan.js
│           └── charts.js
│
├── tests/                       # Pytest suite
│   ├── conftest.py              # App + DB fixtures
│   ├── test_auth.py             # Login, register, logout routes
│   ├── test_scans.py            # Upload, result, history, delete, notes
│   └── test_predict.py          # Inference wrapper — demo mode & dispatch
│
├── uploads/                     # Runtime-created; gitignored
├── backend/weights/             # Runtime-created; gitignored
│   └── retinoguard_best.pth     # Place your trained checkpoint here
│
├── .env.example                 # Template for environment variables
├── run.py                       # Application entry point
├── setup_db.py                  # Database initialisation & demo seed
├── requirements.txt             # Python dependencies
├── LICENSE                      # Proprietary license — read before use
└── COPYRIGHT                    # Copyright notice & third-party attributions
```

---

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip
- (Optional) CUDA-compatible GPU for faster screening

### Step 1 — Clone the repository

```bash
git clone https://github.com/Gaurav-0704/retinoguard.git
cd retinoguard/RetinaGuard
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** PyTorch installation may vary by platform.
> Visit [pytorch.org](https://pytorch.org/get-started/locally/) for the right command for your system.

### Step 3 — Set environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

At minimum, set `SECRET_KEY` before running in any shared environment:

```bash
# generate a strong key
python -c "import secrets; print(secrets.token_hex(32))"
```

If `SECRET_KEY` is not set, the app generates an ephemeral key at startup
(sessions won't survive restarts — fine for local dev, not for deployment).

### Step 4 — Initialise the database

```bash
# Bare initialisation
python setup_db.py

# With demo accounts (recommended for first run)
python setup_db.py --demo
```

Demo accounts created with `--demo`:

| Role | Email | Password |
|---|---|---|
| Patient | demo@retinoguard.com | demo1234 |
| Doctor | admin@retinoguard.com | admin1234 |

### Step 5 — Run the application

```bash
python run.py
```

Open your browser at **http://127.0.0.1:5000**

---

## Running the Tests

```bash
pip install pytest
pytest tests/ -v
```

I wrote the test suite against an in-memory SQLite database with mocked inference,
so tests pass without a GPU, trained weights, or any uploaded images.

---

## Training the Screening Engine

If you have a labelled dataset of retinal fundus images (I trained against the
APTOS 2019 / EyePACS format), you can train the screening engine:

```bash
python -m ml.train \
  --images_dir path/to/images \
  --csv_path   path/to/labels.csv
```

**CSV format:**

```
id_code,diagnosis
abc123,0
def456,2
...
```

Where `diagnosis` is an integer 0–4 corresponding to the DR severity grade.

The best checkpoint is automatically saved to `backend/weights/retinoguard_best.pth`.
Once this file exists, the app switches from Simulation Mode to live screening
automatically on next restart.

### Training Configuration

All hyperparameters are centralised in `ml/config.py`:

```python
MODEL_NAME           = "efficientnet_b4"
NUM_CLASSES          = 5
IMAGE_SIZE           = 512
BATCH_SIZE           = 16
NUM_EPOCHS           = 60
LEARNING_RATE        = 1e-4
EARLY_STOP_PATIENCE  = 12
```

---

## DR Severity Grading Scale

| Grade | Name | Clinical Description |
|---|---|---|
| **0** | No DR | No visible signs of diabetic retinopathy. Annual screening recommended. |
| **1** | Mild DR | Microaneurysms only. Monitor closely; revisit in 9–12 months. |
| **2** | Moderate DR | More than microaneurysms but less than Severe. Ophthalmologist referral; revisit in 6 months. |
| **3** | Severe DR | Extensive haemorrhages, venous beading. Urgent specialist referral required. |
| **4** | Proliferative DR | Neovascularisation present. Immediate ophthalmic intervention needed. |

---

## Simulation Mode

When no trained weights are present at `backend/weights/retinoguard_best.pth`, the
app runs in **Simulation Mode**. In this mode:

- Results are generated deterministically from the image filename (same file → same result every time).
- A yellow banner appears on all result pages flagging the simulation.
- Every other platform feature — patient management, doctor portal, history, notes —
  works identically to the real-model path.

I included Simulation Mode so reviewers can evaluate the full application
without needing a trained checkpoint or a GPU.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | ephemeral (logged warning) | Flask session secret — **must** be set for any shared deployment |
| `DATABASE_URL` | SQLite in project root | SQLAlchemy connection string |

See `.env.example` for a template.

---

## Medical Disclaimer

> RetinaGuard is a screening aid developed for educational and portfolio purposes.
> It is **not** a certified medical device and **must not** be used as a substitute
> for professional ophthalmic examination and diagnosis.
> All results must be reviewed and confirmed by a qualified healthcare professional.
> The authors accept no liability for clinical decisions based on this software.

---

## License & Copyright

This software is proprietary. Viewing is permitted; copying, distribution, modification,
and commercial use are **strictly prohibited** without explicit written permission
from both authors. See [LICENSE](LICENSE) for the full terms.

---

## Authors

I built RetinaGuard as an extension of a diabetic retinopathy detection system Niharika
and I developed together during our undergraduate research. This platform takes that
shared academic foundation and extends it into a full-stack clinical screening application.

| | Name | Role |
|---|---|---|
| 🔬 | **Gaurav Singh Thakur** | Co-author · Full-stack development, screening engine, platform architecture |
| 🔬 | **Niharika Raghunandan** | Co-author · Original DR research, academic foundation, clinical knowledge |

**Gaurav Singh Thakur**
GitHub: [https://github.com/Gaurav-0704](https://github.com/Gaurav-0704)

---

*Copyright (c) 2024 Gaurav Singh Thakur, Niharika Raghunandan. All Rights Reserved.*
