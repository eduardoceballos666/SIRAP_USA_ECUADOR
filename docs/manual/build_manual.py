#!/usr/bin/env python3
"""Build the SIRAP user manual as two PDFs (English and Spanish) from one bilingual source.

    python docs/manual/build_manual.py            # writes SIRAP_Manual_EN.pdf and SIRAP_Manual_ES.pdf here
    python docs/manual/build_manual.py en         # only one language

Requirements: ``playwright`` with Chromium (``python -m playwright install chromium``) and ``pypdf``.
The text lives in ``manual_content.py`` as (English, Spanish) pairs, so both manuals always have the same
structure. Screenshots are read from ``docs/manual/screenshots/<lang>/``.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
SHOTS = HERE / "screenshots"
LANGS = {"en": 0, "es": 1}
OUTPUT = {"en": "SIRAP_Manual_EN.pdf", "es": "SIRAP_Manual_ES.pdf"}

UI = {
    "title": ("SIRAP User Manual", "Manual de usuario de SIRAP"),
    "footer": ("SIRAP · User Manual · Ecuador and United States of America", "SIRAP · Manual de usuario · Ecuador y Estados Unidos de América"),
    "toc": ("Contents", "Contenido"),
    "figure": ("Figure", "Figura"),
    "table": ("Table", "Tabla"),
    "html_lang": ("en", "es"),
}

CSS = r"""
:root{--navy:#0d1b33;--navy2:#13264a;--brand:#2156e8;--yellow:#f7b900;--ink:#17233b;--muted:#5a6785;--line:#d9dfeb;--soft:#f3f6fb;
--ok:#16a34a;--bad:#dc1f26;--warn:#c98700}
@page{size:A4;margin:20mm 16mm 22mm 16mm;
 @bottom-left{content:string(footer);font:8pt Inter,sans-serif;color:#7a869f}
 @bottom-right{content:counter(page);font:8.5pt Inter,sans-serif;color:#7a869f}}
@page cover{margin:0;@bottom-left{content:none}@bottom-right{content:none}}
*{box-sizing:border-box}
html{font-family:Inter,"Helvetica Neue",Arial,sans-serif;color:var(--ink);font-size:10pt;line-height:1.5;
 -webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0}
h1,h2,h3{color:var(--navy);line-height:1.2;margin:0}
h1{font-size:21pt;font-weight:800;break-before:page;padding:0 0 3mm;margin-bottom:6mm;border-bottom:3px solid var(--yellow)}
h1 .num{color:var(--brand);margin-right:3mm}
h2{font-size:13.5pt;font-weight:750;margin:7mm 0 2.5mm;break-after:avoid}
h3{font-size:11pt;font-weight:700;margin:5mm 0 1.5mm;break-after:avoid}
p{margin:0 0 3mm;orphans:3;widows:3}
ul,ol{margin:0 0 3.5mm;padding-left:6mm}
li{margin:0 0 1.4mm}
code{font-family:"DejaVu Sans Mono",monospace;font-size:8.6pt;background:#eef2fa;border-radius:3px;padding:.2mm 1.2mm}
a{color:var(--brand);text-decoration:none}
/* cover */
.cover{page:cover;height:297mm;width:210mm;background:linear-gradient(160deg,#0a1529 0%,#0d1b33 55%,#13264a 100%);color:#fff;
 padding:34mm 24mm 22mm;position:relative;break-after:page;overflow:hidden}
.cover .logo{display:inline-block;position:relative;padding:5mm 9mm;margin:3mm}
.cover .logo b{display:block;background:var(--yellow);color:#000;font-weight:900;font-size:44pt;letter-spacing:1pt;border-radius:7mm;
 padding:1mm 9mm;border:2.2px solid #000;line-height:1.25}
.cover .logo i{position:absolute;width:9mm;height:9mm;border:3px solid #fff}
.cover .logo i:nth-child(1){left:0;top:0;border-right:0;border-bottom:0}
.cover .logo i:nth-child(2){right:0;top:0;border-left:0;border-bottom:0}
.cover .logo i:nth-child(3){left:0;bottom:0;border-right:0;border-top:0}
.cover .logo i:nth-child(4){right:0;bottom:0;border-left:0;border-top:0}
.cover h1{color:#fff;border:0;font-size:38pt;margin:20mm 0 3mm;padding:0;break-before:auto}
.cover .sub{font-size:14pt;color:#cdd7ee;max-width:140mm}
.cover .chips{margin-top:12mm}
.cover .chips span{display:inline-block;border:1.5px solid var(--yellow);color:var(--yellow);border-radius:20mm;padding:1.6mm 6mm;
 font-weight:700;font-size:11pt;margin-right:4mm}
.cover .meta{position:absolute;left:24mm;right:24mm;bottom:22mm;color:#aebbd8;font-size:9.5pt;line-height:1.6;
 border-top:1px solid #2a3d63;padding-top:5mm}
.cover .meta b{color:#fff}
/* toc */
.toc{break-after:page}
.toc h1{break-before:auto}
.toc ol{list-style:none;padding:0;margin:0}
.toc li{display:flex;align-items:baseline;gap:2mm;margin:0;padding:.9mm 0}
.toc li .t{flex:0 1 auto}
.toc li .d{flex:1 1 auto;border-bottom:1px dotted #9aa6c0;transform:translateY(-1.2mm);min-width:6mm}
.toc li .p{flex:0 0 auto;font-variant-numeric:tabular-nums;color:var(--muted)}
.toc li.l1{margin-top:2.2mm;font-weight:750;color:var(--navy)}
.toc li.l2{padding-left:7mm;font-size:9.4pt}
.toc a{color:inherit}
/* tables */
table{width:100%;border-collapse:collapse;margin:1mm 0 1mm;font-size:8.9pt;break-inside:auto}
thead th{background:var(--navy);color:#fff;text-align:left;font-weight:700;padding:2mm 2.6mm;font-size:8.4pt;letter-spacing:.2pt}
tbody td{padding:1.9mm 2.6mm;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:nth-child(even) td{background:var(--soft)}
tr{break-inside:avoid}
td:first-child{font-weight:650}
.cap{font-size:8.4pt;color:var(--muted);margin:1.2mm 0 5mm;font-style:italic;break-before:avoid}
.tw.short{break-inside:avoid}
/* callouts */
.note{border-left:4px solid var(--brand);background:#eef3ff;border-radius:0 5px 5px 0;padding:2.6mm 4mm;margin:3mm 0 4mm;break-inside:avoid}
.note .nt{font-weight:800;font-size:8.6pt;letter-spacing:.5pt;text-transform:uppercase;color:var(--brand);margin-bottom:.6mm}
.note p:last-child{margin-bottom:0}
.note.warn{border-color:var(--yellow);background:#fff7de}.note.warn .nt{color:#9a6b00}
.note.danger{border-color:var(--bad);background:#fdeeed}.note.danger .nt{color:var(--bad)}
.note.ok{border-color:var(--ok);background:#eafaf0}.note.ok .nt{color:#0f7a37}
/* figures */
figure{margin:3mm 0 5mm;break-inside:avoid;text-align:center}
figure img{width:91%;margin:0 auto;border:1px solid var(--line);border-radius:5px;box-shadow:0 1px 5px rgba(13,27,51,.12);display:block}
figure.narrow img{width:56%;margin:0 auto}
figcaption{font-size:8.4pt;color:var(--muted);margin:1.8mm 4.5% 0;font-style:italic;text-align:left}
figure.pair{display:flex;gap:8mm;justify-content:center;align-items:flex-start;flex-wrap:wrap}
figure.pair .it{flex:0 0 58mm;text-align:left}
figure.pair .it img{width:100%;margin:0}
figure.pair figcaption{margin:1.8mm 0 0}
.steps{counter-reset:s;list-style:none;padding:0}
.steps li{counter-increment:s;position:relative;padding-left:9mm;min-height:6mm;margin-bottom:2mm}
.steps li::before{content:counter(s);position:absolute;left:0;top:.1mm;width:6mm;height:6mm;border-radius:50%;background:var(--brand);color:#fff;
 font-weight:800;font-size:8.4pt;text-align:center;line-height:6mm}
.kv{display:grid;grid-template-columns:34mm 1fr;gap:1mm 4mm;font-size:9.4pt}
.kv dt{font-weight:700;color:var(--navy)}.kv dd{margin:0}
.checklist{list-style:none;padding:0}.checklist li{padding-left:7mm;position:relative}
.checklist li::before{content:"";position:absolute;left:0;top:1.2mm;width:3.6mm;height:3.6mm;border:1.4px solid var(--brand);border-radius:1mm}
"""


class Doc:
    def __init__(self, lang: str):
        self.lang, self.i = lang, LANGS[lang]
        self.body: list[str] = []
        self.toc: list[tuple[int, str, str]] = []  # (level, id, label)
        self.h1n = 0
        self.fig_n = 0
        self.tab_n = 0
        self.uid = 0

    # ---- helpers
    def t(self, v) -> str:
        """Pick the language version; a plain string is language-neutral."""
        return v[self.i] if isinstance(v, (tuple, list)) else v

    def add(self, s: str) -> None:
        self.body.append(s)

    # ---- blocks
    def h1(self, en, es):
        self.h1n += 1
        label = self.t((en, es))
        self.uid += 1
        hid = f"c{self.h1n}"
        self.toc.append((1, hid, f"{self.h1n}. {label}"))
        self.add(f'<h1 id="{hid}"><span class="num">{self.h1n}.</span>{label}</h1>')
        self.h2n = 0

    def h1_plain(self, en, es, label_prefix=""):
        """Unnumbered chapter (appendices)."""
        label = self.t((en, es))
        self.uid += 1
        hid = f"a{self.uid}"
        self.toc.append((1, hid, f"{label_prefix}{label}"))
        self.add(f'<h1 id="{hid}">{html.escape(label_prefix)}{label}</h1>')
        self.h2n = 0

    def h2(self, en, es):
        self.h2n += 1
        label = self.t((en, es))
        hid = f"c{self.h1n}-{self.h2n}"
        full = f"{self.h1n}.{self.h2n} {label}" if self.h1n else label
        self.toc.append((2, hid, full))
        self.add(f'<h2 id="{hid}">{self.h1n}.{self.h2n} {label}</h2>' if self.h1n else f'<h2 id="{hid}">{label}</h2>')

    def h3(self, en, es):
        self.add(f"<h3>{self.t((en, es))}</h3>")

    def p(self, en, es):
        self.add(f"<p>{self.t((en, es))}</p>")

    def ul(self, items):
        self.add("<ul>" + "".join(f"<li>{self.t(x)}</li>" for x in items) + "</ul>")

    def steps(self, items):
        self.add('<ol class="steps">' + "".join(f"<li>{self.t(x)}</li>" for x in items) + "</ol>")

    def checklist(self, items):
        self.add('<ul class="checklist">' + "".join(f"<li>{self.t(x)}</li>" for x in items) + "</ul>")

    def note(self, kind, title, en, es):
        self.add(f'<div class="note {kind}"><div class="nt">{self.t(title)}</div><p>{self.t((en, es))}</p></div>')

    def table(self, head, rows, caption=None, widths=None):
        self.tab_n += 1
        cols = ""
        if widths:
            cols = "<colgroup>" + "".join(f'<col style="width:{w}%">' for w in widths) + "</colgroup>"
        th = "".join(f"<th>{self.t(h)}</th>" for h in head)
        body = "".join("<tr>" + "".join(f"<td>{self.t(c)}</td>" for c in r) + "</tr>" for r in rows)
        cap = f'<p class="cap">{self.t(("Table", "Tabla"))} {self.tab_n}. {self.t(caption)}</p>' if caption else ""
        kind = "short" if len(rows) <= 9 else "long"  # short tables are never split across pages
        self.add(f'<div class="tw {kind}"><table>{cols}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>{cap}</div>')

    def fig(self, name, en, es, narrow=False):
        self.fig_n += 1
        path = SHOTS / self.lang / f"{name}.png"
        assert path.exists(), path
        cls = ' class="narrow"' if narrow else ""
        self.add(
            f'<figure{cls}><img src="{path.as_uri()}" alt=""><figcaption>{self.t(("Figure", "Figura"))} {self.fig_n}. '
            f"{self.t((en, es))}</figcaption></figure>"
        )

    def pair(self, a, cap_a, b, cap_b):
        items = []
        for name, cap in ((a, cap_a), (b, cap_b)):
            self.fig_n += 1
            path = SHOTS / self.lang / f"{name}.png"
            assert path.exists(), path
            items.append(
                f'<div class="it"><img src="{path.as_uri()}" alt=""><figcaption>{self.t(("Figure", "Figura"))} {self.fig_n}. '
                f"{self.t(cap)}</figcaption></div>"
            )
        self.add('<figure class="pair">' + "".join(items) + "</figure>")

    def raw(self, s):
        self.add(s)


def cover(d: Doc) -> str:
    L = d.t
    return f"""
<section class="cover">
  <div class="logo"><i></i><i></i><i></i><i></i><b>SIRAP</b></div>
  <h1>{L(UI['title'])}</h1>
  <div class="sub">{L(("Automatic License Plate Detection and Recognition System for vehicle access control.",
                       "Sistema de Detección y Reconocimiento Automático de Placas para el control de acceso vehicular."))}</div>
  <div class="chips"><span>Ecuador</span><span>{L(("United States of America", "Estados Unidos de América"))}</span></div>
  <div class="meta">
    <div><b>{L(("Version", "Versión"))}:</b> {L(("November 2026", "Noviembre de 2026"))} · {L(("Web application (Vue 3 + FastAPI)", "Aplicación web (Vue 3 + FastAPI)"))}</div>
    <div><b>{L(("Application", "Aplicación"))}:</b> https://eduardoceballos-sirap-usa-ecuador-hf.hf.space</div>
    <div><b>{L(("Source code", "Código fuente"))}:</b> github.com/eduardoceballos666/SIRAP_USA_ECUADOR · Apache-2.0</div>
    <div><b>{L(("Authors", "Autores"))}:</b> Eduardo Alejandro Ceballos Jijón · Christian Xavier Valle Marideña</div>
  </div>
</section>"""


def toc_html(d: Doc, pages: dict[str, int]) -> str:
    rows = []
    for level, hid, label in d.toc:
        pg = pages.get(hid, "")
        rows.append(
            f'<li class="l{level}"><a class="t" href="#{hid}">{label}</a><span class="d"></span><span class="p">{pg}</span></li>'
        )
    return f'<section class="toc"><h1>{d.t(UI["toc"])}</h1><ol>' + "".join(rows) + "</ol></section>"


def render(lang: str, pages: dict[str, int] | None = None) -> tuple[str, Doc]:
    import manual_content

    d = Doc(lang)
    manual_content.build(d)
    pages = pages or {}
    doc = (
        f'<!doctype html><html lang="{UI["html_lang"][d.i]}"><head><meta charset="utf-8"><title>{d.t(UI["title"])}</title>'
        f"<style>{CSS.replace('string(footer)', chr(34) + d.t(UI['footer']) + chr(34))}</style></head><body>"
        + cover(d)
        + toc_html(d, pages)
        + "".join(d.body)
        + "</body></html>"
    )
    return doc, d


def write_pdf(html_text: str, out: Path) -> None:
    tmp = out.with_suffix(".html")
    tmp.write_text(html_text, encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(tmp.as_uri())
        page.wait_for_load_state("load")
        page.evaluate("document.fonts.ready")
        page.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True, outline=True, tagged=True)
        browser.close()
    tmp.unlink()


def find_pages(pdf: Path, d: Doc) -> dict[str, int]:
    """Physical page number (cover = 1) where each heading appears, ignoring the contents pages."""
    reader = PdfReader(str(pdf))
    def norm(text: str) -> str:
        # PDF text extraction drops hyphens/parentheses and glues numbers to titles, so compare letters and digits only
        return re.sub(r"[^0-9A-Za-zÀ-ÿ]", "", text)

    texts = [norm(pg.extract_text() or "") for pg in reader.pages]
    labels = [(hid, norm(label)) for _, hid, label in d.toc]
    toc_last = 0
    for i in range(1, len(texts)):
        if sum(1 for _, lab in labels if lab in texts[i]) >= 8:  # contents pages list many headings at once
            toc_last = i
        elif toc_last:
            break
    pages: dict[str, int] = {}
    for hid, lab in labels:
        for i in range(toc_last + 1, len(texts)):
            if lab in texts[i]:
                pages[hid] = i + 1
                break
    return pages


def build(lang: str) -> Path:
    out = HERE / OUTPUT[lang]
    first, d = render(lang)
    write_pdf(first, out)
    pages = find_pages(out, d)
    second, d = render(lang, pages)
    write_pdf(second, out)
    check = find_pages(out, d)
    if check != pages:
        write_pdf(render(lang, check)[0], out)
    missing = [lab for _, hid, lab in d.toc if hid not in pages]
    print(f"{out.name}: {len(PdfReader(str(out)).pages)} pages, {len(d.toc)} headings, missing={missing}")
    return out


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    for lg in (sys.argv[1:] or ["en", "es"]):
        build(lg)
