# RetinaGuard

> **Diabetic Retinopathy Screening & Patient Management Platform**
>
> Copyright (c) 2024 **Gaurav Singh Thakur, Niharika Raghunandan** — All Rights Reserved.
> See [LICENSE](LICENSE) for usage restrictions.

---

## Overview

RetinaGuard is a full-stack web application for automated diabetic retinopathy (DR) severity screening, longitudinal patient monitoring, and doctor–patient clinical management. It provides a five-level DR grading system aligned with the International Clinical Diabetic Retinopathy Severity Scale, combined with a visual diagnostic focus map that highlights which retinal regions contributed to each assessment.

The platform is built as a two-sided portal: patients upload retinal images and track their eye health history, while clinicians gain a complete dashboard view of all patients, high-risk alerts, and inline annotation tools.

---

## Features

| Feature | Description |
|---|---|
| **5-Level DR Grading** | Classifies retinal images as No DR / Mild / Moderate / Severe / Proliferative |
| **Diagnostic Focus Map** | Visual heatmap overlay identifying the retinal regions driving each severity assessment |
| **Patient Portal** | Secure login, profile, scan upload, full history, clinical advice per result |
| **Doctor Portal** | Patient list, high-risk alerts, severity trend charts, inline notes per scan |
| **Longitudinal Tracking** | Severity trend charts across all visits for every patient |
| **Doctor–Patient Assignment** | Doctors are linked to specific patients; admins see all |
| **Screening Confidence** | Confidence percentage and per-grade probability distribution for each result |
| **Role-Based Access** | Three roles: `patient`, `doctor`, `admin` with separate views and permissions |
| **Simulation Mode** | Full app runs without trained weights — simulated results for demonstration |
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
| Region analysis | Gradient-weighted activation mapping |
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
│   │   ├── base.html            # Shared layout with sidebar navigation
│   │   ├── landing.html         # Public front page
│   │   ├── login.html           # Sign-in page
│   │   ├── register.html        # Registration page
│   │   ├── dashboard.html       # Patient dashboard
│   │   ├── scan.html            # New scan upload & live results
│   │   ├── result.html          # Individual scan report
│   │   ├── history.html         # Scan history grid with filters
│   │   ├── profile.html         # Patient profile form
│   │   ├── doctor_dashboard.html         # Doctor overview
│   │   ├── doctor_patients.html          # Doctor patient list
│   │   └── doctor_patient_detail.html    # Full patient clinical view
│   └── static/
│       ├── css/style.css        # Complete UI stylesheet
│       └── js/
│           ├── main.js          # Global JS (sidebar, alerts, animations)
│           ├── scan.js          # Scan upload, progress, live result display
│           └── charts.js        # Dashboard trend & distribution charts
│
├── uploads/                     # Uploaded retinal images (auto-created)
├── backend/weights/             # Trained model checkpoint (auto-created)
│   └── retinoguard_best.pth     # Place trained weights here
│
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

> **Note:** PyTorch installation may vary by platform. Visit [pytorch.org](https://pytorch.org/get-started/locally/) for the appropriate install command for your system.

### Step 3 — Initialise the database

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

### Step 4 — Run the application

```bash
python run.py
```

Open your browser at **http://127.0.0.1:5000**

---

## Training the Screening Engine

If you have a labelled dataset of retinal fundus images, you can train the screening engine using:

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

The best checkpoint is automatically saved to `backend/weights/retinoguard_best.pth`. Once this file exists, the application switches from Simulation Mode to live screening automatically on next restart.

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

When no trained model weights are found at `backend/weights/retinoguard_best.pth`, the application automatically enters **Simulation Mode**. In this mode:

- Results are generated deterministically from the image filename (reproducible per image).
- A yellow banner appears on all result pages indicating simulation.
- All other platform features (patient management, doctor portal, history, notes) work identically.

This allows full evaluation of the application without requiring a trained model.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `retinoguard-secret-change-in-production` | Flask session secret key |
| `DATABASE_URL` | SQLite in project root | SQLAlchemy connection string |

For production, always set a strong `SECRET_KEY`:

```bash
export SECRET_KEY="your-strong-random-secret"
python run.py --prod
```

---

## Medical Disclaimer

> RetinaGuard is a screening aid developed for educational and portfolio purposes.
> It is **not** a certified medical device and **must not** be used as a substitute
> for professional ophthalmic examination and diagnosis.
> All results must be reviewed and confirmed by a qualified healthcare professional.
> The authors accept no liability for clinical decisions based on this software.

---

## License & Copyright

This software is proprietary. Viewing is permitted; copying, distribution, modification, and commercial use are **strictly prohibited** without explicit written permission from both authors.

See [LICENSE](LICENSE) for the full terms.

---

## Authors

RetinaGuard is built on a diabetic retinopathy detection system originally developed jointly by both authors during their undergraduate research. This platform extends that shared academic foundation into a full-stack clinical screening application.

**Gaurav Singh Thakur**
GitHub: [https://github.com/Gaurav-0704](https://github.com/Gaurav-0704)

---

*Copyright (c) 2024 Gaurav Singh Thakur, Niharika Raghunandan. All Rights Reserved.*
