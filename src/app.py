import streamlit as st
from pathlib import Path
import tempfile
import os
from generate import scrape_titles, make_gemini_prompt, make_gemini_image

st.set_page_config(page_title="Endo Health — Gemini Header Generator", layout="wide")

st.title("Endo Health — Gemini Header Generator")

with st.form("scrape_form"):
    url = st.text_input("Blog URL to scrape", value="")
    limit = st.number_input("Max articles to fetch", value=10, min_value=1, max_value=50)
    submitted = st.form_submit_button("Scrape URL")

titles = []
if submitted and url:
    try:
        titles = scrape_titles(url, limit=limit)
        st.success(f"Found {len(titles)} articles")
    except Exception as e:
        st.error(f"Failed to scrape URL: {e}")

if titles:
    st.subheader("Articles")
    cols = st.columns([4,1])
    with cols[0]:
        sel = st.selectbox("Select an article", options=titles)
    with cols[1]:
        if st.button("Create prompt for selected article"):
            prompt = make_gemini_prompt(sel)
            st.text_area("Generated prompt", value=prompt, height=160)

    st.markdown("---")
    st.subheader("Generate image")
    sel_size = st.text_input("Image size (WxH)", value="1024x576")
    api_key = st.text_input("GOOGLE_API_KEY (optional)", value=os.environ.get("GOOGLE_API_KEY",""))
    generate = st.button("Create image for selected article")

    if generate:
        st.info("Generating image — this will make one Gemini API request (may use your API key / credentials).")
        try:
            # create out dir in temp and call make_gemini_image
            tmp = Path(tempfile.gettempdir()) / "endo_gemini_out"
            tmp.mkdir(parents=True, exist_ok=True)
            theme = None
            # fallback theme: use the default theme loader by name 'endo'
            from generate import get_theme
            theme = get_theme('endo')
            img = make_gemini_image(sel, tuple(map(int, sel_size.split('x'))), theme, api_key=api_key or None, font_path=None, creds=None)
            out_path = tmp / "last_gemini.png"
            img.save(out_path, format="PNG")
            st.image(str(out_path), caption="Generated image", use_column_width=True)
            st.success(f"Saved to {out_path}")
        except Exception as e:
            st.error(f"Image generation failed: {e}")