from pathlib import Path
from uuid import uuid4

from src.models.media_info import MediaInfo
from src.operations.common import input_args, overwrite_output, progress_flags


MIN_USABLE_VIDEO_KBPS = 180


def _target_video_kbps(duration: float, target_size_mb: int, audio_kbps: int) -> int:
    total_kbits = target_size_mb * 8192
    total_kbps = int(total_kbits / max(duration, 1))
    return max(1, total_kbps - audio_kbps)


def build_compress_command(info: MediaInfo, output: Path, target_size_mb: int) -> tuple[list[str], list[str], str | None]:
    audio_kbps = 128 if info.has_audio else 0
    video_kbps = _target_video_kbps(info.duration, target_size_mb, audio_kbps)
    warning = None
    if video_kbps < MIN_USABLE_VIDEO_KBPS:
        warning = "목표 용량이 너무 작아 화질이 크게 낮아질 수 있습니다."
    passlog = str(output.with_suffix(f".{uuid4().hex}.pass"))
    common = [
        *progress_flags(),
        *input_args(info.path),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-b:v",
        f"{video_kbps}k",
    ]
    audio_args = ["-c:a", "aac", "-b:a", f"{audio_kbps}k"] if info.has_audio else ["-an"]
    first_pass = [
        *common,
        "-pass",
        "1",
        "-passlogfile",
        passlog,
        "-an",
        "-f",
        "mp4",
        "NUL",
    ]
    second_pass = [
        *common,
        "-pass",
        "2",
        "-passlogfile",
        passlog,
        *audio_args,
        "-pix_fmt",
        "yuv420p",
        *overwrite_output(output),
    ]
    return first_pass, second_pass, warning
