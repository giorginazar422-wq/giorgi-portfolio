#!/usr/bin/env python3
"""One-command entry point: runs the whole suite and prints where the report is.

Examples
  python run.py                      # test the live site
  python run.py --local              # serve this repository and test it
  python run.py --update-baselines   # refresh the visual baselines
  python run.py -k visual            # only the visual tests
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

QA_DIR = Path(__file__).resolve().parent


def main(argv: list[str]) -> int:
    args = [sys.executable, "-m", "pytest", "-q", "--color=yes"]
    if "--local" in argv:
        argv = [a for a in argv if a != "--local"] + ["--site", "local"]
    args += argv
    print("Running:", " ".join(args))
    code = subprocess.call(args, cwd=QA_DIR)
    report = QA_DIR / "reports" / "report.html"
    if report.exists():
        print(f"\nReport: {report}")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
