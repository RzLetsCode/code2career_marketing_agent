import os
from typing import List, Tuple
import img2pdf
from playwright.sync_api import sync_playwright
from config.settings import settings
from core.logger import logger
from modules.strategist import CarouselPost, Slide


class SlideDesigner:
    """Renders 4:5 portrait graphic slides via Playwright and compiles PDF carousels."""

    def __init__(self, output_dir: str = settings.slides_output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_html(self, slide: Slide, total_slides: int = 5) -> str:
        # Comparison matrix markup for Slide 3
        matrix_html = ""
        if slide.left_column_points and slide.right_column_points:
            left_items = "".join([f"<li style='margin-bottom: 8px;'>✕ {pt}</li>" for pt in slide.left_column_points])
            right_items = "".join([f"<li style='margin-bottom: 8px;'>✓ {pt}</li>" for pt in slide.right_column_points])
            matrix_html = f"""
            <div style="display: flex; gap: 20px; margin-top: 35px; width: 100%;">
                <div style="flex: 1; background: rgba(239, 68, 68, 0.08); border: 1.5px solid rgba(239, 68, 68, 0.35); border-radius: 16px; padding: 24px;">
                    <div style="color: #ef4444; font-size: 16px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 14px;">
                        {slide.left_column_title or "TOY TUTORIAL"}
                    </div>
                    <ul style="list-style: none; padding: 0; margin: 0; color: #cbd5e1; font-size: 18px; line-height: 1.45;">
                        {left_items}
                    </ul>
                </div>
                <div style="flex: 1; background: rgba(34, 197, 94, 0.08); border: 1.5px solid rgba(34, 197, 94, 0.35); border-radius: 16px; padding: 24px;">
                    <div style="color: #22c55e; font-size: 16px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 14px;">
                        {slide.right_column_title or "ENTERPRISE"}
                    </div>
                    <ul style="list-style: none; padding: 0; margin: 0; color: #f8fafc; font-size: 18px; line-height: 1.45;">
                        {right_items}
                    </ul>
                </div>
            </div>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{
                    width: 1080px;
                    height: 1350px;
                    background-color: #07090e;
                    background-image: 
                        radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.12) 0%, transparent 45%),
                        radial-gradient(circle at 85% 85%, rgba(168, 85, 247, 0.10) 0%, transparent 45%);
                    color: #ffffff;
                    font-family: 'Plus Jakarta Sans', sans-serif;
                    padding: 90px 80px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .brand {{
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 24px;
                    font-weight: 700;
                    color: #38bdf8;
                    letter-spacing: -0.5px;
                }}
                .badge {{
                    background: rgba(56, 189, 248, 0.12);
                    border: 1px solid rgba(56, 189, 248, 0.3);
                    color: #38bdf8;
                    padding: 8px 18px;
                    border-radius: 999px;
                    font-size: 16px;
                    font-weight: 700;
                    letter-spacing: 1.2px;
                    text-transform: uppercase;
                }}
                .main {{
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    flex-grow: 1;
                    margin: 40px 0;
                }}
                .headline {{
                    font-size: 58px;
                    font-weight: 800;
                    line-height: 1.15;
                    letter-spacing: -1.5px;
                    color: #ffffff;
                    margin-bottom: 28px;
                }}
                .content {{
                    font-size: 28px;
                    line-height: 1.5;
                    color: #94a3b8;
                    font-weight: 500;
                }}
                .footer {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-top: 1px solid rgba(255, 255, 255, 0.08);
                    padding-top: 36px;
                }}
                .handle {{
                    font-size: 20px;
                    color: #64748b;
                    font-weight: 600;
                }}
                .pagination {{
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 20px;
                    color: #38bdf8;
                    font-weight: 700;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="brand">code2career_ai</div>
                <div class="badge">{slide.tag}</div>
            </div>
            <div class="main">
                <h1 class="headline">{slide.headline}</h1>
                <p class="content">{slide.content}</p>
                {matrix_html}
            </div>
            <div class="footer">
                <span class="handle">@code2career_ai</span>
                <span class="pagination">{slide.slide_num} / {total_slides}</span>
            </div>
        </body>
        </html>
        """
        return html_content

    def export_as_pdf(self, image_paths: List[str], output_pdf: str = None) -> str:
        """Converts rendered PNGs into a multi-page PDF document for LinkedIn."""
        if not output_pdf:
            output_pdf = os.path.join(self.output_dir, "carousel_document.pdf")
        with open(output_pdf, "wb") as f:
            f.write(img2pdf.convert(image_paths))
        logger.info(f"Designer: Multi-page document compiled -> {output_pdf}")
        return output_pdf

    def render_carousel(self, carousel: CarouselPost) -> Tuple[List[str], str]:
        """Renders 5 high-resolution PNG slides and exports a matching PDF document."""
        logger.info(f"Designer: Rendering {len(carousel.slides)} graphic slides via Playwright...")
        image_paths = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)

            for slide in carousel.slides:
                html = self._generate_html(slide, len(carousel.slides))
                page.set_content(html, wait_until="networkidle")
                out_path = os.path.join(self.output_dir, f"slide_{slide.slide_num}.png")
                page.screenshot(path=out_path, type="png")
                image_paths.append(out_path)

            browser.close()

        logger.info("Designer: All 5 slides rendered locally.")
        pdf_path = self.export_as_pdf(image_paths)
        return image_paths, pdf_path


Designer = SlideDesigner