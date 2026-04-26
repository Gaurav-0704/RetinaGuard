#!/usr/bin/env python
# ============================================================
#  run.py — RetinaGuard Entry Point
#
#  Usage:
#    python run.py            (development)
#    python run.py --prod     (production mode)
# ============================================================

import os
import sys
import argparse

# Make sure the repo root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app
from backend.database import db


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prod", action="store_true", help="Run in production mode")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    env = "production" if args.prod else "development"
    app = create_app(env)

    # Create DB tables on first run
    with app.app_context():
        db.create_all()
        print("✓ Database ready.")

    print(f"\n{'='*50}")
    print(f"  RetinaGuard running at http://{args.host}:{args.port}")
    print(f"  Mode: {env}")
    print(f"{'='*50}\n")

    app.run(host=args.host, port=args.port, debug=(env == "development"))


if __name__ == "__main__":
    main()
