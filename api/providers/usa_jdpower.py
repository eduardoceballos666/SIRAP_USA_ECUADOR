"""J.D. Power license-plate lookup for United States plates.

Reads the public report page ``/cars/license-plate-lookup-and-decoder/<plate>-<state>-license-plate-report``
with a headless Chromium (Playwright, already part of the image) and returns the vehicle fields shown in the
"Vehicle details" panel of the United States interface. The names match the columns of section 23.2 of
``notebooks/usa/sirap_backend_usa.ipynb``::

    vehicle_title      "Year and model"  e.g. "2013 Honda Civic"
    specs_exterior     "Color"           e.g. "Taffeta White"
    vehicle_body_type  "Body type"       e.g. "Sedan 4D LX I4"
    state              "State"           e.g. "CA"

Good-citizen rules, same as the notebook: one request at a time, at least two seconds between request
starts, images/fonts/media and trackers are not downloaded, and an access-denied or rate-limit answer
(401/403/429) is recorded and never retried or worked around. Results are cached so a plate that is read
again does not hit the site again. The page returns vehicle information only, not an owner's name or address.

Switch it off with ``vehicle_lookup.enabled: false`` in ``config/countries/usa.yaml``.
"""

from __future__ import annotations

import re
import threading
import time
from dataclasses import dataclass
from typing import Callable

from src.utils import get_logger

logger = get_logger("sirap.api.jdpower")

REPORT_BASE = "https://www.jdpower.com/cars/license-plate-lookup-and-decoder"
PAGE_TIMEOUT_MS = 30_000
MIN_SECONDS_BETWEEN_REQUESTS = 2.0
CACHE_SECONDS_FOUND = 24 * 3600
CACHE_SECONDS_OTHER = 10 * 60
CACHE_MAX_ENTRIES = 500

BLOCKED_ASSETS = {"image", "font", "media"}
BLOCKED_TRACKERS = ("google-analytics.com", "googletagmanager.com", "doubleclick.net")
SPEC_LABELS = {
    "make": "make",
    "exterior": "exterior",
    "interior": "interior",
    "mpg": "mpg",
    "horsepower": "horsepower",
    "fuel type": "fuel_type",
    "transmission": "transmission",
    "drivetrain": "drivetrain",
    "displacement": "displacement",
    "cylinders": "cylinders",
    "fuel tank capacity": "fuel_tank_capacity",
    "towing capacity": "towing_capacity",
    "seating capacity": "seating_capacity",
}
# Lines that can follow the report heading but are not the body type.
NON_BODY_TYPE_PREFIXES = ("see what", "get a history report", "see all photos", "overview", "beenverified")


@dataclass
class ReportPage:
    """What the browser saw: HTTP status, report heading and the visible text."""

    status: int
    title: str = ""
    report_text: str = ""
    body_text: str = ""


Fetcher = Callable[[str], ReportPage]


def lookup_enabled(config: dict) -> bool:
    """True when the country profile switches the J.D. Power lookup on."""
    section = (config or {}).get("vehicle_lookup") or {}
    return bool(section.get("enabled")) and str(section.get("provider", "")).casefold() == "jdpower"


def report_url(serial: str, state: str) -> str:
    return f"{REPORT_BASE}/{serial.lower()}-{state.lower()}-license-plate-report"


def parse_visible_specs(report_text: str) -> dict[str, str]:
    """Extract a limited set of adjacent label/value pairs from the visible report text."""
    lines = [" ".join(line.split()) for line in report_text.splitlines()]
    lines = [line for line in lines if line]
    specs: dict[str, str] = {}
    labels = {label.casefold(): key for label, key in SPEC_LABELS.items()}
    for index, line in enumerate(lines):
        folded = line.casefold().strip().rstrip(":")
        if folded in labels:
            if index + 1 < len(lines):
                value = lines[index + 1].strip()
                if value and value.casefold() not in labels:
                    specs[labels[folded]] = value
            continue
        for label, key in SPEC_LABELS.items():
            prefix = label.casefold() + ":"
            if line.casefold().startswith(prefix):
                value = line[len(label) + 1:].strip()
                if value:
                    specs[key] = value
    return specs


def parse_vehicle_body_type(report_text: str, vehicle_title: str) -> str:
    """Return the line shown right under the report heading, e.g. "Sedan 4D LX I4"."""
    title = " ".join(str(vehicle_title).split()).casefold()
    if not title:
        return ""
    lines = [" ".join(line.split()) for line in report_text.splitlines()]
    lines = [line for line in lines if line]
    for index, line in enumerate(lines[:-1]):
        if line.casefold() != title:
            continue
        candidate = lines[index + 1]
        folded = candidate.casefold().rstrip(":")
        if folded.startswith(NON_BODY_TYPE_PREFIXES) or folded in SPEC_LABELS:
            continue
        return candidate
    return ""


def _intercept(route) -> None:
    request = route.request
    url = request.url.lower()
    if request.resource_type in BLOCKED_ASSETS or any(domain in url for domain in BLOCKED_TRACKERS):
        route.abort()
    else:
        route.continue_()


def fetch_report(url: str) -> ReportPage:
    """Open the report in headless Chromium. Raises if the browser is missing or the page misbehaves."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_default_navigation_timeout(PAGE_TIMEOUT_MS)
            page.route("**/*", _intercept)
            response = page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            if response is None:
                return ReportPage(status=0)
            if response.status != 200:
                return ReportPage(status=response.status)
            heading = page.locator("h1").first
            heading.wait_for(state="visible", timeout=10_000)
            title = (heading.text_content() or "").strip()
            main = page.locator("main")
            has_main = main.count() > 0
            report_text = main.inner_text(timeout=5_000) if has_main else page.locator("body").inner_text(timeout=5_000)
            body_text = page.locator("body").inner_text(timeout=5_000) if has_main else report_text
            return ReportPage(status=200, title=title, report_text=report_text, body_text=body_text)
        finally:
            browser.close()


def _record(serial: str, state: str, **changes) -> dict:
    record = {
        "plate": serial,
        "state": state,
        "lookup_key": f"{state}:{serial}" if state and serial else "",
        "lookup_url": report_url(serial, state) if serial and len(state) == 2 else "",
        "lookup_status": "not_started",
        "vehicle_title": "",
        "vehicle_body_type": "",
        "specs": {},
        "specs_exterior": "",
        "error": "",
    }
    record.update(changes)
    return record


def _read_report(serial: str, state: str, fetcher: Fetcher) -> dict:
    url = report_url(serial, state)
    try:
        page = fetcher(url)
    except ImportError as error:
        return _record(serial, state, lookup_status="browser_unavailable", error=f"{type(error).__name__}: {error}")
    except Exception as error:  # noqa: BLE001 - any browser/page failure must degrade to local data
        return _record(serial, state, lookup_status="error", error=f"{type(error).__name__}: {error}")
    if page.status == 0:
        return _record(serial, state, lookup_status="no_response", error="The browser received no HTTP response.")
    if page.status in (401, 403, 429):
        return _record(
            serial, state, lookup_status=f"access_limited_{page.status}",
            error=f"J.D. Power returned HTTP {page.status}; no retry was attempted.",
        )
    if page.status != 200:
        return _record(serial, state, lookup_status=f"http_{page.status}", error=f"J.D. Power returned HTTP {page.status}.")
    title = " ".join(page.title.split())
    if not title:
        return _record(serial, state, lookup_status="no_report_title")
    specs = parse_visible_specs(page.report_text)
    body_type = parse_vehicle_body_type(page.report_text, title) or parse_vehicle_body_type(page.body_text, title)
    return _record(
        serial, state, lookup_status="found", vehicle_title=title, vehicle_body_type=body_type,
        specs=specs, specs_exterior=specs.get("exterior", ""),
    )


# --- shared state: one request at a time, spaced out, cached -----------------------------------
_LOCK = threading.Lock()
_CACHE_LOCK = threading.Lock()
_CACHE: dict[tuple[str, str], tuple[float, dict]] = {}
_SCHEDULE = {"next_start": 0.0}


def reset_state() -> None:
    """Forget cached results and pacing (used by the tests)."""
    with _CACHE_LOCK:
        _CACHE.clear()
    _SCHEDULE["next_start"] = 0.0


def _cache_get(key: tuple[str, str], clock: Callable[[], float]) -> dict | None:
    with _CACHE_LOCK:
        entry = _CACHE.get(key)
        if entry is None:
            return None
        if entry[0] <= clock():
            _CACHE.pop(key, None)
            return None
        return dict(entry[1])


def _cache_put(key: tuple[str, str], record: dict, clock: Callable[[], float]) -> None:
    ttl = CACHE_SECONDS_FOUND if record["lookup_status"] == "found" else CACHE_SECONDS_OTHER
    with _CACHE_LOCK:
        while len(_CACHE) >= CACHE_MAX_ENTRIES:
            _CACHE.pop(next(iter(_CACHE)))
        _CACHE[key] = (clock() + ttl, dict(record))


def lookup(
    serial: str,
    state: str,
    *,
    fetcher: Fetcher | None = None,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> dict:
    """Look up one plate. Never raises: any failure is reported in ``lookup_status`` / ``error``."""
    serial = re.sub(r"[^A-Z0-9]", "", str(serial or "").upper())
    state = re.sub(r"[^A-Z]", "", str(state or "").upper())
    if not serial or len(state) != 2:
        return _record(
            serial, state, lookup_status="invalid_input",
            error="Plate must be alphanumeric and state must be a two-letter code.",
        )
    key = (state, serial)
    cached = _cache_get(key, clock)
    if cached is not None:
        return cached
    with _LOCK:
        cached = _cache_get(key, clock)  # another request may have filled it while this one waited
        if cached is not None:
            return cached
        delay = _SCHEDULE["next_start"] - clock()
        if delay > 0:
            sleep(delay)
        _SCHEDULE["next_start"] = clock() + MIN_SECONDS_BETWEEN_REQUESTS
        record = _read_report(serial, state, fetcher or fetch_report)
    _cache_put(key, record, clock)
    logger.info("J.D. Power lookup %s:%s -> %s", state, serial, record["lookup_status"])
    return dict(record)


def vehicle_fields(record: dict) -> dict[str, str]:
    """The values the interface shows; empty when the report was not found."""
    if record.get("lookup_status") != "found":
        return {}
    fields = {
        "state": record.get("state", ""),
        "vehicle_title": record.get("vehicle_title", ""),
        "vehicle_body_type": record.get("vehicle_body_type", ""),
        "specs_exterior": record.get("specs_exterior", ""),
    }
    return {key: value for key, value in fields.items() if value}
