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
# Endo Health — Header Lab

Hey, I'm the one who built this little app. I wanted a fast way to generate clean header images for blog posts — either offline typographic headers with Pillow or illustrated headers via Gemini.

What it does
- Scrapes article titles from a blog listing.
- Summarizes an article (using a GenAI text model) and turns that into an image prompt.
- Generates an image with Gemini (preferred) or uses Pillow for a typographic fallback.
- Keeps UI and generated images on-brand by reading `color_pallete.txt` or using the built-in `endo` palette.

Where the code lives
- `src/generate.py`: scraping, summarization, prompt building, and image generation helpers.
- `src/app.py`: Streamlit UI — scrape → select → summarize → prompt → generate.
- `config.json`: palettes and prompt template.
- `color_pallete.txt`: optional palette overrides.

Tech stack
- Python 3.10+ (I use a Conda env)
- Streamlit for the UI
- google-genai (preferred) / google-generativeai (legacy fallback)
- requests + BeautifulSoup for scraping
- Pillow for image composition
- python-dotenv for local env vars

Quick run (Windows)

1) Install deps:

```powershell
F:\Conda\envs\endo\python.exe -m pip install -r requirements.txt
```

2) Set your Google API key (optional, for Gemini):

```powershell
:: Windows cmd
setx GOOGLE_API_KEY "YOUR_API_KEY"
# restart your shell to pick it up
```

3) Run the Streamlit app:

```powershell
F:\Conda\envs\endo\python.exe -m streamlit run "F:\Projects\Endo Health\src\app.py"
```

Notes and tips
- I prefer the modern `google-genai` client; the code falls back to the legacy client if needed.
- The app clamps image sizes to a safe max to avoid accidental quota spikes.
- OAuth helper files were removed — `GOOGLE_API_KEY` is the supported path now.

Want me to tidy further? I can:
- shorten remaining long comments, add unit tests for the prompt builder, or run a linter across the repo. Tell me which and I'll do it.
