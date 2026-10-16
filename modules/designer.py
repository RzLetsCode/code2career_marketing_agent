import os
from typing import List, Tuple
import img2pdf
from playwright.sync_api import sync_playwright
from config.settings import settings
from core.logger import logger
from modules.strategist import CarouselPost, Slide


class SlideDesigner:
    """Renders overflow-proof, enterprise-grade 4:5 portrait graphic slides via Playwright."""

    def __init__(self, output_dir: str = settings.slides_output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_html(self, slide: Slide, total_slides: int = 5) -> str:
        # Comparison matrix markup for Slide 3
        matrix_html = ""
        if slide.left_column_points and slide.right_column_points:
            left_items = "".join([f"<li style='margin-bottom: 10px; display: flex; align-items: flex-start; gap: 8px;'><span style='color: #ef4444; font-weight: 800;'>✕</span> <span>{pt}</span></li>" for pt in slide.left_column_points])
            right_items = "".join([f"<li style='margin-bottom: 10px; display: flex; align-items: flex-start; gap: 8px;'><span style='color: #22c55e; font-weight: 800;'>✓</span> <span>{pt}</span></li>" for pt in slide.right_column_points])
            matrix_html = f"""
            <div style="display: flex; gap: 20px; margin-top: 30px; width: 100%;">
                <div style="flex: 1; background: linear-gradient(135deg, rgba(239, 68, 68, 0.06) 0%, rgba(15, 23, 42, 0.6) 100%); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 16px; padding: 22px;">
                    <div style="color: #f87171; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                        <span style="width: 6px; height: 6px; background: #ef4444; border-radius: 50%;"></span>
                        {slide.left_column_title or "NAIVE PATTERN"}
                    </div>
                    <ul style="list-style: none; padding: 0; margin: 0; color: #cbd5e1; font-size: 16px; line-height: 1.45; font-weight: 500;">
                        {left_items}
                    </ul>
                </div>
                <div style="flex: 1; background: linear-gradient(135deg, rgba(34, 197, 94, 0.08) 0%, rgba(15, 23, 42, 0.6) 100%); border: 1px solid rgba(34, 197, 94, 0.35); border-radius: 16px; padding: 22px;">
                    <div style="color: #4ade80; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                        <span style="width: 6px; height: 6px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 8px #22c55e;"></span>
                        {slide.right_column_title or "ENTERPRISE STANDARD"}
                    </div>
                    <ul style="list-style: none; padding: 0; margin: 0; color: #f8fafc; font-size: 16px; line-height: 1.45; font-weight: 500;">
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
                @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{
                    width: 1080px;
                    height: 1350px;
                    background-color: #07090e;
                    background-image: 
                        radial-gradient(circle at 10% 10%, rgba(56, 189, 248, 0.15) 0%, transparent 40%),
                        radial-gradient(circle at 90% 90%, rgba(168, 85, 247, 0.12) 0%, transparent 40%),
                        linear-gradient(to bottom, #07090e, #0b0f19);
                    color: #ffffff;
                    font-family: 'Plus Jakarta Sans', sans-serif;
                    padding: 85px 80px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    overflow: hidden;
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .brand-container {{
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }}
                .brand-dot {{
                    width: 10px;
                    height: 10px;
                    background-color: #38bdf8;
                    border-radius: 50%;
                    box-shadow: 0 0 12px #38bdf8;
                }}
                .brand {{
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 22px;
                    font-weight: 700;
                    color: #f8fafc;
                    letter-spacing: -0.5px;
                }}
                .badge {{
                    background: rgba(56, 189, 248, 0.1);
                    border: 1px solid rgba(56, 189, 248, 0.3);
                    color: #38bdf8;
                    padding: 8px 20px;
                    border-radius: 999px;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 14px;
                    font-weight: 700;
                    letter-spacing: 1.5px;
                    text-transform: uppercase;
                }}
                .main {{
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    flex-grow: 1;
                    margin: 25px 0;
                }}
                .headline {{
                    font-size: 52px;
                    font-weight: 800;
                    line-height: 1.15;
                    letter-spacing: -1.5px;
                    color: #ffffff;
                    margin-bottom: 24px;
                }}
                .content {{
                    font-size: 26px;
                    line-height: 1.5;
                    color: #94a3b8;
                    font-weight: 500;
                    max-width: 940px;
                }}
                .footer {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-top: 1px solid rgba(255, 255, 255, 0.08);
                    padding-top: 32px;
                }}
                .handle {{
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 18px;
                    color: #64748b;
                    font-weight: 600;
                }}
                .pagination {{
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 18px;
                    color: #38bdf8;
                    font-weight: 700;
                    background: rgba(56, 189, 248, 0.08);
                    padding: 6px 14px;
                    border-radius: 8px;
                    border: 1px solid rgba(56, 189, 248, 0.2);
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="brand-container">
                    <div class="brand-dot"></div>
                    <div class="brand">code2career.ai</div>
                </div>
                <div class="badge">{slide.tag}</div>
            </div>
            <div class="main">
                <h1 class="headline">{slide.headline}</h1>
                <p class="content">{slide.content}</p>
                {matrix_html}
            </div>
            <div class="footer">
                <span class="handle">@code2career_ai • Enterprise AI Engineering</span>
                <span class="pagination">0{slide.slide_num} / 0{total_slides}</span>
            </div>
        </body>
        </html>
        """
        return html_content

    def export_as_pdf(self, image_paths: List[str], output_pdf: str = None) -> str:
        if not output_pdf:
            output_pdf = os.path.join(self.output_dir, "carousel_document.pdf")
        with open(output_pdf, "wb") as f:
            f.write(img2pdf.convert(image_paths))
        logger.info(f"Designer: Multi-page document compiled -> {output_pdf}")
        return output_pdf

    def render_carousel(self, carousel: CarouselPost) -> Tuple[List[str], str]:
        logger.info(f"Designer: Rendering {len(carousel.slides)} enterprise-grade graphic slides via Playwright...")
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

        logger.info("Designer: All 5 enterprise slides rendered locally.")
        pdf_path = self.export_as_pdf(image_paths)
        return image_paths, pdf_path


Designer = SlideDesigner