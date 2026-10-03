"""main.py — 나스닥 브리핑 카드 생성 및 Slack 전송"""

import sys
import json
import pytz
from datetime import datetime
from pathlib import Path

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

import data_fetcher as df
import checkpoint_generator as cg
from card_renderer import build_context, render_card
from slack_sender import send_card

KST = pytz.timezone("Asia/Seoul")
CHECKPOINT_FILE = BASE_DIR / "data" / "checkpoints.json"
DAYS_KO = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}


def load_prev_checkpoints():
    try:
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_checkpoints(checkpoints, date_str):
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {"date": date_str, "checkpoints": checkpoints}
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def build_verification(prev_data, current_indices):
    """전날 체크포인트 vs 실제 결과 검증"""
    if not prev_data:
        return []
    nasdaq_pct = next((i["pct"] for i in current_indices if i["name"] == "NASDAQ"), 0)
    result = []
    icons = {"bullish": "✅", "partial": "⚠️", "miss": "❌"}

    for cp in prev_data.get("checkpoints", []):
        title = cp.get("title", "")
        cp_type = cp.get("type", "quant")

        # 단순 규칙: 상승 예측 vs 실제
        if cp_type == "quant":
            if "강세" in title or "반등" in title:
                if nasdaq_pct > 0.5:
                    icon, reason = icons["bullish"], f"나스닥 {nasdaq_pct:+.2f}% 상승 — 예측 적중"
                elif nasdaq_pct > -0.5:
                    icon, reason = icons["partial"], f"나스닥 {nasdaq_pct:+.2f}% 보합 — 부분 적중"
                else:
                    icon, reason = icons["miss"], f"나스닥 {nasdaq_pct:+.2f}% 하락 — 예측 빗나감"
            elif "조정" in title or "경고" in title or "하락" in title:
                if nasdaq_pct < -0.5:
                    icon, reason = icons["bullish"], f"나스닥 {nasdaq_pct:+.2f}% 하락 — 예측 적중"
                elif nasdaq_pct < 0.5:
                    icon, reason = icons["partial"], f"나스닥 {nasdaq_pct:+.2f}% 보합 — 부분 적중"
                else:
                    icon, reason = icons["miss"], f"나스닥 {nasdaq_pct:+.2f}% 상승 — 예측 빗나감"
            else:
                icon, reason = icons["partial"], f"나스닥 {nasdaq_pct:+.2f}% — 결과 확인"
        else:
            icon, reason = "📰", "뉴스 기반 체크포인트 — 결과 기록"

        result.append({"icon": icon, "title": title, "reason": reason})

    return result


def main():
    now = datetime.now(KST)
    day_ko = DAYS_KO[now.weekday()]
    date_ko = now.strftime(f"%Y년 %m월 %d일 ({day_ko})")
    date_en = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%H:%M KST")

    print(f"\n{'='*40}")
    print(f"  나스닥 브리핑 시작 — {date_ko}")
    print(f"{'='*40}")

    # 1. 데이터 수집
    raw = df.fetch_all()

    # 2. 체크포인트 생성
    print("  체크포인트 생성...")
    checkpoints = cg.generate_quant_checkpoints(
        raw["indices"], raw["sectors"], raw["fear_greed"]
    )
    news_cp = cg.generate_news_checkpoint(raw["news_raw"])
    checkpoints.append(news_cp)

    # 3. 전날 예측 검증
    print("  전날 예측 검증...")
    prev = load_prev_checkpoints()
    verification = build_verification(prev, raw["indices"])

    # 4. 체크포인트 저장 (내일 검증용)
    save_checkpoints(checkpoints, date_en)

    # 5. 카드 렌더링
    print("  카드 렌더링...")
    data = {**raw, "checkpoints": checkpoints, "verification": verification}
    context = build_context(data, date_ko, date_en, timestamp)
    out_path = str(BASE_DIR / "output" / f"market_card_{date_en}.png")
    render_card(context, out_path)

    # 6. Slack 전송
    print("  Slack 전송...")
    success = send_card(out_path, date_ko)

    print(f"\n{'='*40}")
    print(f"  {'완료 ✅' if success else '전송 실패 ❌'}")
    print(f"{'='*40}\n")


if __name__ == "__main__":
    main()
