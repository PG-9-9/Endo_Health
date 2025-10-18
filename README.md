# Endo Health — Header Lab

Hey — I built this app to generate clean header images for blog posts using an AI image backend.

## 🧩 Key Features
- Scrapes article titles from a blog listing and summarizes them using a GenAI text model.
- Builds concise image prompts from the summaries and generates visuals using the Gemini image backend (no Pillow dependency).
- Adjustable number of articles to fetch via the UI.
- On-brand palette support via `color_pallete.txt` or the built-in `endo` theme.

---

## ⚙️ Workflow Overview

1. **Scrape** — Provide a blog listing URL and choose how many titles to fetch.  
2. **Select** — Pick an article from the scraped list.  
3. **Summarize** — Generate a 2–3 sentence summary using the text model.  
4. **Prompt** — Convert the summary into an image prompt.  
5. **Generate** — Create the image using the AI model, then download both the image and the prompt.

---

## 🧭 UI Flow (How to Use)

1. Start the app and paste a blog listing URL into **"Blog URL to scrape"**.  
2. Set **"Max articles to fetch"** — the number is flexible.  
3. Click **Scrape URL** → The list appears on the left panel.  
4. Select an article → Click **1 — Create summary for selected article**.  
5. Click **2 — Create prompt from summary**.  
6. Click **3 — Create image for selected article** → View and download results.

---

## 🗂️ Code Structure

| File | Description |
|------|--------------|
| `src/generate.py` | Handles scraping, summarization, prompt building, and image generation. |
| `src/app.py` | Streamlit UI and event flow. |
| `config.json` | Stores palettes & prompt templates. |
| `color_pallete.txt` | Optional palette overrides. |
| `environment.yml` | Conda environment specification. |

---

## 🧱 Tech Stack

- **Python** 3.10+  
- **Streamlit** for UI  
- **google-genai** (modern client)  
- **requests**, **BeautifulSoup**, **python-dotenv**

---

## 🚀 Quickstart (Conda)

### 1️⃣ Create Environment

```bash
conda env create -f environment.yml
conda activate endo
```

### 2️⃣ Set Google API Key

```bash
# Windows PowerShell
setx GOOGLE_API_KEY "YOUR_API_KEY"
# Restart your shell or IDE afterward
```

### 3️⃣ Run the Streamlit App

```bash
python -m streamlit run src/app.py
```

---

## 🧾 Notes

- Focuses solely on the **AI image backend** — Pillow generation removed.  
- No internal model versions are hardcoded. You can override via `GEMINI_MODEL` env var.  
- Image sizes are clamped to a safe maximum to avoid excessive quota usage.

---


