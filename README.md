# Auto Blog Header Generator (Endo-App mini challenge)

Generate on-brand header images for the latest blog posts automatically.

## Features
- Scrape the 10 most recent blog titles from a page (e.g. `https://endometriose.app/aktuelles-2/`).
- Generate clean, legible typographic headers **offline** with Pillow (no API needed).
- Optional: use **Gemini 2.5 Flash Image** (aka *Nano/Flash Banana*) for *illustrated* headers using one-line prompts.
- Pluggable backends, brand color palettes, smart text-fitting, and CSV input support.

## Quickstart (Typography-only, no API)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1) Scrape latest titles (or skip and use titles.csv)
python src/generate.py scrape --url https://endometriose.app/aktuelles-2/ --limit 10 --out data/titles.csv

# 2) Generate 1600x900 headers with the "endo" palette + soft gradient
python src/generate.py pillow --csv data/titles.csv --size 1600x900 --theme endo --out out/
```

## Optional: Gemini 2.5 Flash Image (aka "Flash/Nano Banana")
```bash
export GOOGLE_API_KEY=YOUR_KEY_HERE  # Windows PowerShell: $env:GOOGLE_API_KEY='YOUR_KEY_HERE'

# Generate AI-illustrated headers (keeps layout consistent and adds a footer bar with title overlay)
python src/generate.py gemini --csv data/titles.csv --size 1600x900 --theme endo --out out/
```
*You can tune the prompt template in `config.json`.*

## Project layout
```
.
├── assets/
├── data/
│   └── titles.csv            # created by the scraper (or you can hand-edit)
├── out/                      # generated headers
├── src/
│   └── generate.py           # CLI: scrape | pillow | gemini
├── config.json               # palettes & prompt templates
├── requirements.txt
└── README.md
```

## Notes
- The **Pillow** backend is the default and requires no network/API keys.
- The **Gemini** backend requires a Google API key. It turns each title into a consistent, minimal illustration using a brand-aware prompt, then overlays typography for legibility.
- For fonts: the script uses system sans-serif fallbacks. For best results, install an open font (e.g., Inter or Noto Sans) and pass `--font-path`.

## Example (one-liner)
```bash
python src/generate.py scrape --url https://endometriose.app/aktuelles-2/ --limit 10 --out data/titles.csv && python src/generate.py pillow --csv data/titles.csv --size 1600x900 --theme endo --out out/
```
