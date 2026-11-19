"""J.D. Power adapter: parsing, access rules, cache, pacing and the real browser path (against a local page)."""

from __future__ import annotations

import http.server
import threading

import pytest

from api.providers import usa_jdpower as jd
from src.utils import load_config

REPORT_TEXT = """Back to License Plate Selection
6ZGY984 - California License Plate Report:
2013 Honda Civic
Sedan 4D LX I4
See what 80% of people paid
Get a History Report
BeenVerified
See All Photos
Overview
Exterior
Taffeta White
Interior
Beige
MPG
28 MPG/39 MPG
"""
TITLE = "2013 Honda Civic"


def found_page(**changes):
    values = dict(status=200, title=TITLE, report_text=REPORT_TEXT, body_text=REPORT_TEXT)
    values.update(changes)
    return jd.ReportPage(**values)


class Recorder:
    """A fetcher that answers with a fixed page and remembers the URLs it was asked for."""

    def __init__(self, page=None, error=None):
        self.page, self.error, self.urls = page or found_page(), error, []

    def __call__(self, url):
        self.urls.append(url)
        if self.error:
            raise self.error
        return self.page


@pytest.fixture(autouse=True)
def clean_state():
    jd.reset_state()
    yield
    jd.reset_state()


def run(serial="6ZGY984", state="CA", fetcher=None, **kwargs):
    kwargs.setdefault("sleep", lambda seconds: None)
    return jd.lookup(serial, state, fetcher=fetcher or Recorder(), **kwargs)


# --- parsing -----------------------------------------------------------------------------------
def test_specs_and_body_type_come_from_the_report_text():
    assert jd.parse_visible_specs(REPORT_TEXT)["exterior"] == "Taffeta White"
    assert jd.parse_vehicle_body_type(REPORT_TEXT, TITLE) == "Sedan 4D LX I4"


def test_body_type_is_empty_rather_than_wrong():
    assert jd.parse_vehicle_body_type("2013 Honda Civic\nGet a History Report\n", TITLE) == ""
    assert jd.parse_vehicle_body_type("2013 Honda Civic\nExterior\nTaffeta White\n", TITLE) == ""
    assert jd.parse_vehicle_body_type(REPORT_TEXT, "") == ""
    assert jd.parse_vehicle_body_type("nothing here", TITLE) == ""


def test_body_type_skips_an_earlier_mention_of_the_title():
    text = "2013 Honda Civic\nSee what 80% of people paid\n" + REPORT_TEXT
    assert jd.parse_vehicle_body_type(text, TITLE) == "Sedan 4D LX I4"


# --- lookup ------------------------------------------------------------------------------------
def test_found_report_fills_the_four_interface_fields():
    fetcher = Recorder()
    record = run(fetcher=fetcher)
    assert fetcher.urls == ["https://www.jdpower.com/cars/license-plate-lookup-and-decoder/6zgy984-ca-license-plate-report"]
    assert record["lookup_status"] == "found"
    assert jd.vehicle_fields(record) == {
        "state": "CA", "vehicle_title": TITLE, "vehicle_body_type": "Sedan 4D LX I4", "specs_exterior": "Taffeta White",
    }


def test_real_page_heading_is_the_plate_line_so_the_vehicle_comes_from_the_text():
    # J.D. Power's <h1> is "<plate> - <state> License Plate Report:"; "2013 Honda Civic" is a line below it.
    heading = "6ZGY984 - California License Plate Report:"
    record = run(fetcher=Recorder(found_page(title=heading)))
    assert record["lookup_status"] == "found"
    assert jd.vehicle_fields(record) == {
        "state": "CA", "vehicle_title": TITLE, "vehicle_body_type": "Sedan 4D LX I4", "specs_exterior": "Taffeta White",
    }


def test_a_report_without_any_vehicle_line_is_not_shown_as_a_vehicle():
    page = found_page(title="6ZGY984 - California License Plate Report:", report_text="Overview\nExterior\nTaffeta White\n", body_text="")
    record = run(fetcher=Recorder(page))
    assert record["lookup_status"] == "no_report_title" and jd.vehicle_fields(record) == {}


def test_find_vehicle_title_ignores_report_lines_and_late_mentions():
    assert jd.find_vehicle_title("2013 Honda Civic", "") == TITLE
    assert jd.find_vehicle_title("Plate report", "2013 Honda Civic Report:\n" + REPORT_TEXT) == TITLE
    assert jd.find_vehicle_title("", REPORT_TEXT) == ""
    late = "\n".join(["filler"] * 40 + ["2024 Toyota Camry"])
    assert jd.find_vehicle_title("Plate report", late) == ""


def test_body_type_falls_back_to_the_whole_page_text():
    page = found_page(report_text="Overview\nExterior\nTaffeta White\n", body_text=REPORT_TEXT)
    assert run(fetcher=Recorder(page))["vehicle_body_type"] == "Sedan 4D LX I4"


def test_plate_and_state_are_normalized():
    record = run("6zg-y 984", "ca")
    assert (record["plate"], record["state"], record["lookup_status"]) == ("6ZGY984", "CA", "found")


@pytest.mark.parametrize("serial,state", [("", "CA"), ("6ZGY984", ""), ("6ZGY984", "CAL"), ("6ZGY984", "1")])
def test_invalid_input_never_reaches_the_site(serial, state):
    fetcher = Recorder()
    record = run(serial, state, fetcher)
    assert record["lookup_status"] == "invalid_input" and fetcher.urls == []
    assert jd.vehicle_fields(record) == {}


@pytest.mark.parametrize("status", [401, 403, 429])
def test_access_denied_or_rate_limited_is_recorded_and_not_retried(status):
    fetcher = Recorder(jd.ReportPage(status=status))
    first = run(fetcher=fetcher)
    again = run(fetcher=fetcher)
    assert first["lookup_status"] == again["lookup_status"] == f"access_limited_{status}"
    assert len(fetcher.urls) == 1  # the second call is answered from the short cache, not the site
    assert jd.vehicle_fields(first) == {}


@pytest.mark.parametrize("page,expected", [
    (jd.ReportPage(status=404), "http_404"),
    (jd.ReportPage(status=500), "http_500"),
    (jd.ReportPage(status=0), "no_response"),
    (found_page(title="  "), "no_report_title"),
])
def test_other_outcomes_are_reported_without_data(page, expected):
    record = run(fetcher=Recorder(page))
    assert record["lookup_status"] == expected and jd.vehicle_fields(record) == {}


def test_browser_problems_degrade_to_a_status_and_never_raise():
    assert run(fetcher=Recorder(error=ImportError("no playwright")))["lookup_status"] == "browser_unavailable"
    assert run("ABC1234", "NY", Recorder(error=RuntimeError("boom")))["lookup_status"] == "error"


def test_cache_and_expiry():
    now = [1000.0]
    fetcher = Recorder()
    kwargs = dict(clock=lambda: now[0])
    run(fetcher=fetcher, **kwargs)
    run(fetcher=fetcher, **kwargs)
    assert len(fetcher.urls) == 1
    run("6ZGY984", "TX", fetcher, **kwargs)  # same serial, other state: different vehicle
    assert len(fetcher.urls) == 2
    now[0] += jd.CACHE_SECONDS_FOUND + 1
    run(fetcher=fetcher, **kwargs)
    assert len(fetcher.urls) == 3

    denied = Recorder(jd.ReportPage(status=403))
    run("DENIED1", "CA", denied, **kwargs)
    now[0] += jd.CACHE_SECONDS_OTHER + 1  # failures are only remembered briefly
    run("DENIED1", "CA", denied, **kwargs)
    assert len(denied.urls) == 2


def test_requests_start_at_least_two_seconds_apart():
    now, slept = [100.0], []

    def sleep(seconds):
        slept.append(seconds)
        now[0] += seconds

    fetcher = Recorder()
    kwargs = dict(clock=lambda: now[0], sleep=sleep)
    jd.lookup("AAA1111", "CA", fetcher=fetcher, **kwargs)
    jd.lookup("BBB2222", "CA", fetcher=fetcher, **kwargs)
    assert slept == [jd.MIN_SECONDS_BETWEEN_REQUESTS]


def test_vehicle_fields_leaves_out_empty_values():
    record = run(fetcher=Recorder(found_page(report_text="Overview\n", body_text="")))
    assert jd.vehicle_fields(record) == {"state": "CA", "vehicle_title": TITLE}


def test_lookup_is_switched_on_by_the_united_states_profile():
    profile = load_config("config/countries/usa.yaml")
    assert jd.lookup_enabled(profile)
    for config in ({}, {"vehicle_lookup": {"enabled": False, "provider": "jdpower"}},
                   {"vehicle_lookup": {"enabled": True, "provider": "other"}}):
        assert not jd.lookup_enabled(config)


# --- real browser against a local page ---------------------------------------------------------
PAGE = b"""<!doctype html><html><body><header><a>Back to License Plate Selection</a></header>
<main><p>6ZGY984 - California License Plate Report:</p>
<h1>2013 Honda Civic</h1><div>Sedan 4D LX I4</div><div>See what 80% of people paid</div>
<div>Get a History Report</div><img src="/car.png"><div>See All Photos</div>
<h2>Overview</h2><div>Exterior</div><div>Taffeta White</div><div>Interior</div><div>Beige</div></main></body></html>"""


PAGE_REAL = PAGE.replace(b"<h1>2013 Honda Civic</h1>", b"<h1>6ZGY984 - California License Plate Report:</h1><h2>2013 Honda Civic</h2>").replace(
    b"<p>6ZGY984 - California License Plate Report:</p>", b"")


# The heading, the vehicle lines and the Overview arrive at different moments: the Overview cards are drawn by a
# script 800 ms after the page loads, as on the real report.
PAGE_LATE = b"""<!doctype html><html><body><main><a>Back to License Plate Selection</a>
<h1>6ZGY984 - California License Plate Report:</h1><h2>2013 Honda Civic</h2><div>Sedan 4D LX I4</div>
<div id="slot"></div></main>
<script>setTimeout(function(){document.getElementById('slot').innerHTML =
 '<h2>Overview</h2><div><div>Exterior</div><div>Taffeta White</div></div><div><div>Interior</div><div>Beige</div></div>';},800);</script>
</body></html>"""


# The lookup page of the real site: a plate field, a searchable State dropdown and "Check Plate". The first button
# on the page is a decoy that must not be pressed. Pressing "Check Plate" opens the report after a short delay.
LOOKUP_COMBOBOX = b"""<!doctype html><html><body><header><ul><li>Vehicles for Sale</li></ul></header>
<div><h1>License Plate Lookup &amp; Decoder</h1>
<div><label for="lp">License Plate*</label><input id="lp" name="licensePlate" type="text"></div>
<div><label for="st">State*</label><input id="st" role="combobox" aria-label="State*" type="text" autocomplete="off">
<ul id="opts" role="listbox" hidden><li role="option">California</li><li role="option">Texas</li><li role="option">New York</li></ul></div>
<button id="vin" onclick="location.href='/decoy'">Vehicles for Sale</button>
<button id="chk">Check Plate</button></div>
<script>
const st=document.getElementById('st'), opts=document.getElementById('opts'); let chosen='';
const codes={California:'ca',Texas:'tx','New York':'ny'};
st.addEventListener('click',()=>{opts.hidden=false}); st.addEventListener('input',()=>{opts.hidden=false});
opts.addEventListener('click',(e)=>{if(e.target.tagName==='LI'){chosen=e.target.textContent;st.value=chosen;opts.hidden=true}});
document.getElementById('chk').addEventListener('click',()=>{
  const p=document.getElementById('lp').value.toLowerCase(); if(!p||!chosen) return;
  setTimeout(()=>{location.href='/report-form?plate='+p+'&state='+codes[chosen]},300);});
</script></body></html>"""

LOOKUP_SELECT = b"""<!doctype html><html><body><main><h1>License Plate Lookup</h1>
<form id="f" onsubmit="return go(event)">
 <label>License plate <input id="plate" type="text" placeholder="Enter license plate"></label>
 <label>State <select id="state"><option value="">Select state</option><option value="CA">California</option>
 <option value="TX">Texas</option></select></label><button type="submit">Look up</button></form></main>
<script>
function go(e){e.preventDefault();
 const p=document.getElementById('plate').value.toLowerCase(), s=document.getElementById('state').value.toLowerCase();
 if(!p||!s) return false; setTimeout(()=>{location.href='/report-form?plate='+p+'&state='+s},300); return false;}
</script></body></html>"""

LOOKUP_DEAD = LOOKUP_SELECT.replace(b"if(!p||!s) return false;", b"return false;")
GENERIC_PAGE = b"<!doctype html><html><body><main><h1>License Plate Lookup</h1><p>Enter a plate.</p></main></body></html>"


class LocalSite(http.server.BaseHTTPRequestHandler):
    hits: list[str] = []

    def do_GET(self):  # noqa: N802 - http.server API
        type(self).hits.append(self.path)
        routes = {
            "/ok": (200, PAGE), "/real": (200, PAGE_REAL), "/late": (200, PAGE_LATE), "/denied": (403, b"no"),
            "/missing": (404, b"no"), "/direct-miss": (200, GENERIC_PAGE), "/lookup": (200, LOOKUP_COMBOBOX),
            "/lookup-select": (200, LOOKUP_SELECT), "/lookup-dead": (200, LOOKUP_DEAD),
            "/lookup-denied": (429, b"slow down"), "/decoy": (200, GENERIC_PAGE),
        }
        path = self.path.split("?")[0]
        status, body = (200, PAGE_LATE) if path == "/report-form" else routes.get(path, (200, b"png"))
        self.send_response(status)
        html = body.startswith(b"<!doctype html>")
        self.send_header("Content-Type", "text/html" if html else "text/plain")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture
def local_site():
    LocalSite.hits = []
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), LocalSite)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


@pytest.fixture(scope="module")
def browser_available():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            playwright.chromium.launch(headless=True).close()
    except Exception as error:  # noqa: BLE001
        pytest.skip(f"Chromium is not available: {error}")


def test_real_browser_reads_the_report_and_skips_images(browser_available, local_site):
    page = jd.fetch_report(local_site + "/ok")
    assert (page.status, page.title) == (200, TITLE)
    assert jd.parse_vehicle_body_type(page.report_text, page.title) == "Sedan 4D LX I4"
    assert jd.parse_visible_specs(page.report_text)["exterior"] == "Taffeta White"
    assert "/car.png" not in LocalSite.hits  # images are blocked, as in the notebook


def test_real_browser_with_the_real_heading_structure(browser_available, local_site):
    assert PAGE_REAL != PAGE and b"<h1>6ZGY984" in PAGE_REAL
    record = run(fetcher=lambda url: jd.fetch_report(local_site + "/real"))
    assert record["lookup_status"] == "found"
    assert jd.vehicle_fields(record) == {
        "state": "CA", "vehicle_title": TITLE, "vehicle_body_type": "Sedan 4D LX I4", "specs_exterior": "Taffeta White",
    }


def test_real_browser_waits_for_the_overview_that_a_script_draws_late(browser_available, local_site):
    page = jd.fetch_report(local_site + "/late")
    assert page.status == 200 and "Taffeta White" in page.report_text
    record = run(fetcher=lambda url: page)
    assert record["lookup_status"] == "found"
    assert jd.vehicle_fields(record) == {
        "state": "CA", "vehicle_title": TITLE, "vehicle_body_type": "Sedan 4D LX I4", "specs_exterior": "Taffeta White",
    }


def test_real_browser_reports_denied_and_missing_pages(browser_available, local_site):
    assert jd.fetch_report(local_site + "/denied").status == 403
    assert jd.fetch_report(local_site + "/missing").status == 404
    record = run(fetcher=lambda url: jd.fetch_report(local_site + "/denied"))
    assert record["lookup_status"] == "access_limited_403"
    assert LocalSite.hits.count("/denied") == 2  # one request per call; nothing retried inside a call


# --- the lookup form as a fallback ---------------------------------------------------------------
FOUR_FIELDS = {"state": "CA", "vehicle_title": TITLE, "vehicle_body_type": "Sedan 4D LX I4", "specs_exterior": "Taffeta White"}


@pytest.fixture
def quick(monkeypatch):
    """Short waits so the tests do not sit through the real timeouts."""
    monkeypatch.setattr(jd, "REPORT_READY_TIMEOUT_MS", 1_500)
    monkeypatch.setattr(jd, "FORM_REPORT_TIMEOUT_MS", 3_000)
    monkeypatch.setattr(jd, "MIN_SECONDS_BETWEEN_REQUESTS", 0.2)


def form_fetch(site, direct, lookup, plate="6ZGY984", state="CA"):
    return jd.fetch_report(site + direct, plate=plate, state=state, lookup_url=site + lookup)


@pytest.mark.parametrize("direct", ["/direct-miss", "/missing"])
def test_real_browser_uses_the_lookup_form_when_the_direct_url_shows_no_report(browser_available, local_site, quick, direct):
    page = form_fetch(local_site, direct, "/lookup")
    assert page.path == "form" and page.status == 200 and not page.problem
    record = run(fetcher=lambda url: page)
    assert record["lookup_status"] == "found" and record["lookup_path"] == "form"
    assert jd.vehicle_fields(record) == FOUR_FIELDS
    assert "/report-form?plate=6zgy984&state=ca" in LocalSite.hits  # the plate typed and the state chosen
    assert "/decoy" not in LocalSite.hits  # the first button of the page is not the lookup button


def test_real_browser_form_with_a_native_state_select(browser_available, local_site, quick):
    page = form_fetch(local_site, "/direct-miss", "/lookup-select", plate="CX9S159", state="TX")
    assert page.path == "form" and not page.problem and page.title.startswith("6ZGY984")
    assert "/report-form?plate=cx9s159&state=tx" in LocalSite.hits


def test_real_browser_does_not_open_the_form_when_the_direct_url_works(browser_available, local_site, quick):
    page = form_fetch(local_site, "/late", "/lookup")
    assert page.path == "direct_url" and "Taffeta White" in page.report_text
    assert not any(path.startswith("/lookup") for path in LocalSite.hits)


def test_real_browser_form_can_be_switched_off(browser_available, local_site, quick):
    page = jd.fetch_report(local_site + "/direct-miss", plate="6ZGY984", state="CA",
                           lookup_url=local_site + "/lookup", form_fallback=False)
    assert page.path == "direct_url" and jd.find_vehicle_title(page.title, page.report_text) == ""
    assert "/lookup" not in LocalSite.hits


@pytest.mark.parametrize("lookup,expected_hits", [("/lookup", ["/denied"]), ("/lookup-denied", ["/direct-miss", "/lookup-denied"])])
def test_real_browser_access_limits_stop_every_path(browser_available, local_site, quick, lookup, expected_hits):
    direct = "/denied" if lookup == "/lookup" else "/direct-miss"
    page = form_fetch(local_site, direct, lookup)
    assert page.status in (403, 429)
    assert LocalSite.hits == expected_hits  # no form after a 403, nothing after a 429 on the form page
    record = run(fetcher=lambda url: page)
    assert record["lookup_status"] == f"access_limited_{page.status}" and jd.vehicle_fields(record) == {}


def test_real_browser_form_that_does_nothing_is_reported_without_data(browser_available, local_site, quick):
    page = form_fetch(local_site, "/direct-miss", "/lookup-dead")
    assert (page.problem_status, page.path) == ("report_not_ready", "form")
    record = run(fetcher=lambda url: page)
    assert record["lookup_status"] == "report_not_ready" and record["lookup_path"] == "form"
    assert "did not appear" in record["error"] and jd.vehicle_fields(record) == {}


def test_real_browser_page_without_a_plate_field_is_form_failed(browser_available, local_site, quick):
    page = form_fetch(local_site, "/direct-miss", "/direct-miss")  # the "lookup page" has no form at all
    assert page.problem_status == "form_failed" and page.problem


def test_known_problems_become_the_record_status_and_the_default_fetcher_gets_the_plate(monkeypatch):
    shot = jd.ReportPage(status=200, title="License Plate Lookup", report_text="Enter a plate", path="form",
                         problem_status="form_failed", problem="RuntimeError: no field")
    record = run(fetcher=Recorder(shot))
    assert (record["lookup_status"], record["lookup_path"], record["error"]) == ("form_failed", "form", "RuntimeError: no field")
    assert run("ABC1234", "NY", Recorder(found_page(path="direct_url")))["lookup_path"] == "direct_url"
    seen = {}

    def fake(url, **kwargs):
        seen.update(url=url, **kwargs)
        return found_page()

    monkeypatch.setattr(jd, "fetch_report", fake)
    jd.lookup("zzz-1111", "tx", sleep=lambda seconds: None)
    assert (seen["plate"], seen["state"]) == ("ZZZ1111", "TX") and seen["url"] == jd.report_url("ZZZ1111", "TX")
