"""Lightweight accessibility checks that do not need an external audit engine."""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.a11y

ACCESSIBLE_NAME_JS = """
(sel) => Array.from(document.querySelectorAll(sel)).map(el => {
  const text = (el.innerText || el.textContent || '').trim();
  const name = el.getAttribute('aria-label') || text;
  const labelledBy = el.getAttribute('aria-labelledby');
  return { tag: el.tagName.toLowerCase(), id: el.id, name: name || (labelledBy ? '[labelledby]' : '') };
})
"""


def _page_for(page: Page, base_url: str, path: str) -> Page:
    page.goto(base_url + path, wait_until="load")
    return page


@pytest.mark.parametrize("path", ["", "classic/", "mars/"], ids=["home", "classic", "mars"])
def test_document_basics(page: Page, base_url: str, path: str):
    _page_for(page, base_url, path)
    assert page.get_attribute("html", "lang"), f"{path or '/'} has no lang attribute"
    assert page.title().strip(), f"{path or '/'} has an empty <title>"
    assert page.locator("meta[name='viewport']").count() == 1, f"{path or '/'} has no viewport meta"
    assert page.locator("h1").count() >= 1, f"{path or '/'} has no <h1>"


@pytest.mark.parametrize("path", ["", "classic/"], ids=["home", "classic"])
def test_buttons_and_links_have_accessible_names(page: Page, base_url: str, path: str):
    _page_for(page, base_url, path)
    items = page.evaluate(ACCESSIBLE_NAME_JS, "button, a[href]")
    unnamed = [f"<{i['tag']} id='{i['id']}'>" for i in items if not i["name"]]
    assert not unnamed, "Controls without an accessible name: " + ", ".join(unnamed)


@pytest.mark.parametrize("path", ["", "classic/"], ids=["home", "classic"])
def test_images_have_alternative_text(page: Page, base_url: str, path: str):
    _page_for(page, base_url, path)
    missing = page.evaluate("""() => {
      const bad = [];
      document.querySelectorAll('img').forEach(i => { if (!i.hasAttribute('alt')) bad.push('img ' + (i.src || i.id)); });
      document.querySelectorAll('[role="img"]').forEach(i => { if (!i.getAttribute('aria-label')) bad.push('role=img ' + i.className); });
      return bad;
    }""")
    assert not missing, "Images without alternative text: " + ", ".join(missing)


def test_home_landmarks_and_live_regions(page: Page, base_url: str):
    _page_for(page, base_url, "")
    assert page.locator("main").count() == 1, "home page should have exactly one <main>"
    assert page.locator("nav[aria-label]").count() >= 1, "navigation has no aria-label"
    assert page.locator("dialog[aria-labelledby]").count() == 1, "dialog is not labelled"
    assert page.locator("[role='status']").count() >= 1, "copy-email status has no live region"


def test_noscript_fallback_exists(page: Page, base_url: str):
    _page_for(page, base_url, "")
    html = page.content()
    assert "<noscript>" in html and "mailto:" in html.split("<noscript>")[1], \
        "noscript fallback should contain a contact link"
