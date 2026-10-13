import sys
import time
import random
from typing import Callable, Any
from core.logger import logger
from core.state_manager import StateManager
from modules.trend_researcher import TrendResearcher
from modules.strategist import MarketingStrategist
from modules.designer import Designer
from modules.uploader import Uploader
from modules.publisher import Publisher
from modules.linkedin_publisher import LinkedInPublisher


def execute_with_retry(
    action: Callable[[], Any],
    step_name: str,
    max_retries: int = 3,
    initial_delay: float = 2.0,
    backoff_factor: float = 2.0
) -> Any:
    """
    Executes a callable action with exponential backoff and random jitter.
    """
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            return action()
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"❌ {step_name} failed permanently after {max_retries} attempts: {e}")
                raise
            
            jitter = random.uniform(0.2, 0.8)
            sleep_duration = delay + jitter
            logger.warning(f"⚠️ [Attempt {attempt}/{max_retries}] {step_name} failed: {e}. Retrying in {sleep_duration:.2f}s...")
            print(f"    [!] Error during {step_name}: {e}. Retrying in {sleep_duration:.2f}s (Attempt {attempt}/{max_retries})...", flush=True)
            time.sleep(sleep_duration)
            delay *= backoff_factor


def run_pipeline():
    print("=" * 65, flush=True)
    print("🚀 CODE2CAREER_AI AUTONOMOUS MARKETING PIPELINE STARTED", flush=True)
    print("=" * 65, flush=True)

    # Step 0: State Check & Deduplication
    print("[*] Step 0: Initializing state manager...", flush=True)
    try:
        state_mgr = StateManager()
        past_topics = state_mgr.get_published_topics()
        print(f"    Found {len(past_topics)} past topics in state history.", flush=True)
    except Exception as e:
        logger.error(f"Failed to load state history: {e}")
        past_topics = []
        print(f"    [!] Warning: Could not read past topics. Proceeding with empty history: {e}", flush=True)

    # Step 1: Real-time Developer Trend Scouting
    print("\n[*] Step 1: Scouting latest market trends...", flush=True)
    scout = TrendResearcher()
    signals = execute_with_retry(
        action=lambda: scout.get_latest_market_signals(),
        step_name="Step 1: Trend Research",
        max_retries=3,
        initial_delay=2.0
    )

    # Step 2: Strategist Formulates Content Architecture
    print("\n[*] Step 2: Formulating carousel strategy with Azure OpenAI...", flush=True)
    strategist = MarketingStrategist()
    carousel = execute_with_retry(
        action=lambda: strategist.formulate_carousel(market_signals=signals, past_topics=past_topics),
        step_name="Step 2: Strategy & Content Generation",
        max_retries=3,
        initial_delay=3.0
    )
    print(f"    Topic Selected: '{carousel.topic}'", flush=True)
    print(f"    Pillar: {carousel.pillar} | Keyword: {carousel.trigger_keyword}", flush=True)

    # Step 3: Render Graphic Slides (PNGs) & Compile PDF Document
    print(f"\n[*] Step 3: Rendering {len(carousel.slides)} slides with Playwright...", flush=True)
    designer = Designer()
    image_paths, pdf_path = execute_with_retry(
        action=lambda: designer.render_carousel(carousel),
        step_name="Step 3: Slide Rendering & PDF Compilation",
        max_retries=2,
        initial_delay=2.0
    )
    print(f"    Rendered {len(image_paths)} PNG slides and compiled {pdf_path}", flush=True)

    # Step 4: Host Slides on Cloudinary CDN
    print("\n[*] Step 4: Uploading slides to Cloudinary...", flush=True)
    uploader = Uploader()
    image_urls = execute_with_retry(
        action=lambda: uploader.upload_all(image_paths),
        step_name="Step 4: CDN Image Upload",
        max_retries=3,
        initial_delay=2.0
    )
    print(f"    Uploaded {len(image_urls)} images to secure HTTPS URLs.", flush=True)

    # Step 5: Publish Live Carousel to Instagram
    print("\n[*] Step 5: Publishing carousel to Instagram...", flush=True)
    publisher = Publisher()
    media_id = execute_with_retry(
        action=lambda: publisher.publish_carousel(image_urls=image_urls, caption=carousel.caption),
        step_name="Step 5: Instagram Carousel Publishing",
        max_retries=3,
        initial_delay=5.0  # Allows Meta media container processing time
    )
    print(f"    Instagram Carousel Published Successfully! Media ID: {media_id}", flush=True)

    # Step 6: Syndication to LinkedIn (Document Carousel)
    print("\n[*] Step 6: Publishing document carousel to LinkedIn...", flush=True)
    linkedin_post_id = None
    try:
        linkedin_pub = LinkedInPublisher()

        def _publish_linkedin():
            if hasattr(linkedin_pub, "publish_document"):
                return linkedin_pub.publish_document(
                    pdf_path=pdf_path,
                    title=carousel.topic,
                    commentary=carousel.caption
                )
            elif hasattr(linkedin_pub, "publish_carousel"):
                return linkedin_pub.publish_carousel(
                    pdf_path=pdf_path,
                    caption=carousel.caption,
                    title=carousel.topic
                )
            raise AttributeError("LinkedInPublisher has no valid publish method ('publish_document' or 'publish_carousel').")

        linkedin_post_id = execute_with_retry(
            action=_publish_linkedin,
            step_name="Step 6: LinkedIn Document Publishing",
            max_retries=3,
            initial_delay=3.0
        )
        print(f"    LinkedIn Carousel Published Successfully! Post ID: {linkedin_post_id}", flush=True)
    except Exception as e:
        logger.error(f"LinkedIn syndication failed after retries: {e}")
        print(f"    [!] LinkedIn syndication failed: {e}", flush=True)
        print("    Proceeding to state recording to preserve Instagram publication...", flush=True)

    # Step 7: Record Event in History
    print("\n[*] Step 7: Recording post to content_history.json...", flush=True)
    try:
        execute_with_retry(
            action=lambda: state_mgr.record_publication(
                topic=carousel.topic,
                media_id=media_id,
                keyword=carousel.trigger_keyword
            ),
            step_name="Step 7: State Persistence",
            max_retries=3,
            initial_delay=1.0
        )
        print("    Post recorded in state history.", flush=True)
    except Exception as e:
        logger.critical(f"FATAL: Post published to IG ({media_id}) but failed to update state history: {e}")
        print(f"    [CRITICAL] Post published but state history not saved: {e}", flush=True)

    # Execution Summary
    print("=" * 65, flush=True)
    print("✅ PIPELINE EXECUTION COMPLETED!", flush=True)
    print(f"   Topic:       {carousel.topic}", flush=True)
    print(f"   Instagram:   {media_id}", flush=True)
    print(f"   LinkedIn:    {linkedin_post_id if linkedin_post_id else 'Failed / Skipped'}", flush=True)
    print(f"   IG Link:     https://www.instagram.com/code2career_ai/", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        logger.exception(f"FATAL: Pipeline execution halted: {e}")
        sys.exit(1)