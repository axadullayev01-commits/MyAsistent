import asyncio
import os
import shutil
from pathlib import Path


class FFmpegUtils:
    """Audio va video fayllarni FFmpeg yordamida qayta ishlash moduli."""

    @staticmethod
    def is_ffmpeg_installed() -> bool:
        """Tizimda ffmpeg o'rnatilganligini tekshiradi."""
        return shutil.which("ffmpeg") is not None

    @staticmethod
    async def extract_audio_from_video(video_path: Path, output_audio_path: Path | None = None) -> Path:
        """Videodan audio yo'lakchasini ajratib oladi (masalan, dumaloq video xabarlar uchun)."""
        if output_audio_path is None:
            output_audio_path = video_path.with_suffix(".mp3")

        cmd = [
            "ffmpeg",
            "-y",  # mavjud faylni qayta yozish
            "-i", str(video_path),
            "-vn",  # videoni o'chirish
            "-acodec", "libmp3lame",
            "-q:a", "2",
            str(output_audio_path)
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.communicate()

        if output_audio_path.exists() and output_audio_path.stat().st_size > 0:
            return output_audio_path
        return video_path

    @staticmethod
    async def convert_to_mp3(input_path: Path, output_path: Path | None = None) -> Path:
        """Ixtiyoriy audio formatni (ogg, oga, opus, wav) standart mp3 ga o'tkazadi."""
        if output_path is None:
            output_path = input_path.with_suffix(".mp3")

        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_path),
            "-acodec", "libmp3lame",
            "-ab", "128k",
            str(output_path)
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.communicate()

        if output_path.exists() and output_path.stat().st_size > 0:
            return output_path
        return input_path


ffmpeg_utils = FFmpegUtils()
