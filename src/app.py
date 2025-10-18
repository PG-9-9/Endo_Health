import streamlit as st
from pathlib import Path
import tempfile
import os
from generate import scrape_titles_with_links, make_gemini_prompt, make_gemini_image, summarize_article_and_prompt, build_prompt_from_summary, get_theme

st.set_page_config(page_title="Endo Health-Header Lab", layout="wide")

st.title("Endo Health-Header Lab")

# Apply simplified palette at startup
CSS_SIMPLE = """
<style>
/* App background and base text */
[data-testid="stAppViewContainer"] { background: #FFFFFF !important; }
body, .stApp, .css-1d391kg { color: #000000 !important; }

/* Labels (field labels, form labels) should be readable on white background */
label, .stTextInput>label, .stNumberInput>label, .stSelectbox>label, .stForm>label {
    color: #212d3e !important;
}

/* Buttons and download buttons: base + hover + focus */
.stButton>button, .stDownloadButton>button {
    background-color: #A22A52 !important;
    border-color: #A22A52 !important;
    color: #ffffff !important;
    box-shadow: none !important;
}
.stButton>button:hover, .stDownloadButton>button:hover, .stButton>button:focus {
    background-color: #A22A52 !important;
    border-color: #A22A52 !important;
    color: #ffffff !important;
    filter: none !important;
}
.stButton>button:active, .stDownloadButton>button:active {
    background-color: #A22A52 !important;
}
.stButton>button[disabled], .stDownloadButton>button[disabled] {
    opacity: 0.6 !important;
}

/* Inputs and textareas: border and text color */
.stTextInput>div>div>input, .stTextArea>div>textarea, input, textarea {
    color: #B2B2B2 !important;
    border-color: #B2B2B2 !important;
    background: #FFFFFF !important;
}

/* Placeholder text (best-effort) */
input::placeholder, textarea::placeholder { color: #B2B2B2 !important; }

/* Select boxes and other interactive widgets (best-effort selectors) */
.stSelectbox>div, .stMultiSelect>div, .stNumberInput>div {
    color: #B2B2B2 !important;
}

/* Headings accent */
h1, h2, h3 { color: #A22A52 !important; }
</style>
"""
try:
    st.markdown(CSS_SIMPLE, unsafe_allow_html=True)
except Exception:
    pass

with st.form("scrape_form"):
    url = st.text_input("Blog URL to scrape", value="")
    limit = st.number_input("Max articles to fetch", value=10, min_value=1, max_value=50)
    submitted = st.form_submit_button("Scrape URL")
    # Ensure the scrape button follows the app accent color and hover state
    st.markdown(
        """
        <style>
        div[data-testid="stForm"] button { background-color: #A22A52 !important; border-color: #A22A52 !important; color: #fff !important; }
        div[data-testid="stForm"] button:hover { background-color: #A22A52 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

if 'articles' not in st.session_state:
    st.session_state['articles'] = []

if submitted and url:
    try:
        st.session_state['articles'] = scrape_titles_with_links(url, limit=limit)
        st.success(f"Found {len(st.session_state['articles'])} articles")
    except Exception as e:
        st.error(f"Failed to scrape URL: {e}")

articles = st.session_state['articles']

if articles:
    st.subheader("Articles")
    # ensure session state keys
    if 'selected_idx' not in st.session_state:
        st.session_state['selected_idx'] = 0
    if 'generated_prompt' not in st.session_state:
        st.session_state['generated_prompt'] = ''
    if 'generated_summary' not in st.session_state:
        st.session_state['generated_summary'] = ''

    cols = st.columns([4,1])
    # Create controls first so state updates happen before widgets are created
    with cols[1]:
        # Load theme palette to style UI
        try:
            theme = get_theme('endo')
        except Exception:
            theme = None

        # Inject minimal CSS based on theme colors (if available)
        if theme:
            bg0 = theme.bg[0] if theme.bg else '#FFFFFF'
            bg1 = theme.bg[-1] if len(theme.bg) > 0 else bg0
            accent = theme.accent or '#E91E63'
            text = theme.text or '#212121'
            css = f"""
            <style>
            [data-testid="stAppViewContainer"] {{ background: linear-gradient(180deg, {bg0}, {bg1}); }}
            .stButton>button, .stDownloadButton>button {{ background-color: {accent} !important; border-color: {accent} !important; color: #fff !important; }}
            .stButton>button:disabled, .stDownloadButton>button:disabled {{ opacity: 0.6 !important; }}
            h1, h2, h3 {{ color: {accent} !important; }}
            </style>
            """
            st.markdown(css, unsafe_allow_html=True)

        # Controls column: size + the three-step buttons stacked together for clear UX
        sel_size = st.text_input("Image size (WxH)", value="1024x576", key='sel_size')

        # Button: Create Summary (always enabled)
        if st.button("1 — Create summary for selected article", key='btn_summary'):
            try:
                article = articles[st.session_state['selected_idx']]
                article_url = article.get('url')
                summary, _ = summarize_article_and_prompt(article_url, article.get('title',''), api_key=os.environ.get('GOOGLE_API_KEY',''))
                st.session_state['generated_summary'] = summary
                # Clear any previously generated prompt so the user explicitly creates a prompt from the summary
                st.session_state['generated_prompt'] = ''
            except Exception as e:
                st.error(f"Failed to summarize article: {e}")

        # Button: Create Prompt (only shown/enabled after summary exists)
        if st.session_state.get('generated_summary'):
            if st.button("2 — Create prompt from summary", key='btn_prompt'):
                try:
                    article = articles[st.session_state['selected_idx']]
                    summary_text = st.session_state.get('generated_summary','')
                    prompt = build_prompt_from_summary(summary_text, article.get('title',''))
                    st.session_state['generated_prompt'] = prompt
                except Exception as e:
                    st.error(f"Failed to create prompt from summary: {e}")
        else:
            st.button("2 — Create prompt from summary", key='btn_prompt_disabled', disabled=True)

        # Button: Create Image (only shown/enabled after prompt exists)
        if st.session_state.get('generated_prompt'):
            if st.button("3 — Create image for selected article", key='btn_generate'):
                st.info("Generating image — Please wait :)")
                try:
                    # create out dir in temp and call make_gemini_image
                    tmp = Path(tempfile.gettempdir()) / "endo_gemini_out"
                    tmp.mkdir(parents=True, exist_ok=True)
                    # Use the theme loader by name 'endo' (which may be overridden by color_pallete.txt)
                    theme = get_theme('endo')
                    # Use the generated prompt as override when calling the image generator
                    prompt_override = st.session_state.get('generated_prompt') or None
                    w,h = tuple(map(int, sel_size.split('x')))
                    img = make_gemini_image(articles[st.session_state['selected_idx']]['title'], (w,h), theme, api_key=os.environ.get('GOOGLE_API_KEY','') or None, font_path=None, creds=None, prompt_override=prompt_override)
                    out_path = tmp / "last_gemini.png"
                    img.save(out_path, format="PNG")
                    # Save the prompt next to the image (private)
                    try:
                        prompt_file = tmp / "last_gemini_prompt.txt"
                        with open(prompt_file, "w", encoding="utf-8") as pf:
                            pf.write(st.session_state.get('generated_prompt',''))
                    except Exception:
                        pass
                    # Display the image (use width='stretch' per Streamlit API changes)
                    st.image(str(out_path), caption="Generated image", width='stretch')
                    st.success("Image generated")
                    # Provide download buttons for image and prompt
                    try:
                        with open(out_path, 'rb') as f:
                            img_bytes = f.read()
                        st.download_button("Download image", data=img_bytes, file_name="header_ai.png", mime="image/png")
                    except Exception:
                        pass
                    try:
                        st.download_button("Download prompt", data=st.session_state.get('generated_prompt',''), file_name="prompt.txt", mime="text/plain")
                    except Exception:
                        pass
                except Exception as e:
                    st.error(f"Image generation failed: {e}")
        else:
            st.button("3 — Create image for selected article", key='btn_generate_disabled', disabled=True)

    # Now render the main column (select + widgets) after controls to avoid session_state modification errors
    with cols[0]:
        # present articles by index with titles as labels
        sel_idx = st.selectbox("Select an article", options=list(range(len(articles))), format_func=lambda i: articles[i]['title'], index=st.session_state.get('selected_idx', 0), key='selected_idx')

        st.subheader("Article summary")
        # Bind the text areas to session_state via key only (no value) to avoid Streamlit warnings
        st.text_area("Summary", height=120, key='generated_summary')
        st.subheader("Generated prompt")
        st.text_area("Generated prompt", height=160, key='generated_prompt')