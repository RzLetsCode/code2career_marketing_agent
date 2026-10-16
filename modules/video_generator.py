import os
import asyncio
from typing import List
import edge_tts
from PIL import Image
from config.settings import settings
from core.logger import logger
from modules.strategist import CarouselPost, Slide

try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
    MOVIEPY_V2 = False
except ImportError:
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    MOVIEPY_V2 = True


class VideoGenerator:
    """Compiles 1080x1350 slides + neural voiceovers into a polished 1080x1920 (9:16) MP4 Reel."""

    def __init__(self, output_dir: str = settings.slides_output_dir, voice: str = "en-US-ChristopherNeural"):
        self.output_dir = output_dir
        self.voice = voice
        os.makedirs(self.output_dir, exist_ok=True)

    async def _synthesize_audio(self, text: str, out_path: str):
        communicate = edge_tts.Communicate(text=text, voice=self.voice, rate="+4%")
        await communicate.save(out_path)

    def _build_narration_text(self, slide: Slide, total_slides: int, trigger_keyword: str) -> str:
        if getattr(slide, "voiceover", None) and slide.voiceover.strip():
            return slide.voiceover.strip()

        parts = [slide.headline.strip(), slide.content.strip()]
        if slide.slide_num == total_slides and trigger_keyword:
            parts.append(f"Comment {trigger_keyword} below and our system will instantly DM you the complete source repository.")

        return " ".join(parts)

    def _frame_for_reel(self, img_path: str, idx: int) -> str:
        reel_frame_path = os.path.join(self.output_dir, f"temp_reel_frame_{idx}.png")
        with Image.open(img_path).convert("RGB") as slide_img:
            canvas = Image.new("RGB", (1080, 1920), (7, 9, 14))
            y_offset = (1920 - slide_img.height) // 2
            canvas.paste(slide_img, (0, max(0, y_offset)))
            canvas.save(reel_frame_path, "PNG")
        return reel_frame_path

    def render_reel(self, carousel: CarouselPost, image_paths: List[str], output_filename: str = "carousel_reel.mp4") -> str:
        logger.info("VideoGenerator: Synthesizing neural voiceover and compiling 9:16 MP4 Reel...")
        video_clips = []
        audio_clips = []
        temp_files = []
        total_slides = len(carousel.slides)

        try:
            for idx, (slide, img_path) in enumerate(zip(carousel.slides, image_paths), start=1):
                narration = self._build_narration_text(slide, total_slides, carousel.trigger_keyword)
                audio_path = os.path.join(self.output_dir, f"temp_voice_{idx}.mp3")
                asyncio.run(self._synthesize_audio(narration, audio_path))
                temp_files.append(audio_path)

                reel_frame_path = self._frame_for_reel(img_path, idx)
                temp_files.append(reel_frame_path)

                audio_clip = AudioFileClip(audio_path)
                audio_clips.append(audio_clip)
                duration = max(audio_clip.duration + 0.4, 3.2)

                if MOVIEPY_V2:
                    clip = ImageClip(reel_frame_path).with_duration(duration).with_audio(audio_clip)
                else:
                    clip = ImageClip(reel_frame_path).set_duration(duration).set_audio(audio_clip)

                video_clips.append(clip)

            final_video = concatenate_videoclips(video_clips, method="compose")
            output_video_path = os.path.join(self.output_dir, output_filename)

            final_video.write_videofile(
                output_video_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                bitrate="3500k",
                logger=None
            )
            final_video.close()
            logger.info(f"VideoGenerator: MP4 Reel compiled -> {output_video_path}")
            return output_video_path

        finally:
            for c in video_clips:
                try:
                    c.close()
                except Exception:
                    pass
            for a in audio_clips:
                try:
                    a.close()
                except Exception:
                    pass
            for f_path in temp_files:
                if os.path.exists(f_path):
                    try:
                        os.remove(f_path)
                    except Exception:
                        pass