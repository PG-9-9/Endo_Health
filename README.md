# Endo Health — Header Lab

Hey — I built this app to generate clean header images for blog posts using an AI image backend.

🌐 **Live Demo:** [http://project-demo.live/](http://project-demo.live/)

---

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
- **Docker** for containerization  
- **GitHub Actions** for CI/CD automation  
- **AWS EC2** for production deployment  

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

## ⚙️ CI/CD Pipeline Overview

The **Endo Health — Header Lab** app is continuously integrated and deployed using a lightweight CI/CD setup built on **Docker**, **GitHub Actions**, and **AWS EC2**.

### 🧩 1. Dockerization
- The app is containerized using a `Dockerfile` that defines dependencies, environment variables, and runtime.  
- The image includes Streamlit and all GenAI libraries for full reproducibility.  

### ⚙️ 2. GitHub Actions (CI/CD)
- Every push to `main` triggers a **GitHub Actions workflow**.  
- The workflow runs:
  - **Linting and testing**  
  - **Docker image build**  
  - **Push to AWS ECR**  
  - **Remote deployment trigger via SSH**  

### ☁️ 3. AWS EC2 Deployment
- The EC2 instance hosts a **Dockerized Streamlit service** exposed on port `80`.  
- GitHub Actions connects to EC2 using SSH secrets (`EC2_SSH_KEY`) to pull the latest image and restart the container automatically.  
- The latest deployed version is accessible at:  
  👉 **[http://project-demo.live/](http://project-demo.live/)**

This ensures seamless CI/CD automation — each commit leads to a tested, containerized, and live deployment without manual steps.

---
