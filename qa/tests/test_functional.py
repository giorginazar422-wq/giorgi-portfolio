"""Functional checks of the rover journey page (index.html) and the supporting pages."""
from __future__ import annotations

import json

import pytest
from playwright.sync_api import Page, expect

import config

pytestmark = pytest.mark.functional


# --------------------------------------------------------------------------- loading
def test_home_page_loads(page: Page, base_url: str, notes):
    response = page.goto(base_url, wait_until="load")
    assert response is not None and response.status == 200, f"Home page answered {response and response.status}"
    expect(page).to_have_title("Giorgi Khuchua — Creative Web Developer")
    assert page.get_attribute("html", "lang") == "en"
    expect(page.locator("#hero")).to_be_visible()
    notes.append(f"title: {page.title()}")


def test_journey_video_becomes_ready(home: Page, notes):
    hint = home.locator("#hint")
    expect(hint).not_to_contain_text("Preparing", timeout=20_000)
    text = hint.inner_text()
    assert "unavailable" not in text.lower(), f"Video failed to load: hint says '{text}'"
    duration = home.evaluate("document.getElementById('v').duration")
    assert duration and duration > 10, f"Unexpected video duration: {duration}"
    notes.append(f"video duration {duration:.1f}s")


def test_no_console_errors_or_broken_resources(home: Page, request):
    home.wait_for_timeout(1500)
    log = request.node._page_log
    assert not log.console_errors, "Console errors:\n" + "\n".join(log.console_errors)
    assert not log.failed_requests, "Broken resources:\n" + "\n".join(log.failed_requests)


@pytest.mark.parametrize("path", list(config.PAGES.values()), ids=list(config.PAGES))
def test_page_responds_with_200(page: Page, base_url: str, path: str):
    response = page.goto(base_url + path, wait_until="load")
    assert response is not None and response.status == 200, f"{path or '/'} answered {response and response.status}"


def test_unknown_page_returns_404(page: Page, base_url: str):
    response = page.request.get(base_url + "this-page-does-not-exist/")
    assert response.status == 404, f"Expected 404 for a missing page, got {response.status}"


def test_rover_redirects_to_home(page: Page, base_url: str):
    page.goto(base_url + "rover/", wait_until="load")
    page.wait_for_url(base_url, timeout=10_000)
    expect(page.locator("#hero")).to_be_visible()


# --------------------------------------------------------------------------- assets
def test_manifest_and_icons_are_valid(page: Page, base_url: str):
    response = page.request.get(base_url + "manifest.webmanifest")
    assert response.status == 200, f"manifest answered {response.status}"
    manifest = json.loads(response.text())
    for key in ("name", "short_name", "start_url", "icons"):
        assert key in manifest, f"manifest is missing '{key}'"
    assert manifest["icons"], "manifest has no icons"
    for icon in manifest["icons"]:
        r = page.request.get(base_url + icon["src"])
        assert r.status == 200, f"icon {icon['src']} answered {r.status}"
        assert r.headers.get("content-type", "").startswith("image/"), f"icon {icon['src']} is not an image"


def test_story_video_and_poster_are_served(page: Page, base_url: str):
    video = page.request.head(base_url + "assets/story.mp4")
    assert video.status == 200, f"story.mp4 answered {video.status}"
    assert "video" in video.headers.get("content-type", ""), f"story.mp4 content-type: {video.headers.get('content-type')}"
    poster = page.request.get(base_url + "assets/poster.jpg")
    assert poster.status == 200 and poster.headers.get("content-type", "").startswith("image/")


# --------------------------------------------------------------------------- navigation
@pytest.mark.parametrize("target,label", list(config.CHAPTERS.items()))
def test_navigation_link_opens_chapter(home: Page, target: str, label: str):
    link = home.locator(f"#navigation a[data-to='{target}']")
    expect(link).to_be_visible()
    link.click()
    expect(home.locator("#chapter")).to_contain_text(label, timeout=10_000)
    section = home.locator(f"#{target}")
    expect(section).to_be_visible()
    expect(section).not_to_have_attribute("inert", "")
    assert home.evaluate("location.hash") == f"#{target[2:]}", "URL hash was not updated"
    expect(link).to_have_attribute("aria-current", "location")


def test_next_buttons_walk_through_every_room(home: Page):
    home.locator("#navigation a[data-to='p-about']").click()
    expect(home.locator("#chapter")).to_contain_text("ABOUT ME")
    order = ["p-skills", "p-projects", "p-contact"]
    for target in order:
        home.locator(f".wall .next[data-to='{target}']").click()
        expect(home.locator("#chapter")).to_contain_text(config.CHAPTERS[target], timeout=10_000)
    home.locator(".wall .next[data-to='top']").click()
    expect(home.locator("#chapter")).to_contain_text("LANDING", timeout=10_000)


def test_journey_arrow_controls(home: Page):
    nxt, prev = home.locator("#next-room"), home.locator("#prev-room")
    expect(nxt).to_be_visible()
    nxt.click()
    expect(home.locator("#chapter")).to_contain_text("ABOUT ME", timeout=10_000)
    nxt.click()
    expect(home.locator("#chapter")).to_contain_text("TOOLKIT", timeout=10_000)
    prev.click()
    expect(home.locator("#chapter")).to_contain_text("ABOUT ME", timeout=10_000)


def test_keyboard_drives_the_journey(home: Page):
    home.locator("body").click(position={"x": 5, "y": 5})
    home.keyboard.press("End")
    expect(home.locator("#chapter")).to_contain_text("CONTACT", timeout=10_000)
    home.keyboard.press("Home")
    expect(home.locator("#chapter")).to_contain_text("LANDING", timeout=10_000)
    # Each PageDown drives the rover 0.6 screen heights along a journey that is 26 screens long,
    # so about 19 presses reach the first room.
    for _ in range(22):
        home.keyboard.press("PageDown")
    expect(home.locator("#chapter")).to_contain_text("ABOUT ME", timeout=10_000)


def test_hash_deep_link_opens_chapter(page: Page, base_url: str):
    page.goto(base_url + "#skills", wait_until="load")
    expect(page.locator("#chapter")).to_contain_text("TOOLKIT", timeout=15_000)
    expect(page.locator("#p-skills")).to_be_visible()


def test_hero_explore_button_goes_to_work(home: Page):
    home.locator("#hero .action-primary").click()
    expect(home.locator("#chapter")).to_contain_text("SELECTED WORK", timeout=10_000)


def test_brand_link_returns_to_start(home: Page):
    home.locator("#navigation a[data-to='p-contact']").click()
    expect(home.locator("#chapter")).to_contain_text("CONTACT")
    home.locator("#brand").click()
    expect(home.locator("#chapter")).to_contain_text("LANDING", timeout=10_000)


def test_progress_bar_grows_with_journey(home: Page):
    before = home.evaluate("document.getElementById('prog').getBoundingClientRect().width")
    home.locator("#navigation a[data-to='p-contact']").click()
    home.wait_for_timeout(800)
    after = home.evaluate("document.getElementById('prog').getBoundingClientRect().width")
    assert after > before, f"Progress bar did not grow ({before:.0f}px -> {after:.0f}px)"


# --------------------------------------------------------------------------- dialog & contact
def test_read_portfolio_dialog_opens_and_closes(home: Page):
    dialog = home.locator("#dossier")
    home.locator("#read").click()
    expect(dialog).to_be_visible()
    assert home.evaluate("document.getElementById('dossier').open"), "dialog.open is false after clicking Read"
    expect(dialog.locator("#dossier-title")).to_contain_text("Giorgi Khuchua")
    assert dialog.locator(".dossier-section").count() == 4, "dialog should have 4 sections"
    home.locator("#close-dossier").click()
    expect(dialog).to_be_hidden()
    home.locator("#hero button[data-read]").click()
    expect(dialog).to_be_visible()
    home.keyboard.press("Escape")
    expect(dialog).to_be_hidden()


def test_copy_email_button(home: Page):
    home.locator("#navigation a[data-to='p-contact']").click()
    expect(home.locator("#p-contact")).to_be_visible()
    home.locator("#copy").click()
    expect(home.locator("#copy-status")).to_have_text("Email copied.")
    clipboard = home.evaluate("navigator.clipboard.readText()")
    assert clipboard == config.CONTACT_EMAIL, f"Clipboard contains '{clipboard}'"


def test_contact_links_point_to_the_right_places(home: Page):
    mail = home.locator("#p-contact a.mail")
    expect(mail).to_have_attribute("href", f"mailto:{config.CONTACT_EMAIL}")
    expect(mail).to_have_text(config.CONTACT_EMAIL)
    github = home.locator("#p-contact a[href*='github.com']")
    expect(github).to_have_attribute("href", config.GITHUB_PROFILE)
    expect(github).to_have_attribute("target", "_blank")
    rel = github.get_attribute("rel") or ""
    assert "noopener" in rel, "external link is missing rel=noopener"


def test_github_profile_is_reachable(page: Page):
    response = page.request.get(config.GITHUB_PROFILE)
    assert response.status == 200, f"GitHub profile answered {response.status}"


# --------------------------------------------------------------------------- mobile
@pytest.mark.parametrize("viewport", ["mobile"], indirect=True)
def test_mobile_layout_has_no_horizontal_overflow(home: Page, notes):
    width = home.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
    assert width[0] <= width[1], f"Page is wider than the viewport: {width[0]}px > {width[1]}px"
    for selector in ("#brand", "#read", "#hero h1", "#journey-controls"):
        box = home.locator(selector).bounding_box()
        assert box, f"{selector} has no box on mobile"
        assert box["x"] >= 0 and box["x"] + box["width"] <= width[1] + 1, f"{selector} overflows the viewport"
    notes.append(f"scrollWidth {width[0]}px / viewport {width[1]}px")


@pytest.mark.parametrize("viewport", ["mobile"], indirect=True)
def test_mobile_navigation_still_works(home: Page):
    home.locator("#next-room").click()
    expect(home.locator("#chapter")).to_contain_text("ABOUT ME", timeout=10_000)
    home.locator("#read").click()
    expect(home.locator("#dossier")).to_be_visible()


# --------------------------------------------------------------------------- classic page
def test_classic_navigation_targets_exist(classic: Page):
    hrefs = classic.eval_on_selector_all("#links a", "els => els.map(e => e.getAttribute('href'))")
    assert hrefs, "classic page has no navigation links"
    for href in hrefs:
        assert href.startswith("#"), f"unexpected link {href}"
        assert classic.locator(href).count() == 1, f"navigation link {href} has no matching section"


@pytest.mark.parametrize("message,expected", [
    ("python", "Python"),
    ("hello", "Hello"),
    ("caritas", "Caritas Georgia"),
])
def test_classic_chat_demo_answers(classic: Page, message: str, expected: str):
    before = classic.locator("#messages .bubble").count()
    classic.fill("#chat-text", message)
    classic.press("#chat-text", "Enter")
    expect(classic.locator("#messages .bubble")).to_have_count(before + 2)
    reply = classic.locator("#messages .bubble").last
    expect(reply).to_contain_text(expected, ignore_case=True)
    expect(classic.locator("#chat-text")).to_have_value("")


def test_classic_copy_email_and_footer_year(classic: Page):
    classic.locator("#copy-email").click()
    expect(classic.locator("#copy-status")).to_contain_text("copied", ignore_case=True)
    year = classic.evaluate("new Date().getFullYear()")
    expect(classic.locator("#year")).to_have_text(str(year))


@pytest.mark.parametrize("viewport", ["mobile"], indirect=True)
def test_classic_mobile_menu_toggles(classic: Page):
    menu = classic.locator("#menu")
    expect(menu).to_be_visible()
    expect(menu).to_have_attribute("aria-expanded", "false")
    menu.click()
    expect(menu).to_have_attribute("aria-expanded", "true")
    expect(classic.locator("#links")).to_be_visible()
    menu.click()
    expect(menu).to_have_attribute("aria-expanded", "false")
