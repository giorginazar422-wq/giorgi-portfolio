"""Collects test outcomes during a pytest session and renders the final report."""
from __future__ import annotations

import json
import platform
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

from reporting.html_report import render_html


@dataclass
class TestResult:
    nodeid: str
    name: str
    module: str
    category: str            # functional / visual / a11y
    outcome: str             # passed / failed / skipped
    duration: float
    message: str = ""
    notes: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)   # paths relative to the reports dir
    console_errors: list[str] = field(default_factory=list)
    failed_requests: list[str] = field(default_factory=list)


class ReportCollector:
    def __init__(self, base_url: str, reports_dir: Path):
        self.base_url = base_url
        self.reports_dir = reports_dir
        self.results: list[TestResult] = []
        self.started = time.time()

    def add(self, result: TestResult) -> None:
        self.results.append(result)

    # --- summary helpers -------------------------------------------------
    def counts(self) -> dict[str, int]:
        c = {"passed": 0, "failed": 0, "skipped": 0}
        for r in self.results:
            c[r.outcome] = c.get(r.outcome, 0) + 1
        return c

    def defects(self) -> list[TestResult]:
        return [r for r in self.results if r.outcome == "failed"]

    def to_dict(self) -> dict:
        counts = self.counts()
        return {
            "site": self.base_url,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "duration_seconds": round(time.time() - self.started, 1),
            "platform": f"{platform.system()} {platform.release()} / Python {platform.python_version()}",
            "summary": {**counts, "total": len(self.results)},
            "status": "DEFECTS FOUND" if counts["failed"] else "OK",
            "results": [asdict(r) for r in self.results],
        }

    def write(self) -> tuple[Path, Path]:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        data = self.to_dict()
        json_path = self.reports_dir / "report.json"
        html_path = self.reports_dir / "report.html"
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        html_path.write_text(render_html(data), encoding="utf-8")
        return html_path, json_path
