import sys
from core.logger import logger
from core.state_manager import StateManager
from modules.trend_researcher import TrendResearcher
from modules.strategist import MarketingStrategist
from modules.designer import Designer
from modules.uploader import Uploader
from modules.publisher import Publisher
from modules.linkedin_publisher import LinkedInPublisher


def run_pipeline():
    print("=" * 65, flush=True)
    print("🚀 CODE2CAREER_AI AUTONOMOUS MARKETING PIPELINE STARTED", flush=True)
    print("=" * 65, flush=True)

    # Step 0: State Check & Deduplication
    print("[*] Step 0: Initializing state manager...", flush=True)
    state_mgr = StateManager()
    past_topics = state_mgr.get_published_topics()
    print(f"    Found {len(past_topics)} past topics in state history.", flush=True)

    # Step 1: Real-time Developer Trend Scouting
    scout = TrendResearcher()
    signals = scout.get_latest_market_signals()

    # Step 2: Strategist Formulates Content Architecture
    print("\n[*] Step 2: Formulating carousel strategy with Azure OpenAI...", flush=True)
    strategist = MarketingStrategist()
    carousel = strategist.formulate_carousel(market_signals=signals, past_topics=past_topics)
    print(f"    Topic Selected: '{carousel.topic}'")
    print(f"    Pillar: {carousel.pillar} | Keyword: {carousel.trigger_keyword}")

    # Step 3: Render Graphic Slides (PNGs) & Compile PDF Document
    print(f"\n[*] Step 3: Rendering {len(carousel.slides)} slides with Playwright...", flush=True)
    designer = Designer()
    image_paths, pdf_path = designer.render_carousel(carousel)
    print(f"    Rendered {len(image_paths)} PNG slides and compiled {pdf_path}")

    # Step 4: Host Slides on Cloudinary CDN
    print("\n[*] Step 4: Uploading slides to Cloudinary...", flush=True)
    uploader = Uploader()
    image_urls = uploader.upload_all(image_paths)
    print(f"    Uploaded {len(image_urls)} images to secure HTTPS URLs.")

    # Step 5: Publish Live Carousel to Instagram
    print("\n[*] Step 5: Publishing carousel to Instagram...", flush=True)
    publisher = Publisher()
    media_id = publisher.publish_carousel(image_urls=image_urls, caption=carousel.caption)

    # Step 6: Syndication to LinkedIn (Optional Document Carousel)
    linkedin_pub = LinkedInPublisher()
    linkedin_pub.publish_document(
        pdf_path=pdf_path,
        title=carousel.topic,
        commentary=carousel.caption
    )

    # Step 7: Record Event in History
    print("\n[*] Step 7: Recording post to content_history.json...", flush=True)
    state_mgr.record_publication(
        topic=carousel.topic,
        media_id=media_id,
        keyword=carousel.trigger_keyword
    )

    print("=" * 65, flush=True)
    print("✅ PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print(f"   Topic:    {carousel.topic}")
    print(f"   Media ID: {media_id}")
    print("   Profile:  https://www.instagram.com/code2career_ai/")
    print("=" * 65, flush=True)


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        logger.exception(f"FATAL: Pipeline execution failed: {e}")
        sys.exit(1)