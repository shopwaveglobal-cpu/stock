# 1IM Video Tool Design

## Goal

Build `1IM Video Tool`, a Windows-only local desktop video utility for non-technical Korean users. The app hides FFmpeg commands, processes files locally, never overwrites originals, and produces a portable Windows package.

The project will live in `C:\Users\log\Desktop\code\1im-video-tool` so existing workspace files remain untouched.

## Scope

V1 includes:

- Video format conversion to MP4, MOV, or MKV using H.264 + AAC.
- Video compression to a target size using duration-based bitrate calculation and two-pass encoding where appropriate.
- Audio extraction to MP3, M4A, or WAV.
- Accurate trimming from the beginning and end of each video.
- Merging selected videos into one MP4, with a fast concat path and an automatic compatibility path.
- Korean Tkinter UI with dark styling and `#F37021` accent.
- Local FFmpeg/FFprobe bundling from verified executables already present on the PC.
- Unit tests for validation and command generation.
- PyInstaller `--onedir --windowed` packaging with a portable zip.

Out of scope for V1:

- Cloud processing, accounts, analytics, telemetry, or network calls.
- Electron, web UI, or a browser-based application.
- Obscure output presets such as AVI, FLV, or WMV.
- One-file executable packaging.

## Architecture

The app will use a small layered structure:

- `app.py` starts the Tkinter application.
- `src/ui/` owns the main window, theme, and dialogs.
- `src/services/` owns FFmpeg execution, ffprobe inspection, queue orchestration, output paths, and logging.
- `src/operations/` owns feature-specific command builders and job creation.
- `src/models/` defines typed job and media-info objects.
- `src/utils/` contains resource-path and validation helpers.
- `tests/` covers validation and FFmpeg command generation without requiring real video processing.

FFmpeg command construction will be centralized around reusable helpers so every operation returns argument arrays only. `subprocess` will never use `shell=True`.

## UI Design

The main window will present:

- App title and subtitle.
- A vertical feature selector for conversion, compression, audio extraction, trimming, and merging.
- File and folder add buttons, optional drag-and-drop when `tkinterdnd2` is available, remove/clear controls, and a selected-file count.
- Feature-specific settings that update when the selected feature changes.
- Output location controls with the default set to `1IM Video Tool Output/<feature name>/` beside each source file.
- Start, cancel-current, and stop-all controls.
- Progress text, progress bar, result list, and open-output-folder button.
- Settings/about dialog with app version, FFmpeg status, local-only privacy statement, and third-party notices link.

The UI will use clean Korean labels. The prompt contains mojibake text for several labels, so implementation will use corrected Korean text that matches the intended meaning.

## Data Flow

1. User adds files or a folder.
2. The app filters supported media extensions and skips anything inside `1IM Video Tool Output`.
3. `ffprobe_service` validates each file and reads duration, stream, codec, audio, dimensions, and FPS details.
4. The selected operation creates one or more `Job` records.
5. `queue_manager` runs jobs on a worker thread.
6. `ffmpeg_runner` executes FFmpeg with argument arrays and parses progress from stdout.
7. UI updates happen through Tkinter-safe queue polling on the main thread.
8. Results and a UTF-8 queue log are written after completion or stop.

## Feature Behavior

Conversion:

- Default output is MP4.
- Quality presets map to conservative CRF values.
- Audio is preserved when present; video-only files still convert.
- Unsupported or corrupt media shows a Korean error and does not stop the queue.

Compression:

- Target size presets include 25 MB through 1 GB plus custom input.
- Bitrate is calculated from ffprobe duration.
- Audio bitrate is reserved before calculating video bitrate.
- Very low video bitrates trigger a warning before processing.
- Output is MP4 H.264 + AAC.

Audio extraction:

- Defaults to MP3 at normal quality.
- M4A uses AAC, WAV uses PCM.
- Files without audio are skipped with a clear Korean result message.

Trim:

- Start and end trim accept whole seconds or decimals.
- Validation ensures start trim plus end trim is shorter than source duration.
- Output is accurately re-encoded MP4 H.264 + AAC.

Merge:

- Multiple files or one folder become a single merge list.
- Folder input is sorted by filename.
- The UI supports moving items up/down and removing items.
- Automatic mode chooses fast concat when stream properties match, otherwise normalizes to the first clip dimensions with padding, FPS 30, and silent audio as needed.

## Paths And Safety

- Original files are never overwritten or deleted.
- Output filename collisions append `_1`, `_2`, and so on.
- Korean paths, spaces, and long names are handled through `pathlib` and argument arrays.
- Files inside `1IM Video Tool Output` are skipped to avoid recursive processing.
- Logs are UTF-8 and readable, while raw FFmpeg commands stay out of the normal UI.

## Packaging

`build.bat` will:

1. Create or reuse `.venv`.
2. Install requirements.
3. Verify `bin\ffmpeg.exe` and `bin\ffprobe.exe`.
4. Run tests.
5. Build with PyInstaller using `--onedir --windowed`.
6. Include FFmpeg binaries.
7. Create `dist\1IM Video Tool\` and `dist\1IM_Video_Tool_Portable.zip`.

If FFmpeg is not found locally, the app can still be developed, but packaging will fail with an explicit message until the binaries are placed in `bin/`.

## Testing

Unit tests will cover:

- Supported extension validation.
- Output path collision behavior.
- Recursive-output-folder skipping.
- Trim duration validation.
- Command builder outputs for convert, compress, audio extraction, trim, and merge path decisions where possible.

Manual verification will attempt to:

- Run the app locally.
- Confirm FFmpeg/FFprobe detection.
- Process at least one available local video file through each feature if a suitable sample exists.
- Build the portable package after dependencies and FFmpeg binaries are available.

## Open Constraint

Initial checks showed `where.exe ffmpeg`, `where.exe ffprobe`, `ffmpeg -version`, and `ffprobe -version` did not find FFmpeg on PATH. Implementation will search common local installation locations and the workspace. If no executable is found, the project will include clear setup/build failure messages rather than downloading binaries.
