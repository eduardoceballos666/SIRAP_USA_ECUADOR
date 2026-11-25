# SIRAP user manual / Manual de usuario de SIRAP

| | |
|---|---|
| 🇬🇧 English | [`SIRAP_Manual_EN.pdf`](SIRAP_Manual_EN.pdf) |
| 🇪🇸 Español | [`SIRAP_Manual_ES.pdf`](SIRAP_Manual_ES.pdf) |

Both PDFs have the same structure (preface, 15 chapters, 2 appendices) and cover the Ecuador and United States of America profiles: sign-in (including the default United States of America profile and the country flags), the Recognition and Access screen, access results, the U.S. state + serial rules, two-frame confirmation and the J.D. Power vehicle button, recording actions, History, Dashboard, Administration, About the model, phones and tablets, worked examples, troubleshooting and an operator checklist.
Ambos PDF tienen la misma estructura (prefacio, 15 capítulos, 2 apéndices) y cubren los perfiles de Ecuador y Estados Unidos de América.

## Screenshots / Capturas

`screenshots/en/` and `screenshots/es/` hold the images used by the manuals (the English and the Spanish interface). They were taken from a **test installation** with the sample photographs of `data/samples/`, fictitious users, fictitious U.S. vehicles and generated DEMO operations — no real plates, people or operational records.
Illustrative parts (the manuals say so in "About the screenshots"):

- **U.S. recognition screens** (`31_usa_recognition`, `32_usa_first_frame`, `33_usa_confirmed`, `36_usa_vehicle_button`): the plate model is not distributed with the code, so only the *reading response* of `/api/recognize` was simulated (plate `KDM4827`, state TX, 1/2 then 2/2 frames). The rest of the screen — login, registry, lists, buttons — is the real application running against a scratch data folder. The scene is `data/samples/garita1_GSA-1234.jpg` with an **original plate drawn for this guide** by [`make_usa_demo_scene.py`](make_usa_demo_scene.py); no third-party plate image is used.
- **Vehicle details (U.S.)**: the panel only holds the *See Vehicle Details on J.D. Power* button, which opens J.D. Power's public page in a new tab. The J.D. Power page itself is not reproduced.
- **Ecuador screens** (`02`–`21`, `23`) were taken before the country flags (left menu, control bar, login) were added and are unchanged. The login screens (`01`, `22`, `30`) and the U.S. recognition, history and dashboard screens (`31`–`36`) were retaken with the current interface.

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
