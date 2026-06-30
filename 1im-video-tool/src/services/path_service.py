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
