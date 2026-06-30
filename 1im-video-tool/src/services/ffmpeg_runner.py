import subprocess
from collections.abc import Callable
from pathlib import Path

from src.utils.resource_path import resource_path


class FFmpegError(RuntimeError):
    pass


def ffmpeg_path() -> Path:
    return resource_path("bin", "ffmpeg.exe")


def ffmpeg_available() -> bool:
    return ffmpeg_path().exists()


def run_ffmpeg(
    command: list[str],
    duration: float | None,
    on_progress: Callable[[float], None],
    should_cancel: Callable[[], bool],
) -> None:
    executable = ffmpeg_path()
    if not executable.exists():
        raise FFmpegError("FFmpeg를 찾을 수 없습니다.")
    full_command = [str(executable), *command]
    process = subprocess.Popen(
        full_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    assert process.stdout is not None
    return_code = 0
    try:
        for line in process.stdout:
            if should_cancel():
                process.terminate()
                raise FFmpegError("사용자가 작업을 취소했습니다.")
            if duration and line.startswith("out_time_ms="):
                out_time = int(line.partition("=")[2].strip() or "0") / 1_000_000
                on_progress(max(0.0, min(1.0, out_time / duration)))
        return_code = process.wait()
    finally:
        if process.poll() is None:
            process.terminate()
    if return_code != 0:
        raise FFmpegError("처리 중 오류가 발생했습니다. 상세 로그를 확인하세요.")


def run_command_sequence(
    commands: list[list[str]],
    duration: float | None,
    on_progress: Callable[[float], None],
    should_cancel: Callable[[], bool],
) -> None:
    total = len(commands)
    for index, command in enumerate(commands):
        base = index / total
        span = 1 / total
        run_ffmpeg(command, duration, lambda p: on_progress(base + p * span), should_cancel)
