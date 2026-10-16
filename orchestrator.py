import os
import sys
import time
import random
import argparse
from dotenv import load_dotenv

from core.logger import logger
from core.state_manager import StateManager
from modules.trend_researcher import TrendResearcher
from modules.strategist import MarketingStrategist
from modules.designer import Designer
from modules.uploader import Uploader
from modules.publisher import Publisher
from modules.linkedin_publisher import LinkedInPublisher
from modules.video_generator import VideoGenerator
from modules.animator import AnimationEngine

load_dotenv()


def execute_with_retry(
    action,
    step_name: str,
    max_retries: int = 3,
    initial_delay: float = 2.0,
    backoff_factor: float = 2.0
):
    """Executes a callable action with exponential backoff and random jitter."""
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


def get_execution_controls() -> tuple[str, str, str]:
    """Reads format, platform, and video animation mode toggles from CLI arguments or .env defaults."""
    parser = argparse.ArgumentParser(description="Code2Career_AI Autonomous Marketing Pipeline")
    parser.add_argument(
        "--formats",
        choices=["both", "carousel", "video", "none"],
        default=os.getenv("PUBLISH_FORMATS", "carousel").lower().strip(),
        help="Formats to run: both | carousel | video | none"
    )
    parser.add_argument(
        "--platforms",
        choices=["both", "instagram", "linkedin", "none"],
        default=os.getenv("PUBLISH_PLATFORMS", "both").lower().strip(),
        help="Platforms to publish to: both | instagram | linkedin | none"
    )
    parser.add_argument(
        "--video-mode",
        choices=["motion", "manim", "auto"],
        default=os.getenv("VIDEO_ENGINE_MODE", "auto").lower().strip(),
        help="Video engine: motion (Ken Burns) | manim (Vector animations) | auto (Smart routing)"
    )
    args, _ = parser.parse_known_args()
    return args.formats, args.platforms, args.video_mode


def run_pipeline():
    formats_mode, platforms_mode, video_mode = get_execution_controls()

    run_carousel = formats_mode in ("both", "carousel")
    run_video = formats_mode in ("both", "video")
    run_ig = platforms_mode in ("both", "instagram")
    run_li = platforms_mode in ("both", "linkedin")

    print("=" * 65, flush=True)
    print("🚀 CODE2CAREER_AI AUTONOMOUS MARKETING PIPELINE STARTED", flush=True)
    print(f"   🎛️  Formats:     {formats_mode.upper()} (Carousel={run_carousel}, Video={run_video})", flush=True)
    print(f"   🎯 Platforms:   {platforms_mode.upper()} (Instagram={run_ig}, LinkedIn={run_li})", flush=True)
    print(f"   🎬 Video Engine: {video_mode.upper()}", flush=True)
    print("=" * 65, flush=True)

    if not run_carousel and not run_video:
        print("[~] PUBLISH_FORMATS is set to 'none'. Exiting cleanly without action.", flush=True)
        return

    # Step 0: State Check & Deduplication
    print("[*] Step 0: Initializing state manager...", flush=True)
    state_mgr = None
    try:
        state_mgr = StateManager()
        past_topics = state_mgr.get_published_topics()
        print(f"    Found {len(past_topics)} past topics in state history.", flush=True)
    except Exception as e:
        logger.error(f"Failed to read state file: {e}")
        past_topics = []
        print(f"    [!] Warning: Could not read past topics. Proceeding with empty history: {e}", flush=True)

    # Step 1: Real-time Developer Trend Scouting
    scout = TrendResearcher()
    signals = execute_with_retry(
        action=lambda: scout.get_latest_market_signals(),
        step_name="Step 1: Trend Research",
        max_retries=3,
        initial_delay=2.0
    )

    # Step 2: Strategist Formulates Content Architecture
    print("\n[*] Step 2: Formulating content strategy with Azure OpenAI...", flush=True)
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

    uploader = Uploader()
    publisher = Publisher() if run_ig else None
    linkedin_pub = LinkedInPublisher() if run_li else None

    ig_carousel_id = None
    li_carousel_id = None
    ig_reel_id = None
    li_video_id = None

    # =========================================================================
    # TRACK A: CAROUSEL PIPELINE
    # =========================================================================
    if run_carousel:
        print("\n--- [TRACK A: CAROUSEL PIPELINE] ---", flush=True)

        if run_ig:
            try:
                print("[*] Step 4a: Uploading PNG slides to Cloudinary...", flush=True)
                image_urls = execute_with_retry(
                    action=lambda: uploader.upload_all(image_paths),
                    step_name="Step 4a: CDN Image Upload",
                    max_retries=3,
                    initial_delay=2.0
                )
                print(f"    Uploaded {len(image_urls)} images to secure HTTPS URLs.", flush=True)

                print("[*] Step 5a: Publishing carousel to Instagram...", flush=True)
                ig_carousel_id = execute_with_retry(
                    action=lambda: publisher.publish_carousel(image_urls=image_urls, caption=carousel.caption),
                    step_name="Step 5a: Instagram Carousel Publishing",
                    max_retries=3,
                    initial_delay=5.0
                )
                print(f"    ✅ Instagram Carousel Published! Media ID: {ig_carousel_id}", flush=True)
            except Exception as e:
                logger.error(f"Instagram Carousel failed: {e}")
                print(f"    [!] Instagram Carousel failed: {e}", flush=True)
        else:
            print("    [~] Instagram Carousel skipped (Platform disabled).", flush=True)

        if run_li:
            try:
                print("[*] Step 6a: Publishing document carousel to LinkedIn...", flush=True)

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
                    raise AttributeError("LinkedInPublisher has no valid publish method.")

                li_carousel_id = execute_with_retry(
                    action=_publish_linkedin,
                    step_name="Step 6a: LinkedIn Document Publishing",
                    max_retries=3,
                    initial_delay=3.0
                )
                print(f"    ✅ LinkedIn Document Carousel Published! Post ID: {li_carousel_id}", flush=True)
            except Exception as e:
                logger.error(f"LinkedIn Document Carousel failed: {e}")
                print(f"    [!] LinkedIn Document Carousel failed: {e}", flush=True)
        else:
            print("    [~] LinkedIn Document Carousel skipped (Platform disabled).", flush=True)
    else:
        print("\n[~] Track A (Carousel) skipped via configuration.", flush=True)

    # =========================================================================
    # TRACK B: VIDEO PIPELINE (Smart Auto-Routing)
    # =========================================================================
    if run_video:
        selected_video_mode = video_mode
        if selected_video_mode == "auto":
            technical_keywords = ["rag", "pipeline", "agent", "embedding", "vector", "architecture", "flow", "chunk", "memory", "browser", "deployment", "async", "distributed"]
            is_technical = any(kw in carousel.topic.lower() for kw in technical_keywords)
            selected_video_mode = "manim" if is_technical else "motion"
            print(f"   🤖 Auto-Router evaluated topic -> Selected Engine: {selected_video_mode.upper()}", flush=True)

        print(f"\n--- [TRACK B: VIDEO PIPELINE ({selected_video_mode.upper()} ENGINE)] ---", flush=True)
        try:
            if selected_video_mode == "manim":
                print("[*] Step 4b: Rendering vector animations via Manim...", flush=True)
                anim_engine = AnimationEngine()
                video_path = execute_with_retry(
                    action=lambda: anim_engine.render_animated_reel(carousel=carousel),
                    step_name="Step 4b: Manim Vector Animation",
                    max_retries=2,
                    initial_delay=2.0
                )
            else:
                print("[*] Step 4b: Compiling cinematic Ken Burns motion video via MoviePy...", flush=True)
                video_gen = VideoGenerator()
                video_path = execute_with_retry(
                    action=lambda: video_gen.render_reel(carousel=carousel, image_paths=image_paths),
                    step_name="Step 4b: Motion Video Rendering",
                    max_retries=2,
                    initial_delay=2.0
                )
            print(f"    ✅ Compiled video asset: {video_path}", flush=True)

            if run_ig:
                try:
                    print("[*] Step 5b: Uploading video to Cloudinary & publishing Instagram Reel...", flush=True)
                    video_url = execute_with_retry(
                        action=lambda: uploader.upload_video(video_path),
                        step_name="Step 5b-1: Cloudinary Video Upload",
                        max_retries=3,
                        initial_delay=2.0
                    )
                    ig_reel_id = execute_with_retry(
                        action=lambda: publisher.publish_reel(video_url=video_url, caption=carousel.caption),
                        step_name="Step 5b-2: Instagram Reel Publishing",
                        max_retries=2,
                        initial_delay=5.0
                    )
                    print(f"    ✅ Instagram Reel Published! Media ID: {ig_reel_id}", flush=True)
                except Exception as e:
                    logger.error(f"Instagram Reel failed: {e}")
                    print(f"    [!] Instagram Reel failed: {e}", flush=True)
            else:
                print("    [~] Instagram Reel skipped (Platform disabled).", flush=True)

            if run_li:
                try:
                    print("[*] Step 6b: Publishing native video to LinkedIn...", flush=True)
                    li_video_id = execute_with_retry(
                        action=lambda: linkedin_pub.publish_video(
                            video_path=video_path,
                            caption=carousel.caption,
                            title=carousel.topic
                        ),
                        step_name="Step 6b: LinkedIn Video Publishing",
                        max_retries=2,
                        initial_delay=3.0
                    )
                    print(f"    ✅ LinkedIn Video Published! Post ID: {li_video_id}", flush=True)
                except Exception as e:
                    logger.error(f"LinkedIn Video failed: {e}")
                    print(f"    [!] LinkedIn Video failed: {e}", flush=True)
            else:
                print("    [~] LinkedIn Video skipped (Platform disabled).", flush=True)

        except Exception as e:
            logger.error(f"Video track failed: {e}")
            print(f"    [!] Video track failed: {e}", flush=True)
    else:
        print("\n[~] Track B (Video) skipped via configuration.", flush=True)

    # =========================================================================
    # STEP 7: RECORD STATE IN HISTORY
    # =========================================================================
    primary_id = ig_carousel_id or ig_reel_id or li_carousel_id or li_video_id
    if primary_id and state_mgr:
        print("\n[*] Step 7: Recording post to content_history.json...", flush=True)
        try:
            execute_with_retry(
                action=lambda: state_mgr.record_publication(
                    topic=carousel.topic,
                    media_id=str(primary_id),
                    keyword=carousel.trigger_keyword,
                    pillar=carousel.pillar
                ),
                step_name="Step 7: State Persistence",
                max_retries=3,
                initial_delay=1.0
            )
            print("    Post recorded in state history with analytics telemetry.", flush=True)
        except Exception as e:
            logger.critical(f"FATAL: Post published ({primary_id}) but failed to update state history: {e}")
            print(f"    [CRITICAL] Post published but state history not saved: {e}", flush=True)
    else:
        print("\n[~] Step 7: No live posts published (Dry-run or all platforms disabled). State history unchanged.", flush=True)

    # Execution Summary
    print("=" * 65, flush=True)
    print("✅ PIPELINE EXECUTION COMPLETED!", flush=True)
    print(f"   Topic:              {carousel.topic}", flush=True)
    print(f"   Video Engine:       {video_mode.upper()}", flush=True)
    print(f"   Instagram Carousel: {ig_carousel_id or 'Skipped / Disabled'}", flush=True)
    print(f"   LinkedIn Carousel:  {li_carousel_id or 'Skipped / Disabled'}", flush=True)
    print(f"   Instagram Reel:     {ig_reel_id or 'Skipped / Disabled'}", flush=True)
    print(f"   LinkedIn Video:     {li_video_id or 'Skipped / Disabled'}", flush=True)
    print(f"   IG Link:            https://www.instagram.com/code2career_ai/", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        logger.exception(f"FATAL: Pipeline execution halted: {e}")
        sys.exit(1)