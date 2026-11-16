"""Central configuration for the portfolio QA suite."""
from __future__ import annotations

import os
from pathlib import Path

QA_DIR = Path(__file__).resolve().parent
REPO_ROOT = QA_DIR.parent

# Website under test. Override with BASE_URL=http://127.0.0.1:8000/ or BASE_URL=local
DEFAULT_BASE_URL = "https://giorginazar422-wq.github.io/giorgi-portfolio/"
BASE_URL = os.environ.get("BASE_URL", DEFAULT_BASE_URL)

BASELINE_DIR = QA_DIR / "baseline"
REPORTS_DIR = QA_DIR / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
DIFFS_DIR = REPORTS_DIR / "diffs"

# Viewports used by the visual regression tests.
VIEWPORTS = {
    "desktop": {"width": 1366, "height": 800},
    "tablet": {"width": 820, "height": 1180},
    "mobile": {"width": 390, "height": 844},
}

# Maximum share of changed pixels before a visual test is reported as a defect.
VISUAL_DIFF_THRESHOLD = 0.01  # 1 %
# Per-channel difference below which two pixels count as "the same" (anti-aliasing noise).
PIXEL_TOLERANCE = 24

# Pages that must answer with HTTP 200.
PAGES = {
    "home": "",
    "classic": "classic/",
    "mars": "mars/",
    "rover": "rover/",
}

CONTACT_EMAIL = "khuchuagiorgi@gmail.com"
GITHUB_PROFILE = "https://github.com/giorginazar422-wq"

# Chapters of the rover journey: nav data-to id -> label shown in #chapter.
CHAPTERS = {
    "p-about": "ABOUT ME",
    "p-skills": "TOOLKIT",
    "p-projects": "SELECTED WORK",
    "p-contact": "CONTACT",
}
