from pathlib import Path


QUALITY_CRF = {
    "고화질": 18,
    "균형": 23,
    "작은 용량": 28,
}

AUDIO_QUALITY = {
    "고음질": "256k",
    "일반": "192k",
    "작은 용량": "128k",
}


def progress_flags() -> list[str]:
    return ["-hide_banner", "-y", "-progress", "pipe:1", "-nostats"]


def input_args(path: Path) -> list[str]:
    return ["-i", str(path)]


def h264_aac_args(crf: int = 23, audio: bool = True) -> list[str]:
    args = ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p"]
    if audio:
        args += ["-c:a", "aac", "-b:a", "192k"]
    else:
        args += ["-an"]
    return args


def overwrite_output(path: Path) -> list[str]:
    return [str(path)]
