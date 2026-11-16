"""Visual regression: screenshots of key states are compared with stored baselines.

The first run (or ``--update-baselines``) stores the screenshots in ``qa/baseline``.
Later runs report a defect when more than ``config.VISUAL_DIFF_THRESHOLD`` of the pixels changed
and save a baseline | current | diff image under ``qa/reports/diffs``.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import Callable

import pytest
from playwright.sync_api import Page, expect

import config
from reporting.visual import compare_images

pytestmark = pytest.mark.visual

# Freeze everything that moves so that screenshots are repeatable.
FREEZE_CSS = """
*, *::before, *::after { animation: none !important; transition: none !important; caret-color: transparent !important; }
#v, #bg { visibility: hidden !important; }
"""


def _home_ready(page: Page, base_url: str) -> None:
    page.goto(base_url, wait_until="load")
    page.wait_for_function("() => !document.getElementById('hint').textContent.startsWith('Preparing')", timeout=20_000)


def landing(page: Page, base_url: str) -> None:
    _home_ready(page, base_url)


def contact_room(page: Page, base_url: str) -> None:
    _home_ready(page, base_url)
    page.locator("#navigation a[data-to='p-contact']").click()
    expect(page.locator("#p-contact")).to_be_visible()
    page.wait_for_timeout(1200)


def skills_room(page: Page, base_url: str) -> None:
    _home_ready(page, base_url)
    page.locator("#navigation a[data-to='p-skills']").click()
    expect(page.locator("#p-skills")).to_be_visible()
    page.wait_for_timeout(1200)


def portfolio_dialog(page: Page, base_url: str) -> None:
    _home_ready(page, base_url)
    page.locator("#read").click()
    expect(page.locator("#dossier")).to_be_visible()


def classic_page(page: Page, base_url: str) -> None:
    page.goto(base_url + "classic/", wait_until="load")


def mars_page(page: Page, base_url: str) -> None:
    page.goto(base_url + "mars/", wait_until="load")
    page.wait_for_timeout(800)


@dataclass(frozen=True)
class Scenario:
    name: str
    prepare: Callable[[Page, str], None]
    viewports: tuple[str, ...] = ("desktop", "mobile")
    full_page: bool = False


SCENARIOS = [
    Scenario("home-landing", landing, ("desktop", "tablet", "mobile")),
    Scenario("home-skills", skills_room),
    Scenario("home-contact", contact_room),
    Scenario("home-dialog", portfolio_dialog),
    Scenario("classic", classic_page, ("desktop", "mobile"), full_page=True),
    Scenario("mars", mars_page, ("desktop",)),
]

CASES = [(s, vp) for s in SCENARIOS for vp in s.viewports]


def _stabilize(page: Page) -> None:
    page.add_style_tag(content=FREEZE_CSS)
    page.evaluate("document.fonts && document.fonts.ready")
    page.wait_for_timeout(400)


@pytest.mark.parametrize("scenario,viewport", CASES, indirect=["viewport"],
                         ids=[f"{s.name}-{vp}" for s, vp in CASES])
def test_visual_matches_baseline(page: Page, base_url: str, scenario: Scenario, viewport: dict,
                                 pytestconfig, request, notes):
    scenario.prepare(page, base_url)
    _stabilize(page)

    vp_name = next(k for k, v in config.VIEWPORTS.items() if v == viewport)
    key = f"{scenario.name}-{vp_name}"
    current = config.SCREENSHOTS_DIR / f"{key}.png"
    baseline = config.BASELINE_DIR / f"{key}.png"
    page.screenshot(path=current, full_page=scenario.full_page)

    if pytestconfig.getoption("--update-baselines") or not baseline.exists():
        baseline.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(current, baseline)
        notes.append("baseline created" if not pytestconfig.getoption("--update-baselines") else "baseline updated")
        request.node._screenshots.append(str(current.relative_to(config.REPORTS_DIR)))
        return

    diff = compare_images(baseline, current, config.DIFFS_DIR / f"{key}-diff.png", config.PIXEL_TOLERANCE)
    notes.append(f"{diff.changed_ratio:.2%} of pixels changed (limit {config.VISUAL_DIFF_THRESHOLD:.0%})")
    if diff.changed_ratio > config.VISUAL_DIFF_THRESHOLD or diff.size_mismatch:
        request.node._screenshots.append(str(diff.diff_path.relative_to(config.REPORTS_DIR)))
    assert not diff.size_mismatch, f"Screenshot size changed for {key} (page layout height/width differs from baseline)"
    assert diff.changed_ratio <= config.VISUAL_DIFF_THRESHOLD, (
        f"Visual difference for {key}: {diff.changed_ratio:.2%} of pixels changed "
        f"({diff.changed_pixels}/{diff.total_pixels}); see diff image")
