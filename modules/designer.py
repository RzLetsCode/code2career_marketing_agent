import os
from typing import List
from playwright.sync_api import sync_playwright
from modules.strategist import Slide
from config.settings import settings
from core.logger import logger

class SlideDesigner:
    def __init__(self, output_dir: str = settings.rendered_slides_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_html(self, slide: Slide, total_slides: int) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8" />
          <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
              width: 1080px; height: 1350px;
              background: #080D1A; color: #F8FAFC;
              font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
              display: flex; flex-direction: column; justify-content: space-between;
              padding: 100px 85px;
            }}
            .header {{ display: flex; justify-content: space-between; align-items: center; }}
            .brand {{ font-size: 34px; font-weight: 900; color: #38BDF8; letter-spacing: -0.5px; }}
            .tag {{
              font-size: 20px; font-weight: 700; color: #38BDF8;
              background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35);
              padding: 8px 22px; border-radius: 999px; letter-spacing: 1px;
            }}
            .main {{ margin: auto 0; }}
            .headline {{
              font-size: 66px; font-weight: 800; line-height: 1.15;
              color: #FFFFFF; margin-bottom: 40px; letter-spacing: -1.2px;
            }}
            .body-box {{
              background: #10172A; border-left: 6px solid #38BDF8;
              padding: 42px; border-radius: 16px; font-size: 36px;
              line-height: 1.5; color: #CBD5E1; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }}
            .footer {{
              display: flex; justify-content: space-between; align-items: center;
              font-size: 24px; color: #64748B; border-top: 2px solid #1E293B; padding-top: 35px;
            }}
          </style>
        </head>
        <body>
          <div class="header">
            <div class="brand">Code2Career_AI</div>
            <div class="tag">{slide.tag}</div>
          </div>
          <div class="main">
            <div class="headline">{slide.headline}</div>
            <div class="body-box">{slide.content}</div>
          </div>
          <div class="footer">
            <span>Slide {slide.slide_num} of {total_slides}</span>
            <span>Follow @code2career_ai</span>
          </div>
        </body>
        </html>
        """

    def render(self, slides: List[Slide]) -> List[str]:
        logger.info(f"Designer: Rendering {len(slides)} graphic slides via Playwright...")
        rendered_paths = []

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1080, "height": 1350})

            for s in slides:
                html_content = self._generate_html(s, len(slides))
                file_path = os.path.abspath(f"{self.output_dir}/slide_{s.slide_num}.png")
                page.set_content(html_content)
                page.screenshot(path=file_path)
                rendered_paths.append(file_path)

            browser.close()

        logger.info(f"Designer: All {len(rendered_paths)} slides rendered locally.")
        return rendered_paths