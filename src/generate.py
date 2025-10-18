
import argparse, csv, os, re, random, math, io, json, textwrap, sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional
from dotenv import load_dotenv
load_dotenv()


# scraping
import requests
from bs4 import BeautifulSoup

# imaging
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# optional: Gemini - prefer modern `google.genai` client but keep older client available
try:
    from google import genai as genai_mod
except Exception:
    genai_mod = None

try:
    import google.generativeai as genai_old
except Exception:
    genai_old = None

# If a local helper for obtaining OAuth creds exists (load_creds.py at repo root),
# try to load credentials and configure clients where possible so image generation can use OAuth.
try:
    import sys
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root))
    try:
        from load_creds import load_creds
    except Exception:
        load_creds = None

    creds = None
    if load_creds:
        try:
            creds = load_creds()
            # configure older client if present
            if creds and genai_old:
                try:
                    genai_old.configure(credentials=creds)
                except Exception:
                    pass
            # export token for REST fallback or new client use
            if creds and getattr(creds, 'token', None):
                os.environ.setdefault('GOOGLE_OAUTH_BEARER', creds.token)
        except Exception:
            pass
except Exception:
    pass

HERE = Path(__file__).resolve().parent.parent
CONFIG = json.loads(open(HERE / "config.json", "r", encoding="utf-8").read())

# ---------------------------
# Utilities
# ---------------------------

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def parse_size(s: str) -> Tuple[int,int]:
    try:
        w,h = s.lower().split("x")
        return int(w), int(h)
    except Exception:
        raise ValueError("Size must look like WIDTHxHEIGHT, e.g. 1600x900")

def load_font(font_path: Optional[str], size: int) -> ImageFont.FreeTypeFont:
    if font_path and Path(font_path).exists():
        return ImageFont.truetype(font_path, size=size)
    # fallback: PIL default
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except Exception:
        return ImageFont.load_default()

def wrap_text_to_box(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    words = text.split()
    lines = []
    current = []
    for w in words:
        test = " ".join(current+[w])
        bbox = draw.textbbox((0,0), test, font=font)
        if bbox[2]-bbox[0] <= max_width:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
                current = [w]
            else:
                lines.append(w)
                current = []
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)

def draw_gradient(size: Tuple[int,int], colors: List[str]) -> Image.Image:
    w,h = size
    base = Image.new("RGB", (w,h), colors[0])
    top = Image.new("RGB", (w,h), colors[-1])
    mask = Image.linear_gradient("L").resize((w,h)).filter(ImageFilter.GaussianBlur(radius=64))
    return Image.composite(top, base, mask)

def add_soft_shapes(img: Image.Image, accent_hex: str):
    """Draw a couple of soft blobs and arcs for visual interest."""
    draw = ImageDraw.Draw(img, "RGBA")
    w,h = img.size
    def hex_to_rgba(hx, a=40):
        hx = hx.lstrip("#")
        r = int(hx[0:2],16); g=int(hx[2:4],16); b=int(hx[4:6],16)
        return (r,g,b,a)
    # off-canvas circles
    for i in range(3):
        r = random.randint(int(h*0.25), int(h*0.45))
        cx = random.randint(-int(w*0.2), int(w*1.2))
        cy = random.randint(-int(h*0.2), int(h*1.2))
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=hex_to_rgba(accent_hex, a=30))
    return img

def overlay_text(img: Image.Image, title: str, palette: dict, font_path: Optional[str]=None):
    w,h = img.size
    draw = ImageDraw.Draw(img)
    # footer bar for legibility
    footer_h = int(h*0.28)
    bar = Image.new("RGBA", (w, footer_h), (0,0,0,90))
    img.paste(bar, (0, h-footer_h), bar)

    title_font = load_font(font_path, size=int(h*0.065))
    subtitle_font = load_font(font_path, size=int(h*0.03))

    padding = int(0.06*w)
    max_text_w = int(w*0.88)

    wrapped = wrap_text_to_box(draw, title, title_font, max_text_w)
    # Adjust font down until it fits in the footer bar if needed
    while True:
        bbox = draw.multiline_textbbox((padding, h-footer_h+padding//2), wrapped, font=title_font, spacing=int(h*0.01))
        if bbox[3] <= h - padding//2:
            break
        size = max(18, title_font.size - 2)
        title_font = load_font(font_path, size)

    draw.multiline_text((padding, h-footer_h+padding//2), wrapped, fill=palette["text"], font=title_font, spacing=int(h*0.01))

    # small brand line
    sub = "Endo‑Blog • endometriose.app"
    bbox = draw.textbbox((0, 0), sub, font=subtitle_font)
    sub_w, sub_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    draw.text((padding, h - sub_h - int(padding*0.4)), sub, fill=palette["subtext"], font=subtitle_font)

    # accent pill
    pill_w = min(220, int(w*0.18)); pill_h = int(sub_h*1.6)
    pill = Image.new("RGBA", (pill_w, pill_h), (0,0,0,0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle((0,0,pill_w,pill_h), radius=int(pill_h/2), fill=palette["accent"])
    pd.text((int(pill_w*0.1), int(pill_h*0.17)), "WISSEN & TIPPS", font=subtitle_font, fill="#000000")
    img.paste(pill, (w - pill_w - padding, h - pill_h - int(padding*0.45)), pill)
    return img

# ---------------------------
# Scraper
# ---------------------------

def scrape_titles(url: str, limit: int=10) -> List[str]:
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    # Heuristic: headlines within the blog listing are H3 (###) links
    titles = []
    for h3 in soup.find_all(["h2","h3","h4"]):
        a = h3.find("a")
        t = (a.get_text(strip=True) if a else h3.get_text(strip=True))
        if not t or len(t) < 5: 
            continue
        # skip boilerplate duplicates & buttons
        if any(x in t.lower() for x in ["weiterlesen", "read more", "news", "blog", "menu"]):
            continue
        titles.append(t)
        if len(titles) >= limit:
            break
    return titles

# ---------------------------
# Backends
# ---------------------------

@dataclass
class Theme:
    bg: List[str]
    accent: str
    text: str
    subtext: str

def get_theme(name: str) -> Theme:
    pal = CONFIG["palettes"].get(name, CONFIG["palettes"]["endo"])
    return Theme(bg=pal["bg"], accent=pal["accent"], text=pal["text"], subtext=pal["subtext"])

def make_pillow(title: str, size: Tuple[int,int], theme: Theme, font_path: Optional[str]) -> Image.Image:
    img = draw_gradient(size, theme.bg)
    img = add_soft_shapes(img, theme.accent)
    # pass through dict for overlay_text
    palette = {"accent": theme.accent, "text": theme.text, "subtext": theme.subtext}
    img = overlay_text(img, title, palette, font_path=font_path)
    return img

def make_gemini_prompt(title: str) -> str:
    tmpl = CONFIG["prompt_template"]
    return tmpl.format(title=title, accent_desc=CONFIG.get("accent_desc","a soft yellow"))

def make_gemini_image(title: str, size: Tuple[int,int], theme: Theme, api_key: Optional[str], font_path: Optional[str], creds: Optional[object]=None) -> Image.Image:
    # prefer the modern google.genai client
    api_key_env = api_key or os.environ.get("GOOGLE_API_KEY")
    # Enforce conservative defaults to avoid hitting quota/token limits.
    # Clamp requested dimensions to a maximum of 1024x1024.
    max_dim = 1024
    W = min(size[0], max_dim)
    H = min(size[1], max_dim)
    size = (W, H)

    # Use new genai client if present
    if genai_mod is not None:
        # Initialize client with either credentials or api_key (mutually exclusive)
        if creds:
            client = genai_mod.Client(credentials=creds)
        elif api_key_env:
            client = genai_mod.Client(api_key=api_key_env)
        else:
            raise RuntimeError("No api_key or credentials available for genai client")

        prompt = make_gemini_prompt(title)
        # Print the prompt used to generate the image for transparency/debugging
        print("Gemini prompt:\n", prompt)

        # Default to the Gemini image model unless overridden by GEMINI_MODEL
        model_name = os.environ.get("GEMINI_MODEL", "models/gemini-2.5-flash-image")
        # Some models accept a size hint; include it in the prompt as a soft instruction.
        prompt_with_size = prompt + f"\n(SizeHint: {size[0]}x{size[1]})"
        try:
            resp = client.models.generate_content(model=model_name, contents=[prompt_with_size])
        except Exception as e:
            serr = str(e)
            if "RESOURCE_EXHAUSTED" in serr or "quota" in serr.lower() or "429" in serr:
                print("\nGemini API returned RESOURCE_EXHAUSTED (quota exceeded).\n")
                print("Possible fixes:")
                print(" - Enable billing and check quotas in Google Cloud Console for the project used by your OAuth credentials.")
                print(" - Request a quota increase or use a different model that you have access to.")
                print(" - Use a different account/project with available quota.")
                print("To continue: enable billing at https://console.cloud.google.com/ and ensure the Generative AI API is enabled for your project.")
                raise
            if "NOT_FOUND" in serr or "not found" in serr.lower():
                print("\nGemini client returned NOT_FOUND for model:", model_name)
                print("This means the model isn't available for your API version/account. Run a model list or set GEMINI_MODEL to a model you have access to.")
                print("Example: set GEMINI_MODEL=models/gemini-2.5-flash-image")
                raise
            raise

        # parse response parts for inline image data
        try:
            cand = resp.candidates[0]
        except Exception:
            raise RuntimeError("No candidates returned from Gemini")

        for part in cand.content.parts:
            if getattr(part, 'inline_data', None) and getattr(part.inline_data, 'data', None):
                img_bytes = part.inline_data.data
                image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                # Do not overlay text on Gemini-generated images per user request.
                return image

        raise RuntimeError("Gemini returned no inline image data in response.")

    # Fallback to older google.generativeai client if available
    if genai_old is not None:
        if not api_key_env:
            raise RuntimeError("Missing GOOGLE_API_KEY environment variable for legacy client.")
        genai_old.configure(api_key=api_key_env)
        model = genai_old.GenerativeModel("gemini-2.5-flash-image")
        prompt_payload = [{"role": "user", "parts": [make_gemini_prompt(title)]}]
        resp = model.generate_content(prompt_payload, generation_config={"mime_type": "image/png", "size": f"{size[0]}x{size[1]}"})
        if not hasattr(resp, "binary") or not resp.binary:
            raise RuntimeError("No image data returned from Gemini (legacy client).")

        img_bytes = resp.binary
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        # Do not overlay text on Gemini-generated images per user request.
        # Print the prompt used (legacy flow uses same helper)
        print("Gemini prompt (legacy):\n", make_gemini_prompt(title))
        return image

    raise RuntimeError("No supported Gemini client installed. Install 'google-genai' or 'google-generativeai'.")

# ---------------------------
# CLI
# ---------------------------

def cmd_scrape(args):
    titles = scrape_titles(args.url, args.limit)
    ensure_dir(Path(args.out).parent)
    ensure_dir(Path(args.out).parent)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["title"])
        for t in titles:
            w.writerow([t])
    print(f"Wrote {len(titles)} titles -> {args.out}")

def iter_titles(csv_path: Path) -> List[str]:
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            t = row.get("title","").strip()
            if t:
                rows.append(t)
    return rows

def cmd_pillow(args):
    raise RuntimeError('Pillow generation has been removed. Use the gemini subcommand.')

def cmd_gemini(args):
    # upfront checks for environment and optional dependency to avoid a long traceback
    if genai_mod is None and genai_old is None:
        print("No Gemini client installed. Install 'google-genai' (preferred) or 'google-generativeai' (legacy).")
        return

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    # Try to load OAuth creds if api_key absent
    creds = None
    if not api_key:
        try:
            from load_creds import load_creds
            creds = load_creds()
        except Exception:
            creds = None

    if not api_key and not creds:
        print("Missing credentials: either set GOOGLE_API_KEY or provide OAuth credentials via load_creds.py/token.json.")
        return

    titles = iter_titles(Path(args.csv))
    theme = get_theme(args.theme)
    W,H = parse_size(args.size)
    out_dir = Path(args.out); ensure_dir(out_dir)
    # load creds once if API key not provided
    creds = None
    if not api_key:
        try:
            from load_creds import load_creds
            creds = load_creds()
        except Exception:
            creds = None

    # Limit number of Gemini requests per run to avoid exceeding token/quota limits.
    try:
        max_reqs = int(os.environ.get("GEMINI_MAX_REQUESTS", "1"))
    except Exception:
        max_reqs = 1

    for i, t in enumerate(titles, 1):
        if i > max_reqs:
            print(f"Reached GEMINI_MAX_REQUESTS={max_reqs}; skipping remaining titles.")
            break
        img = make_gemini_image(t, (W,H), theme, api_key=api_key, font_path=args.font_path, creds=creds)
        out_path = out_dir / f"{i:02d}_header_ai.png"
        img.save(out_path, format="PNG")
        print("Saved", out_path)

def main():
    p = argparse.ArgumentParser(description="Auto-generate blog header images.")
    sub = p.add_subparsers()

    ps = sub.add_parser("scrape", help="Scrape latest titles")
    ps.add_argument("--url", required=True)
    ps.add_argument("--limit", type=int, default=10)
    ps.add_argument("--out", default="data/titles.csv")
    ps.set_defaults(func=cmd_scrape)

    pp = sub.add_parser("pillow", help="Generate typographic headers (no API)")
    pp.add_argument("--csv", default="data/titles.csv")
    pp.add_argument("--size", default="1600x900")
    pp.add_argument("--theme", default="endo")
    pp.add_argument("--out", default="out/")
    pp.add_argument("--font-path", default=None, help="Optional path to a .ttf/.otf font")
    pp.set_defaults(func=cmd_pillow)

    pg = sub.add_parser("gemini", help="Generate illustrated headers via Gemini 2.5 Flash Image")
    pg.add_argument("--csv", default="data/titles.csv")
    pg.add_argument("--size", default="1600x900")
    pg.add_argument("--theme", default="endo")
    pg.add_argument("--out", default="out/")
    pg.add_argument("--font-path", default=None)
    pg.set_defaults(func=cmd_gemini)

    args = p.parse_args()
    if not hasattr(args, "func"):
        p.print_help()
        sys.exit(1)
    args.func(args)

if __name__ == "__main__":
    main()
