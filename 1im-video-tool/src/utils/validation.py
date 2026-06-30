from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".mov",
    ".mp4",
    ".m4v",
    ".mkv",
    ".webm",
    ".avi",
    ".wmv",
    ".mts",
    ".m2ts",
    ".3gp",
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
