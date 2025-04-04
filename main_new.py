import os
import tempfile
import asyncio
import markdown2
from playwright.async_api import async_playwright

# === Ask user for headers/footers ===
def ask(prompt):
    val = input(prompt + " (or leave blank): ")
    return val.strip() if val.strip() else None

header_left = None
header_center = "kubernetes master node setup guide"
header_right = None

footer_left = None
footer_center = "Page <span class='pageNumber'></span> of <span class='totalPages'></span>"
footer_right = "vinit shah"

# === Read Markdown ===
input_file = "full_master_node_setup.md"
base_filename = os.path.splitext(os.path.basename(input_file))[0]
with open(input_file, "r", encoding="utf-8") as f:
    md_text = f.read()

# === Convert Markdown to HTML using markdown2 ===
html_body = markdown2.markdown(md_text, extras=["fenced-code-blocks", "tables", "footnotes", "task_list"])

# === Themes: light and dark ===
themes = {
    "light": {
        "css": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css",
        "bg": "#ffffff",
        "fg": "#24292f",
        "border": "#d0d7de",
        "code_bg": "#dcdcdc",
        "accent": "#333333",
        "footer_header_color": "#24292f"
    },
    "dark": {
        "css": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github-dark-dimmed.min.css",
        "bg": "#121212",
        "fg": "#e0e0e0",
        "border": "#3a3a3a",
        "code_bg": "#2a2a2a",
        "accent": "#cccccc",
        "footer_header_color": "#ffffff"
    }
}

# === Create HTML files ===
html_files = {}
for theme, t in themes.items():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'>
        <title>{theme.title()} PDF</title>
        <link rel='stylesheet' href='{t['css']}'>
        <script src='https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js'></script>
        <script>hljs.highlightAll();</script>
        <style>
            html, body {{
                background-color: {t['bg']};
                color: {t['fg']};
                font-family: "Segoe UI Emoji", sans-serif;
                margin: 0;
                padding: 20px;
                padding-bottom: 60px;
                height: 100%;
                width: 100%;
            }}
            @page:first {{
                margin-top: 30px;
                margin-left: 40px;
                margin-right: 40px;
                margin-bottom: 60px;
            }}
            @page {{
                size: A4;
                margin: 60px 40px;
                background: {t['bg']};
            }}
            h1, h2, h3 {{
                color: {t['accent']};
                border-bottom: 1px solid {t['border']};
                padding-bottom: 0.3em;
                margin-top: 1.5em;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 1em;
            }}
            th, td {{
                border: 1px solid {t['border']};
                padding: 8px 12px;
                background-color: {t['code_bg'] if theme == 'dark' else '#fff'};
            }}
            code {{
                background-color: {t['code_bg']};
                padding: 2px 6px;
                border-radius: 4px;
            }}
            pre code {{
                display: block;
                padding: 16px;
                background-color: {t['code_bg']};
                border-radius: 6px;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
    {html_body}
    </body>
    </html>
    """
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
        f.write(html)
        html_files[theme] = f.name

# === Generate PDFs ===
async def generate_pdfs():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for theme, html_path in html_files.items():
            page = await browser.new_page()
            await page.goto("file://" + os.path.abspath(html_path))
            output_path = f"C:/Users/vinit.shah/Documents/Research/master/kubernetes_master_node_setup_guide_{theme}_1.pdf"
            footer_header_color = themes[theme]['footer_header_color']
            await page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                margin={"top": "60px", "bottom": "60px", "left": "40px", "right": "40px"},
                display_header_footer=True,
                header_template=f"<div style='font-size:10px;color:{footer_header_color};width:100%;display:flex;justify-content:space-between;padding:0 10px;'><span>{header_left or ''}</span><span>{header_center or ''}</span><span>{header_right or ''}</span></div>",
                footer_template=f"<div style='font-size:10px;color:{footer_header_color};width:100%;display:flex;justify-content:space-between;padding:0 10px;'><span>{footer_left or ''}</span><span>{footer_center}</span><span>{footer_right or ''}</span></div>"
            )
            print(f"✅ Saved {output_path}")
        await browser.close()

# Run PDF generation
asyncio.run(generate_pdfs())