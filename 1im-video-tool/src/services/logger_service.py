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
