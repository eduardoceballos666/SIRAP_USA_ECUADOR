# SIRAP user manual / Manual de usuario de SIRAP

| | |
|---|---|
| 🇬🇧 English | [`SIRAP_Manual_EN.pdf`](SIRAP_Manual_EN.pdf) |
| 🇪🇸 Español | [`SIRAP_Manual_ES.pdf`](SIRAP_Manual_ES.pdf) |

Both PDFs have the same structure (preface, 15 chapters, 2 appendices) and cover the Ecuador and United States profiles: sign-in, the Recognition and Access screen, access results, the U.S. state + serial rules and two-frame confirmation, recording actions, History, Dashboard, Administration, About the model, phones and tablets, worked examples, troubleshooting and an operator checklist.
Ambos PDF tienen la misma estructura (prefacio, 15 capítulos, 2 apéndices) y cubren los perfiles de Ecuador y Estados Unidos.

## Screenshots / Capturas

`screenshots/en/` and `screenshots/es/` hold the images used by the manuals (the English and the Spanish interface). They were taken from a **test installation** with the sample photographs of `data/samples/`, fictitious users and generated DEMO operations — no real plates, people or operational records. The United States example is a composite: a license-plate crop pasted onto a sample scene, because the repository has no U.S. vehicle photograph. The vehicle details shown for the U.S. example are illustrative values, not a live J.D. Power answer.
The demo password is never printed in the manuals.

## Rebuild the PDFs / Regenerar los PDF

```bash
python -m pip install playwright pypdf
python -m playwright install chromium
python docs/manual/build_manual.py          # both languages
python docs/manual/build_manual.py en       # only English
```

The text lives in `manual_content.py` (chapters 1–6) and `manual_content2.py` (chapters 7–15 and appendices) as *(English, Spanish)* pairs, so both manuals stay aligned. `build_manual.py` renders HTML with Chromium and numbers the table of contents from the printed PDF.
Retake screenshots after a UI change and overwrite the files in `screenshots/<lang>/` before rebuilding.
