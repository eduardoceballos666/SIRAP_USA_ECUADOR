"""J.D. Power license-plate lookup for United States plates.

Reads the public report page ``/cars/license-plate-lookup-and-decoder/<plate>-<state>-license-plate-report``
with a headless Chromium (Playwright, already part of the image) and returns the vehicle fields shown in the
"Vehicle details" panel of the United States interface. The names match the columns of section 23.2 of
``notebooks/usa/sirap_backend_usa.ipynb``::

    vehicle_title      "Year and model"  e.g. "2013 Honda Civic"
    specs_exterior     "Color"           e.g. "Taffeta White"
    vehicle_body_type  "Body type"       e.g. "Sedan 4D LX I4"
    state              "State"           e.g. "CA"

The report is opened by its direct URL first. If that does not show the report, the lookup page is used the way a
person would: the plate is typed, the state is chosen and "Check Plate" is pressed. An access-denied or rate-limit
answer at any step ends the lookup.

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

from src.usa_jurisdiction import STATE_ABBR_TO_NAME
from src.utils import get_logger

logger = get_logger("sirap.api.jdpower")

REPORT_BASE = "https://www.jdpower.com/cars/license-plate-lookup-and-decoder"
PAGE_TIMEOUT_MS = 30_000
REPORT_READY_TIMEOUT_MS = 12_000
# Fallback when the direct report URL does not show the report: use the lookup form like a person would.
LOOKUP_FORM_FALLBACK = True
FORM_STEP_TIMEOUT_MS = 4_000       # for the form to appear
FORM_CONTROL_TIMEOUT_MS = 1_000    # for each candidate control once the form is there
FORM_REPORT_TIMEOUT_MS = 15_000    # for the report to appear after "Check Plate"
FORM_FALLBACK_LATEST_SECONDS = 50  # the interface waits about two minutes in total; never start the form later
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
# Words that make the submit button the lookup button and not, say, the site search or a category menu.
SUBMIT_BUTTON_PATTERN = re.compile(
    r"\b(check( plate)?|look ?up|search|submit|find|continue|decode|get report|view report)\b|^go$", re.IGNORECASE
)
CHECK_PLATE_BUTTON_PATTERN = re.compile(r"\bcheck (the )?plate\b", re.IGNORECASE)  # J.D. Power's own button
# On the real report the <h1> is the plate line ("6ZGY984 - California License Plate Report:"); the vehicle
# name is the first line that starts with a model year.
VEHICLE_TITLE_PATTERN = re.compile(r"^(?:19|20)\d{2}\s+\S.{2,78}$")
# Lines that can follow the report heading but are not the body type.
NON_BODY_TYPE_PREFIXES = ("see what", "get a history report", "see all photos", "overview", "beenverified")


# True once the results page has been drawn: the heading is "<year> <make> <model>" or an "Overview" section
# exists. The report is filled in by scripts after the first HTML, so the heading alone is not enough.
REPORT_READY_JS = r"""() => {
  const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const h1 = document.querySelector('h1');
  const title = h1 ? clean(h1.innerText) : '';
  const hasOverview = Array.from(document.querySelectorAll('h2, h3'))
    .some((h) => clean(h.innerText).toLowerCase() === 'overview');
  return /^(19|20)\d{2}\s+\S/.test(title) || (title !== '' && hasOverview);
}"""


@dataclass
class ReportPage:
    """What the browser saw: HTTP status, report heading and the visible text."""

    status: int
    title: str = ""
    report_text: str = ""
    body_text: str = ""
    path: str = ""            # "direct_url" or "form": how the page was reached
    problem_status: str = ""  # set when the page is not the report and the reason is known
    problem: str = ""


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


def find_vehicle_title(heading: str, report_text: str) -> str:
    """The vehicle name ("2013 Honda Civic"): the <h1> if it is one, else the first line starting with a year."""
    heading = " ".join(str(heading).split())
    if not heading:
        return ""  # not a report page
    if VEHICLE_TITLE_PATTERN.match(heading):
        return heading
    lines = [" ".join(line.split()) for line in str(report_text).splitlines()]
    for line in [line for line in lines if line][:30]:
        if VEHICLE_TITLE_PATTERN.match(line) and not line.endswith(":") and "report" not in line.casefold():
            return line
    return ""


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


def _wait_until_rendered(page, timeout_ms: int | None = None) -> bool:
    """Wait for the report, its Overview cards and a steady page text. False when the report never appeared."""
    timeout_ms = REPORT_READY_TIMEOUT_MS if timeout_ms is None else timeout_ms
    try:
        page.wait_for_function(REPORT_READY_JS, timeout=timeout_ms)
    except Exception:  # noqa: BLE001 - what is on the page is read anyway; the parsers report a missing report
        return False
    try:
        page.get_by_text("Overview", exact=True).first.wait_for(state="visible", timeout=5_000)
    except Exception:  # noqa: BLE001
        pass
    try:
        page.wait_for_load_state("networkidle", timeout=4_000)
    except Exception:  # noqa: BLE001
        pass
    previous, stable, waited = -1, 0, 0
    while stable < 2 and waited < 4_000:
        length = page.evaluate("() => ((document.querySelector('main') || document.body).innerText || '').length")
        stable = stable + 1 if length == previous else 0
        previous = length
        page.wait_for_timeout(300)
        waited += 300
    return True


def _first_visible(candidates, timeout_ms: int):
    """The first locator that becomes visible, or None."""
    for locator in candidates:
        try:
            locator.first.wait_for(state="visible", timeout=timeout_ms)
            return locator.first
        except Exception:  # noqa: BLE001
            continue
    return None


def _choose_state(page, state: str) -> None:
    """Pick the state in the lookup form: a native <select> or a searchable dropdown."""
    name = STATE_ABBR_TO_NAME.get(state, state)
    native = page.locator("select").filter(has_text=name)
    if native.count():
        for option in ({"value": state}, {"label": name}, {"label": state}):
            try:
                native.first.select_option(timeout=FORM_CONTROL_TIMEOUT_MS, **option)
                return
            except Exception:  # noqa: BLE001
                continue
    box = _first_visible(
        [
            page.get_by_role("combobox"),
            page.get_by_label(re.compile("state", re.IGNORECASE)),
            page.get_by_placeholder(re.compile("state", re.IGNORECASE)),
        ],
        FORM_CONTROL_TIMEOUT_MS,
    )
    if box is None:
        raise RuntimeError("The state field was not found on the lookup page.")
    box.click()
    try:
        box.fill(name)
    except Exception:  # noqa: BLE001 - a dropdown that cannot be typed into is clicked instead
        pass
    option = re.compile(rf"^({re.escape(name)}|{re.escape(state)})$", re.IGNORECASE)
    page.get_by_role("option", name=option).first.click(timeout=FORM_STEP_TIMEOUT_MS)


def _fill_and_submit_form(page, plate: str, state: str) -> None:
    """Type the plate, choose the state and press the lookup button of the same form."""
    page.wait_for_selector("input, select", state="visible", timeout=FORM_STEP_TIMEOUT_MS)
    plate_input = _first_visible(
        [
            page.get_by_placeholder(re.compile("plate", re.IGNORECASE)),
            page.get_by_label(re.compile("plate", re.IGNORECASE)),
            page.locator("input[name*='plate' i], input[id*='plate' i]"),
            page.locator("input[type='text']"),
        ],
        FORM_CONTROL_TIMEOUT_MS,
    )
    if plate_input is None:
        raise RuntimeError("The license plate field was not found on the lookup page.")
    plate_input.fill(plate)
    _choose_state(page, state)
    form = plate_input.locator("xpath=ancestor::form[1]")
    submit = None
    for scope in ([form, page] if form.count() else [page]):
        submit = _first_visible(
            [
                scope.get_by_role("button", name=CHECK_PLATE_BUTTON_PATTERN),
                scope.get_by_role("button", name=SUBMIT_BUTTON_PATTERN),
                scope.locator("button[type='submit'], input[type='submit']"),
            ],
            FORM_CONTROL_TIMEOUT_MS,
        )
        if submit is not None:
            break
    if submit is None:
        plate_input.press("Enter")
    else:
        submit.click()


def _snapshot(page, path: str) -> ReportPage:
    """Read the heading and the visible text of the page the browser is on."""
    title = page.evaluate("() => { const h = document.querySelector('h1'); return h ? (h.textContent || '') : ''; }")
    main = page.locator("main")
    has_main = main.count() > 0
    report_text = main.inner_text(timeout=5_000) if has_main else page.locator("body").inner_text(timeout=5_000)
    body_text = page.locator("body").inner_text(timeout=5_000) if has_main else report_text
    return ReportPage(status=200, title=title.strip(), report_text=report_text, body_text=body_text, path=path)


def _open_report_via_form(page, plate: str, state: str, lookup_url: str) -> ReportPage:
    """Open the lookup page, enter the plate and the state, and read the page that follows."""
    response = page.goto(lookup_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
    status = response.status if response is not None else 0
    if status != 200:
        return ReportPage(status=status, path="form")  # includes 401/403/429: recorded by the caller, not worked around
    try:
        _fill_and_submit_form(page, plate, state)
    except Exception as error:  # noqa: BLE001 - the form was not what was expected
        shot = _snapshot(page, "form")
        shot.problem_status, shot.problem = "form_failed", f"{type(error).__name__}: {error}"
        return shot
    ready = _wait_until_rendered(page, FORM_REPORT_TIMEOUT_MS)
    shot = _snapshot(page, "form")
    if not ready:
        shot.problem_status = "report_not_ready"
        shot.problem = "The report did not appear after the state and the plate were entered."
    return shot


def fetch_report(
    url: str,
    *,
    plate: str = "",
    state: str = "",
    lookup_url: str = REPORT_BASE,
    form_fallback: bool | None = None,
) -> ReportPage:
    """Open the report in headless Chromium. Raises if the browser is missing or the page misbehaves.

    ``url`` is the direct report URL. When it does not show the report and ``plate`` and ``state`` are given, the
    lookup form at ``lookup_url`` is used instead. 401/403/429 is returned as it is and nothing else is tried.
    """
    from playwright.sync_api import sync_playwright

    use_form = (LOOKUP_FORM_FALLBACK if form_fallback is None else form_fallback) and bool(plate) and len(state) == 2
    started = time.monotonic()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_default_navigation_timeout(PAGE_TIMEOUT_MS)
            page.route("**/*", _intercept)
            response = page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            if response is None:
                return ReportPage(status=0)
            status = response.status
            if status in (401, 403, 429):
                return ReportPage(status=status)
            if status == 200 and _wait_until_rendered(page):
                return _snapshot(page, "direct_url")
            if not use_form or status not in (200, 404) or time.monotonic() - started > FORM_FALLBACK_LATEST_SECONDS:
                return _snapshot(page, "direct_url") if status == 200 else ReportPage(status=status)
            page.wait_for_timeout(int(MIN_SECONDS_BETWEEN_REQUESTS * 1000))  # same pace as between two lookups
            return _open_report_via_form(page, plate, state, lookup_url)
        finally:
            browser.close()


def _record(serial: str, state: str, **changes) -> dict:
    record = {
        "plate": serial,
        "state": state,
        "lookup_key": f"{state}:{serial}" if state and serial else "",
        "lookup_url": report_url(serial, state) if serial and len(state) == 2 else "",
        "lookup_status": "not_started",
        "lookup_path": "",
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
    title = find_vehicle_title(page.title, page.report_text or page.body_text)
    if not title:
        return _record(
            serial, state, lookup_status=page.problem_status or "no_report_title", lookup_path=page.path, error=page.problem,
        )
    specs = parse_visible_specs(page.report_text)
    body_type = parse_vehicle_body_type(page.report_text, title) or parse_vehicle_body_type(page.body_text, title)
    return _record(
        serial, state, lookup_status="found", lookup_path=page.path, vehicle_title=title,
        vehicle_body_type=body_type, specs=specs, specs_exterior=specs.get("exterior", ""),
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
        record = _read_report(
            serial, state, fetcher or (lambda url: fetch_report(url, plate=serial, state=state))
        )
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
