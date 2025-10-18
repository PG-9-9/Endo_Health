# Endo Health — Header Lab

Hey — I built this app to generate clean header images for blog posts using an AI image backend.

Key points
- The UI scrapes article titles from a listing and lets you summarize an article, build an image prompt from that summary, and generate an image using the AI image backend (Gemini via the modern client). The repo no longer uses Pillow for generation.
- The number of articles to fetch is adjustable in the UI via "Max articles to fetch".

What it does (workflow)
- Scrape: provide a blog listing URL and choose how many titles to fetch.
- Select: pick an article from the scraped list.
- Summarize: create a 2–3 sentence summary of the article using the text model.
- Prompt: convert the summary into a concise image prompt.
- Generate: create the image using the AI image model and download the image and prompt.

UI flow (how to use)
1. Start the app and paste a blog listing URL into the "Blog URL to scrape" field. Set "Max articles to fetch" to how many titles you want (the number is not fixed).
2. Click "Scrape URL". The article list appears in the left column.
3. Select an article from the drop-down.
4. Click "1 — Create summary for selected article" to generate a short summary.
5. Click "2 — Create prompt from summary" to make the image prompt.
6. Click "3 — Create image for selected article" to generate and view the image. Download buttons are provided for image and prompt.

Where the code lives
- `src/generate.py`: scraping, summarization, prompt building, and image generation.
- `src/app.py`: Streamlit UI and event flow.
- `config.json`: palettes & prompt template.
- `color_pallete.txt`: optional palette overrides.
- `environment.yml`: conda environment specification.

Stack
- Python 3.10+
- Streamlit
- google-genai (modern client)
- requests, BeautifulSoup, python-dotenv

Quickstart (Conda)
1) Create the conda env from the provided YAML:

```powershell
conda env create -f environment.yml
conda activate endo
```

2) Set your `GOOGLE_API_KEY` (required to generate images):

```powershell
setx GOOGLE_API_KEY "YOUR_API_KEY"
# restart your shell/IDE to pick it up
```

3) Run the Streamlit app:

```powershell
python -m streamlit run src/app.py
```

Notes
- The repo focuses on the AI image backend only; Pillow generation has been removed.
- The README avoids mentioning specific internal model versions; set a different model via the `GEMINI_MODEL` env var if needed.
- The app clamps image sizes to a safe maximum to reduce accidental quota usage.

If you'd like, I can:
- add a tiny test for the prompt builder, run a linter, or remove any remaining Pillow references from code and docs.

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

