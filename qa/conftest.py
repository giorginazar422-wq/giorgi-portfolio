"""Pytest fixtures and hooks: browser setup, console capture, local server, report generation."""
from __future__ import annotations

import functools
import http.server
import shutil
import socket
import sys
import threading
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config as settings  # noqa: E402
from reporting.collector import ReportCollector, TestResult  # noqa: E402


# --------------------------------------------------------------------------- options
def pytest_addoption(parser):
    parser.addoption("--site", default=settings.BASE_URL,
                     help="Site to test. Use 'local' to serve the repository with a local HTTP server.")
    parser.addoption("--headed", action="store_true", help="Run the browser with a visible window.")
    parser.addoption("--update-baselines", action="store_true",
                     help="Overwrite the visual baselines with the current screenshots.")
    parser.addoption("--slowmo", type=int, default=0, help="Slow down Playwright actions (ms).")


def pytest_configure(config):
    cfg = config
    base_url = cfg.getoption("--site")
    if base_url == "local":
        cfg._local_server = _start_local_server(settings.REPO_ROOT)
        base_url = f"http://127.0.0.1:{cfg._local_server.server_port}/"
    if not base_url.endswith("/"):
        base_url += "/"
    cfg.base_url = base_url
    cfg.report = ReportCollector(base_url, settings.REPORTS_DIR)
    for folder in (settings.SCREENSHOTS_DIR, settings.DIFFS_DIR):   # start every run clean
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True, exist_ok=True)


def pytest_unconfigure(config):
    cfg = config
    server = getattr(cfg, "_local_server", None)
    if server:
        server.shutdown()


def _start_local_server(root: Path) -> http.server.ThreadingHTTPServer:
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):  # keep the pytest output clean
            pass

    handler = functools.partial(QuietHandler, directory=str(root))
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


# --------------------------------------------------------------------------- fixtures
@pytest.fixture(scope="session")
def base_url(pytestconfig) -> str:
    return pytestconfig.base_url


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance, pytestconfig) -> Browser:
    browser = playwright_instance.chromium.launch(
        headless=not pytestconfig.getoption("--headed"),
        slow_mo=pytestconfig.getoption("--slowmo"),
    )
    yield browser
    browser.close()


class PageLog:
    """Console errors and failed network responses captured for one test."""

    def __init__(self):
        self.console_errors: list[str] = []
        self.failed_requests: list[str] = []

    def attach(self, page: Page) -> None:
        page.on("console", lambda m: self.console_errors.append(f"[{m.type}] {m.text}")
                if m.type == "error" else None)
        page.on("pageerror", lambda e: self.console_errors.append(f"[pageerror] {e}"))
        page.on("response", lambda r: self.failed_requests.append(f"{r.status} {r.url}")
                if r.status >= 400 else None)
        page.on("requestfailed", self._request_failed)

    def _request_failed(self, request) -> None:
        # Browsers abort their own media range requests once they have the bytes they need.
        if request.resource_type == "media" and "ERR_ABORTED" in (request.failure or ""):
            return
        self.failed_requests.append(f"FAILED {request.url} ({request.failure})")


@pytest.fixture
def viewport(request) -> dict:
    """Viewport for the test; parametrize indirectly with a key of settings.VIEWPORTS."""
    key = getattr(request, "param", "desktop")
    return settings.VIEWPORTS[key]


@pytest.fixture
def context(browser: Browser, viewport: dict, base_url: str) -> BrowserContext:
    ctx = browser.new_context(viewport=viewport, device_scale_factor=1, reduced_motion="reduce",
                              locale="en-US", timezone_id="Asia/Tbilisi")
    ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=base_url.rstrip("/"))
    ctx.set_default_timeout(15_000)
    yield ctx
    ctx.close()


@pytest.fixture
def page(context: BrowserContext, request) -> Page:
    page = context.new_page()
    log = PageLog()
    log.attach(page)
    request.node._page = page
    request.node._page_log = log
    request.node._notes = []
    request.node._screenshots = []
    yield page


@pytest.fixture
def notes(request) -> list[str]:
    """Append short notes that end up in the report for this test."""
    return request.node._notes


@pytest.fixture
def home(page: Page, base_url: str) -> Page:
    """The rover journey page, loaded and ready (video metadata available)."""
    page.goto(base_url, wait_until="load")
    page.wait_for_function(
        "() => !document.getElementById('hint').textContent.startsWith('Preparing')", timeout=20_000)
    return page


@pytest.fixture
def classic(page: Page, base_url: str) -> Page:
    page.goto(base_url + "classic/", wait_until="load")
    return page


# --------------------------------------------------------------------------- hooks
def _category(item) -> str:
    for marker in ("visual", "a11y", "functional"):
        if item.get_closest_marker(marker):
            return marker
    return item.fspath.purebasename.replace("test_", "")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "setup" and rep.outcome in ("failed", "skipped"):
        _record(item, rep)
    elif rep.when == "call":
        _record(item, rep)


def _record(item, rep) -> None:
    collector: ReportCollector = item.config.report
    page: Page | None = getattr(item, "_page", None)
    log: PageLog | None = getattr(item, "_page_log", None)
    screenshots = list(getattr(item, "_screenshots", []))

    if rep.outcome == "failed" and page is not None and not page.is_closed() and page.url != "about:blank":
        name = item.nodeid.split("::")[-1].replace("/", "_").replace("[", "_").replace("]", "")
        path = settings.SCREENSHOTS_DIR / f"FAIL_{name}.png"
        try:
            page.screenshot(path=path, full_page=False)
            screenshots.append(str(path.relative_to(settings.REPORTS_DIR)))
        except Exception:  # the page may already be gone
            pass

    message = ""
    if rep.outcome == "failed":
        message = str(rep.longrepr)
    elif rep.outcome == "skipped" and rep.longrepr:
        message = rep.longrepr[-1] if isinstance(rep.longrepr, tuple) else str(rep.longrepr)

    collector.add(TestResult(
        nodeid=item.nodeid,
        name=item.name,
        module=item.fspath.basename,
        category=_category(item),
        outcome=rep.outcome,
        duration=rep.duration,
        message=message,
        notes=list(getattr(item, "_notes", [])),
        screenshots=screenshots,
        console_errors=log.console_errors if log else [],
        failed_requests=log.failed_requests if log else [],
    ))


def pytest_sessionfinish(session, exitstatus):
    collector: ReportCollector = getattr(session.config, "report", None)
    if collector is None:
        return
    html_path, json_path = collector.write()
    counts = collector.counts()
    rep = session.config.pluginmanager.get_plugin("terminalreporter")
    if rep:
        rep.write_sep("=", "QA report")
        rep.write_line(f"Site: {collector.base_url}")
        rep.write_line(f"Passed {counts['passed']}  Failed {counts['failed']}  Skipped {counts['skipped']}")
        rep.write_line(f"HTML: {html_path}")
        rep.write_line(f"JSON: {json_path}")
