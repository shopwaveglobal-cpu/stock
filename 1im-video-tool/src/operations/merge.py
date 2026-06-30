from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

from src.models.media_info import MediaInfo
from src.operations.common import overwrite_output, progress_flags


def can_fast_concat(infos: list[MediaInfo]) -> bool:
    if len(infos) < 2 or not infos[0].video:
        return False
    first_video = infos[0].video
    first_audio = infos[0].audio
    for info in infos[1:]:
        if not info.video:
            return False
        if (
            info.video.codec != first_video.codec
            or info.video.width != first_video.width
            or info.video.height != first_video.height
            or round(info.video.fps, 2) != round(first_video.fps, 2)
            or bool(info.audio) != bool(first_audio)
        ):
            return False
        if info.audio and first_audio and info.audio.codec != first_audio.codec:
            return False
    return True


def build_fast_merge_command(infos: list[MediaInfo], output: Path) -> tuple[list[str], Path]:
    list_path = Path(gettempdir()) / f"1im_concat_{uuid4().hex}.txt"
    list_path.write_text(
        "\n".join(f"file '{info.path.as_posix()}'" for info in infos),
        encoding="utf-8",
    )
    return [
        *progress_flags(),
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_path),
        "-c",
        "copy",
        *overwrite_output(output),
    ], list_path


def build_compat_merge_command(infos: list[MediaInfo], output: Path) -> list[str]:
    first_video = infos[0].video
    width = first_video.width if first_video else 1280
    height = first_video.height if first_video else 720
    command: list[str] = [*progress_flags()]
    for info in infos:
        command += ["-i", str(info.path)]
    filter_parts = []
    concat_inputs = []
    for index, info in enumerate(infos):
        video_label = f"v{index}"
        audio_label = f"a{index}"
        filter_parts.append(
            f"[{index}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps=30,setsar=1[{video_label}]"
        )
        if info.has_audio:
            filter_parts.append(f"[{index}:a]aresample=48000[{audio_label}]")
        else:
            filter_parts.append(f"anullsrc=channel_layout=stereo:sample_rate=48000,atrim=0:{info.duration}[{audio_label}]")
        concat_inputs.append(f"[{video_label}][{audio_label}]")
    filter_parts.append(f"{''.join(concat_inputs)}concat=n={len(infos)}:v=1:a=1[v][a]")
    return [
        *command,
        "-filter_complex",
        ";".join(filter_parts),
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        *overwrite_output(output),
    ]
