import sys
from core.logger import logger
from core.state_manager import StateManager
from modules.trend_researcher import TrendResearcher
from modules.strategist import StrategistAgent
from modules.designer import SlideDesigner
from modules.uploader import CloudinaryUploader
from modules.publisher import InstagramPublisher

def run_pipeline():
    print("=" * 65, flush=True)
    print("🚀 CODE2CAREER_AI AUTONOMOUS MARKETING PIPELINE STARTED", flush=True)
    print("=" * 65, flush=True)

    try:
        # Step 0: State Check
        print("[*] Step 0: Initializing state manager...", flush=True)
        state_mgr = StateManager()
        past_topics = state_mgr.get_published_topics()
        print(f"    Found {len(past_topics)} past topics in state history.", flush=True)

        # Step 1: Trend Scouting
        researcher = TrendResearcher()
        market_signals = researcher.get_latest_market_signals()

        # Step 2: Content Strategy via Azure OpenAI
        print("\n[*] Step 2: Formulating carousel strategy with Azure OpenAI...", flush=True)
        strategist = StrategistAgent()
        post_data = strategist.formulate_carousel(market_signals, past_topics)
        print(f"    Topic Selected: '{post_data.topic}'", flush=True)
        print(f"    Pillar: {post_data.pillar} | Keyword: {post_data.trigger_keyword}", flush=True)

        # Step 3: Graphic Rendering via Playwright
        print("\n[*] Step 3: Rendering 5 slides with Playwright Chromium...", flush=True)
        designer = SlideDesigner()
        rendered_images = designer.render(post_data.slides)
        print(f"    Rendered {len(rendered_images)} slides to disk.", flush=True)

        # Step 4: Cloudinary Upload
        print("\n[*] Step 4: Uploading slides to Cloudinary...", flush=True)
        uploader = CloudinaryUploader()
        public_urls = uploader.upload_all(rendered_images)
        print(f"    Uploaded {len(public_urls)} images to secure HTTPS URLs.", flush=True)

        # Step 5: Meta Instagram Publishing
        print("\n[*] Step 5: Publishing carousel to Instagram...", flush=True)
        publisher = InstagramPublisher()
        live_media_id = publisher.publish_carousel(public_urls, post_data.caption)

        # Step 6: Atomic State Update
        print("\n[*] Step 6: Recording post to content_history.json...", flush=True)
        state_mgr.record_publication(
            topic=post_data.topic,
            media_id=live_media_id,
            keyword=post_data.trigger_keyword
        )

        print("\n" + "=" * 65, flush=True)
        print(f"✅ CAROUSEL PUBLISHED SUCCESSFULLY!", flush=True)
        print(f"   Topic:    {post_data.topic}", flush=True)
        print(f"   Media ID: {live_media_id}", flush=True)
        print(f"   Profile:  https://www.instagram.com/code2career_ai/", flush=True)
        print("=" * 65, flush=True)

    except Exception as e:
        logger.critical(f"❌ PIPELINE EXECUTION FAILED: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()