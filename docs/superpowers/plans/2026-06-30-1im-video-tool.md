# 1IM Video Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete Windows-only Tkinter desktop app for local FFmpeg video conversion, compression, audio extraction, trimming, and merging.

**Architecture:** Create a new isolated project at `C:\Users\log\Desktop\code\1im-video-tool`. The app separates Tkinter UI, FFmpeg/FFprobe services, operation command builders, queue management, path/log services, and typed models. Unit tests cover validation, output paths, and command generation without needing real media files.

**Tech Stack:** Python 3.12+, Tkinter/ttk, optional `tkinterdnd2`, FFmpeg/FFprobe local executables, pytest, PyInstaller, Windows batch scripts.

---

## File Structure

- `1im-video-tool/app.py`: application entry point.
- `1im-video-tool/requirements.txt`: Python dependencies.
- `1im-video-tool/README.md`: Korean user/developer guide.
- `1im-video-tool/build.bat`: create venv, install, test, build portable zip.
- `1im-video-tool/run_dev.bat`: run app in development.
- `1im-video-tool/THIRD_PARTY_NOTICES.md`: FFmpeg and dependency notices.
- `1im-video-tool/LICENSES/`: placeholder directory for third-party license text.
- `1im-video-tool/bin/`: bundled `ffmpeg.exe` and `ffprobe.exe` when found locally.
- `1im-video-tool/src/models/job.py`: job/result dataclasses and enums.
- `1im-video-tool/src/models/media_info.py`: ffprobe media metadata dataclasses.
- `1im-video-tool/src/utils/resource_path.py`: PyInstaller-safe resource lookup.
- `1im-video-tool/src/utils/validation.py`: extensions, seconds, target-size, and recursive-output validation.
- `1im-video-tool/src/services/path_service.py`: default output and collision-safe filenames.
- `1im-video-tool/src/services/ffprobe_service.py`: ffprobe JSON inspection.
- `1im-video-tool/src/services/ffmpeg_runner.py`: subprocess execution and progress parsing.
- `1im-video-tool/src/services/logger_service.py`: UTF-8 queue logs.
- `1im-video-tool/src/services/queue_manager.py`: worker-thread job processing.
- `1im-video-tool/src/operations/common.py`: shared FFmpeg command helpers.
- `1im-video-tool/src/operations/convert.py`: conversion jobs and commands.
- `1im-video-tool/src/operations/compress.py`: target-size compression jobs and commands.
- `1im-video-tool/src/operations/extract_audio.py`: audio extraction jobs and commands.
- `1im-video-tool/src/operations/trim.py`: trim jobs and commands.
- `1im-video-tool/src/operations/merge.py`: merge command planning.
- `1im-video-tool/src/ui/theme.py`: ttk styles.
- `1im-video-tool/src/ui/dialogs.py`: about, notices, warning dialogs.
- `1im-video-tool/src/ui/main_window.py`: main UI and event coordination.
- `1im-video-tool/tests/test_validation.py`: validation tests.
- `1im-video-tool/tests/test_path_service.py`: output path tests.
- `1im-video-tool/tests/test_command_builders.py`: FFmpeg command tests.

## Task 1: Scaffold Project And Static Files

**Files:**
- Create: all directories listed above.
- Create: `1im-video-tool/app.py`
- Create: `1im-video-tool/requirements.txt`
- Create: `1im-video-tool/README.md`
- Create: `1im-video-tool/THIRD_PARTY_NOTICES.md`
- Create: `1im-video-tool/build.bat`
- Create: `1im-video-tool/run_dev.bat`

- [ ] **Step 1: Create project directories**

Run:

```powershell
New-Item -ItemType Directory -Force -Path .\1im-video-tool, .\1im-video-tool\bin, .\1im-video-tool\LICENSES, .\1im-video-tool\src\ui, .\1im-video-tool\src\services, .\1im-video-tool\src\operations, .\1im-video-tool\src\models, .\1im-video-tool\src\utils, .\1im-video-tool\tests
```

Expected: all directories exist under `C:\Users\log\Desktop\code\1im-video-tool`.

- [ ] **Step 2: Create requirements**

Create `requirements.txt`:

```text
pyinstaller>=6.0
pytest>=8.0
tkinterdnd2>=0.4.2
```

- [ ] **Step 3: Create app entry point**

Create `app.py`:

```python
from src.ui.main_window import main


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Create batch scripts**

Create `run_dev.bat`:

```bat
@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python app.py
```

Create `build.bat`:

```bat
@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if not exist bin\ffmpeg.exe (
  echo Missing bin\ffmpeg.exe
  exit /b 1
)
if not exist bin\ffprobe.exe (
  echo Missing bin\ffprobe.exe
  exit /b 1
)
python -m pytest -q
python -m PyInstaller --noconfirm --onedir --windowed --name "1IM Video Tool" --add-binary "bin\ffmpeg.exe;bin" --add-binary "bin\ffprobe.exe;bin" app.py
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Force -Path 'dist\1IM Video Tool' -DestinationPath 'dist\1IM_Video_Tool_Portable.zip'"
```

- [ ] **Step 5: Create Korean README and notices**

README must include what the tool does, supported features, dev run, build, output location, local-only privacy, known limitations, and FFmpeg licensing reminder.

- [ ] **Step 6: Verify scaffold imports fail only because UI is not created yet**

Run:

```powershell
cd .\1im-video-tool
python app.py
```

Expected: import error for `src.ui.main_window`, confirming the entry point is wired to the planned module.

## Task 2: Models And Validation

**Files:**
- Create: `1im-video-tool/src/models/job.py`
- Create: `1im-video-tool/src/models/media_info.py`
- Create: `1im-video-tool/src/utils/validation.py`
- Test: `1im-video-tool/tests/test_validation.py`

- [ ] **Step 1: Write validation tests**

Create `tests/test_validation.py`:

```python
from pathlib import Path

import pytest

from src.utils.validation import (
    is_supported_media,
    is_inside_output_folder,
    parse_seconds,
    parse_target_size_mb,
    validate_trim_range,
)


def test_supported_media_extensions_are_case_insensitive():
    assert is_supported_media(Path("clip.MOV"))
    assert is_supported_media(Path("clip.mp4"))
    assert not is_supported_media(Path("notes.txt"))


def test_output_folder_detection_skips_recursive_outputs():
    path = Path("D:/video/1IM Video Tool Output/변환/clip.mp4")
    assert is_inside_output_folder(path)
    assert not is_inside_output_folder(Path("D:/video/clip.mp4"))


def test_parse_seconds_accepts_decimal_values():
    assert parse_seconds("1.5") == 1.5
    assert parse_seconds("0") == 0


def test_parse_seconds_rejects_negative_values():
    with pytest.raises(ValueError):
        parse_seconds("-1")


def test_parse_target_size_mb_accepts_presets_and_gb():
    assert parse_target_size_mb("25 MB") == 25
    assert parse_target_size_mb("1 GB") == 1024
    assert parse_target_size_mb("300") == 300


def test_trim_range_must_be_shorter_than_duration():
    validate_trim_range(1, 2, 10)
    with pytest.raises(ValueError):
        validate_trim_range(5, 5, 10)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_validation.py -q
```

Expected: FAIL because `src.utils.validation` is not implemented.

- [ ] **Step 3: Implement models**

Create `src/models/media_info.py`:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VideoStream:
    codec: str
    width: int
    height: int
    fps: float
    pix_fmt: str | None = None


@dataclass(frozen=True)
class AudioStream:
    codec: str
    sample_rate: int | None = None
    channels: int | None = None


@dataclass(frozen=True)
class MediaInfo:
    path: Path
    duration: float
    video: VideoStream | None
    audio: AudioStream | None

    @property
    def has_audio(self) -> bool:
        return self.audio is not None
```

Create `src/models/job.py`:

```python
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELED = "canceled"


@dataclass
class JobResult:
    source: Path
    output: Path | None
    status: JobStatus
    message: str


@dataclass
class Job:
    source: Path
    output: Path
    feature_name: str
    duration: float | None
    command_factory: Callable[[], list[str]]
    status: JobStatus = JobStatus.PENDING
    message: str = ""
    extra_outputs: list[Path] = field(default_factory=list)
```

- [ ] **Step 4: Implement validation**

Create `src/utils/validation.py` with:

```python
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".mov", ".mp4", ".m4v", ".mkv", ".webm", ".avi", ".wmv", ".mts", ".m2ts", ".3gp"
}
OUTPUT_FOLDER_NAME = "1IM Video Tool Output"


def is_supported_media(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def is_inside_output_folder(path: Path) -> bool:
    return OUTPUT_FOLDER_NAME.casefold() in [part.casefold() for part in path.parts]


def parse_seconds(value: str) -> float:
    try:
        seconds = float(value.strip())
    except ValueError as exc:
        raise ValueError("초 단위 숫자를 입력하세요.") from exc
    if seconds < 0:
        raise ValueError("0 이상의 값을 입력하세요.")
    return seconds


def parse_target_size_mb(value: str) -> int:
    normalized = value.strip().upper()
    if normalized.endswith("GB"):
        number = float(normalized[:-2].strip())
        return int(number * 1024)
    if normalized.endswith("MB"):
        number = float(normalized[:-2].strip())
        return int(number)
    number = float(normalized)
    if number <= 0:
        raise ValueError("목표 용량은 0보다 커야 합니다.")
    return int(number)


def validate_trim_range(start_seconds: float, end_seconds: float, duration: float) -> None:
    if start_seconds < 0 or end_seconds < 0:
        raise ValueError("잘라낼 시간은 0 이상이어야 합니다.")
    if start_seconds + end_seconds >= duration:
        raise ValueError("앞/뒤에서 자를 시간의 합이 영상 길이보다 짧아야 합니다.")
```

- [ ] **Step 5: Run validation tests**

Run:

```powershell
python -m pytest tests/test_validation.py -q
```

Expected: PASS.

## Task 3: Resource And Path Services

**Files:**
- Create: `1im-video-tool/src/utils/resource_path.py`
- Create: `1im-video-tool/src/services/path_service.py`
- Test: `1im-video-tool/tests/test_path_service.py`

- [ ] **Step 1: Write path tests**

Create `tests/test_path_service.py`:

```python
from pathlib import Path

from src.services.path_service import default_output_dir, unique_output_path


def test_default_output_dir_uses_source_parent_and_feature_name():
    result = default_output_dir(Path("D:/clips/a.mp4"), "변환")
    assert result == Path("D:/clips/1IM Video Tool Output/변환")


def test_unique_output_path_returns_base_when_available(tmp_path):
    target = unique_output_path(tmp_path, "clip", ".mp4")
    assert target == tmp_path / "clip.mp4"


def test_unique_output_path_adds_number_when_exists(tmp_path):
    (tmp_path / "clip.mp4").write_text("x", encoding="utf-8")
    target = unique_output_path(tmp_path, "clip", ".mp4")
    assert target == tmp_path / "clip_1.mp4"
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_path_service.py -q
```

Expected: FAIL because service is missing.

- [ ] **Step 3: Implement resource path and path service**

Create `src/utils/resource_path.py`:

```python
import sys
from pathlib import Path


def app_root() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def resource_path(*parts: str) -> Path:
    return app_root().joinpath(*parts)
```

Create `src/services/path_service.py`:

```python
from pathlib import Path


OUTPUT_ROOT = "1IM Video Tool Output"


def default_output_dir(source: Path, feature_name: str) -> Path:
    return source.parent / OUTPUT_ROOT / feature_name


def unique_output_path(directory: Path, stem: str, suffix: str) -> Path:
    candidate = directory / f"{stem}{suffix}"
    if not candidate.exists():
        return candidate
    index = 1
    while True:
        candidate = directory / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1
```

- [ ] **Step 4: Run path tests**

Run:

```powershell
python -m pytest tests/test_path_service.py -q
```

Expected: PASS.

## Task 4: FFprobe And FFmpeg Services

**Files:**
- Create: `1im-video-tool/src/services/ffprobe_service.py`
- Create: `1im-video-tool/src/services/ffmpeg_runner.py`
- Create: `1im-video-tool/src/services/logger_service.py`

- [ ] **Step 1: Implement ffprobe service**

Create `src/services/ffprobe_service.py`:

```python
import json
import subprocess
from pathlib import Path

from src.models.media_info import AudioStream, MediaInfo, VideoStream
from src.utils.resource_path import resource_path


class FFprobeError(RuntimeError):
    pass


def ffprobe_path() -> Path:
    return resource_path("bin", "ffprobe.exe")


def parse_fps(value: str | None) -> float:
    if not value or value == "0/0":
        return 0.0
    numerator, denominator = value.split("/")
    return float(numerator) / float(denominator)


def inspect_media(path: Path) -> MediaInfo:
    executable = ffprobe_path()
    if not executable.exists():
        raise FFprobeError("FFprobe를 찾을 수 없습니다.")
    command = [
        str(executable), "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(path)
    ]
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.returncode != 0:
        raise FFprobeError("파일을 읽을 수 없거나 손상되었습니다.")
    data = json.loads(completed.stdout)
    duration = float(data.get("format", {}).get("duration") or 0)
    video = None
    audio = None
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video" and video is None:
            video = VideoStream(
                codec=stream.get("codec_name", ""),
                width=int(stream.get("width") or 0),
                height=int(stream.get("height") or 0),
                fps=parse_fps(stream.get("avg_frame_rate")),
                pix_fmt=stream.get("pix_fmt"),
            )
        if stream.get("codec_type") == "audio" and audio is None:
            audio = AudioStream(
                codec=stream.get("codec_name", ""),
                sample_rate=int(stream["sample_rate"]) if stream.get("sample_rate") else None,
                channels=int(stream["channels"]) if stream.get("channels") else None,
            )
    return MediaInfo(path=path, duration=duration, video=video, audio=audio)
```

- [ ] **Step 2: Implement FFmpeg runner**

Create `src/services/ffmpeg_runner.py`:

```python
import subprocess
from collections.abc import Callable
from pathlib import Path

from src.utils.resource_path import resource_path


class FFmpegError(RuntimeError):
    pass


def ffmpeg_path() -> Path:
    return resource_path("bin", "ffmpeg.exe")


def run_ffmpeg(command: list[str], duration: float | None, on_progress: Callable[[float], None], should_cancel: Callable[[], bool]) -> None:
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
    try:
        for line in process.stdout:
            if should_cancel():
                process.terminate()
                raise FFmpegError("사용자가 작업을 취소했습니다.")
            if duration and line.startswith("out_time_ms="):
                value = int(line.partition("=")[2].strip() or "0") / 1_000_000
                on_progress(max(0.0, min(1.0, value / duration)))
        return_code = process.wait()
    finally:
        if process.poll() is None:
            process.terminate()
    if return_code != 0:
        raise FFmpegError("처리 중 오류가 발생했습니다. 상세 로그를 확인하세요.")
```

- [ ] **Step 3: Implement logger service**

Create `src/services/logger_service.py`:

```python
from datetime import datetime
from pathlib import Path

from src.models.job import JobResult


def write_queue_log(output_root: Path, feature_name: str, results: list[JobResult]) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = output_root / f"{feature_name}_{stamp}.log"
    lines = [f"1IM Video Tool - {feature_name}", f"완료 시각: {datetime.now():%Y-%m-%d %H:%M:%S}", ""]
    for result in results:
        lines.append(f"[{result.status.value}] {result.source}")
        if result.output:
            lines.append(f"출력: {result.output}")
        lines.append(f"메시지: {result.message}")
        lines.append("")
    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path
```

## Task 5: Operation Command Builders

**Files:**
- Create: `1im-video-tool/src/operations/common.py`
- Create: `1im-video-tool/src/operations/convert.py`
- Create: `1im-video-tool/src/operations/compress.py`
- Create: `1im-video-tool/src/operations/extract_audio.py`
- Create: `1im-video-tool/src/operations/trim.py`
- Create: `1im-video-tool/src/operations/merge.py`
- Test: `1im-video-tool/tests/test_command_builders.py`

- [ ] **Step 1: Write command builder tests**

Create `tests/test_command_builders.py`:

```python
from pathlib import Path

from src.models.media_info import AudioStream, MediaInfo, VideoStream
from src.operations.compress import build_compress_command
from src.operations.convert import build_convert_command
from src.operations.extract_audio import build_extract_audio_command
from src.operations.trim import build_trim_command


INFO = MediaInfo(
    path=Path("input.mov"),
    duration=100,
    video=VideoStream(codec="h264", width=1920, height=1080, fps=30),
    audio=AudioStream(codec="aac", sample_rate=48000, channels=2),
)


def test_convert_command_uses_transcoding_not_rename():
    command = build_convert_command(INFO, Path("out.mp4"), "mp4", "균형")
    assert "-c:v" in command
    assert "libx264" in command
    assert str(Path("out.mp4")) in command


def test_extract_audio_mp3_command_uses_audio_codec():
    command = build_extract_audio_command(INFO, Path("out.mp3"), "MP3", "일반")
    assert "-vn" in command
    assert "libmp3lame" in command


def test_trim_command_contains_start_and_duration():
    command = build_trim_command(INFO, Path("trim.mp4"), 2.5, 1.5)
    assert "-ss" in command
    assert "-t" in command
    assert "96.0" in command


def test_compress_command_calculates_bitrate():
    first_pass, second_pass, warning = build_compress_command(INFO, Path("small.mp4"), 25)
    assert first_pass is not None
    assert "-b:v" in second_pass
    assert warning is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_command_builders.py -q
```

Expected: FAIL because operation modules do not exist.

- [ ] **Step 3: Implement shared FFmpeg helpers and operation builders**

Implement `src/operations/common.py` with CRF maps, audio bitrate maps, `progress_flags()`, and `h264_aac_output_args()`.

Required functions:

```python
def progress_flags() -> list[str]:
    return ["-hide_banner", "-y", "-progress", "pipe:1", "-nostats"]


def h264_aac_args(crf: int = 23) -> list[str]:
    return ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k"]
```

Implement each operation so tests pass and commands use input/output paths as strings, never shell strings.

- [ ] **Step 4: Run command builder tests**

Run:

```powershell
python -m pytest tests/test_command_builders.py -q
```

Expected: PASS.

## Task 6: Queue Manager

**Files:**
- Create: `1im-video-tool/src/services/queue_manager.py`

- [ ] **Step 1: Implement worker-thread queue manager**

Create `queue_manager.py` with:

```python
import queue
import threading
from collections.abc import Callable

from src.models.job import Job, JobResult, JobStatus
from src.services.ffmpeg_runner import run_ffmpeg


ProgressCallback = Callable[[dict], None]


class QueueManager:
    def __init__(self, on_event: ProgressCallback) -> None:
        self.on_event = on_event
        self._cancel_current = threading.Event()
        self._stop_all = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self, jobs: list[Job]) -> None:
        self._cancel_current.clear()
        self._stop_all.clear()
        self._thread = threading.Thread(target=self._run, args=(jobs,), daemon=True)
        self._thread.start()

    def cancel_current(self) -> None:
        self._cancel_current.set()

    def stop_all(self) -> None:
        self._stop_all.set()
        self._cancel_current.set()

    def _run(self, jobs: list[Job]) -> None:
        results: list[JobResult] = []
        total = len(jobs)
        for index, job in enumerate(jobs, start=1):
            if self._stop_all.is_set():
                break
            self._cancel_current.clear()
            self.on_event({"type": "job_start", "index": index, "total": total, "job": job})
            try:
                run_ffmpeg(job.command_factory(), job.duration, lambda p: self.on_event({"type": "progress", "progress": p}), self._cancel_current.is_set)
                result = JobResult(job.source, job.output, JobStatus.SUCCESS, "완료")
            except Exception as exc:
                status = JobStatus.CANCELED if self._cancel_current.is_set() else JobStatus.FAILED
                result = JobResult(job.source, job.output, status, str(exc))
            results.append(result)
            self.on_event({"type": "job_done", "result": result})
        self.on_event({"type": "queue_done", "results": results})
```

## Task 7: Tkinter UI

**Files:**
- Create: `1im-video-tool/src/ui/theme.py`
- Create: `1im-video-tool/src/ui/dialogs.py`
- Create: `1im-video-tool/src/ui/main_window.py`

- [ ] **Step 1: Implement theme**

Create dark ttk styles with background `#181818`, panel `#242424`, foreground `#F5F5F5`, accent `#F37021`.

- [ ] **Step 2: Implement dialogs**

Create about dialog showing version, FFmpeg/FFprobe status, local-only privacy statement, and button to open `THIRD_PARTY_NOTICES.md`.

- [ ] **Step 3: Implement main window**

Main window responsibilities:

- Feature selector.
- File/folder add, remove selected, clear.
- Optional drag-and-drop registration guarded by import fallback.
- Feature-specific controls.
- Output location display/change.
- Start disabled until valid files/options exist.
- Queue event polling via `after`.
- Result list with success/failure/output path.
- Open output folder button using `subprocess.Popen(["explorer", path])`.

- [ ] **Step 4: Run app**

Run:

```powershell
python app.py
```

Expected: the desktop window opens without blocking the terminal after close and shows FFmpeg status.

## Task 8: FFmpeg Discovery And Bundling

**Files:**
- Modify: `1im-video-tool/bin/`

- [ ] **Step 1: Check PATH**

Run:

```powershell
where.exe ffmpeg
where.exe ffprobe
ffmpeg -version
ffprobe -version
```

Expected in current environment: not found. Continue with common path search.

- [ ] **Step 2: Search common local install locations**

Run:

```powershell
Get-ChildItem -Path "$env:ProgramFiles", "$env:ProgramFiles(x86)", "$env:LOCALAPPDATA", "$env:USERPROFILE" -Recurse -Filter ffmpeg.exe -ErrorAction SilentlyContinue | Select-Object -First 10 -ExpandProperty FullName
```

Run the same for `ffprobe.exe`. If both are found in the same FFmpeg installation, copy them to `bin\`.

- [ ] **Step 3: Verify copied binaries**

Run:

```powershell
.\bin\ffmpeg.exe -version
.\bin\ffprobe.exe -version
```

Expected: version output for each executable.

## Task 9: Final Verification And Packaging

**Files:**
- Modify as needed based on verification findings.

- [ ] **Step 1: Install dependencies**

Run:

```powershell
cd .\1im-video-tool
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Expected: dependencies install successfully.

- [ ] **Step 2: Run unit tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 3: Run app locally**

Run:

```powershell
.\.venv\Scripts\python.exe app.py
```

Expected: app opens and reports FFmpeg/FFprobe detected if binaries exist.

- [ ] **Step 4: Test each feature with local sample video**

Find a local sample:

```powershell
Get-ChildItem -Path "$env:USERPROFILE" -Recurse -Include *.mp4,*.mov,*.mkv,*.webm -ErrorAction SilentlyContinue | Select-Object -First 5 -ExpandProperty FullName
```

Use one suitable file to manually test conversion, compression, audio extraction, trimming, and merge. If no local video exists, record this as not fully tested.

- [ ] **Step 5: Build portable package**

Run:

```powershell
.\build.bat
```

Expected:

```text
dist\1IM Video Tool\
dist\1IM_Video_Tool_Portable.zip
```

- [ ] **Step 6: Report results**

Final report must include files created, test results, build output location, any feature not fully tested, and exact rebuild command:

```powershell
cd C:\Users\log\Desktop\code\1im-video-tool
.\build.bat
```
