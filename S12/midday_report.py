"""
11:30 중간 점검 리포트
- trading_signals.xlsx(Summary) 에서 매수선 읽기
- 키움 API 로 당일 저가 실시간 조회
- 저가 기준 이격도 5% 이내 종목만 이격도 오름차순으로 표시
- 비거래일 자동 스킵
"""

import argparse
import logging
import sys
import time
import os
from datetime import datetime
from typing import Optional, List, Dict

import requests
import pandas as pd
from dotenv import load_dotenv

# 거래일 체크
from trading_day_utils import is_trading_day

# 알람 전송
from telegram_notifier import send_telegram_message
from slack_notifier import send_slack_message

load_dotenv()

# ── 로깅 설정 ─────────────────────────────────────────────────────
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ── 상수 ─────────────────────────────────────────────────────────
KIWOOM_BASE_URL = "https://api.kiwoom.com"
KIWOOM_TOKEN_URL = "https://api.kiwoom.com/oauth2/token"
MIDDAY_THRESHOLD = 5.0        # 이격도 임계값 (%)
DEFAULT_S12_SIGNAL = "output/trading_signals.xlsx"
DEFAULT_S1_SIGNAL  = "output/trading_signals_s1.xlsx"


# ── API ──────────────────────────────────────────────────────────
def get_api_token(appkey: str, secret: str) -> str:
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    body = {
        "grant_type": "client_credentials",
        "appkey": appkey,
        "secretkey": secret
    }
    response = requests.post(KIWOOM_TOKEN_URL, headers=headers, json=body, timeout=20)
    response.raise_for_status()
    data = response.json()
    token = data.get("token") or data.get("access_token")
    if not token:
        raise ValueError("토큰을 찾을 수 없습니다")
    logger.info("✓ API 토큰 획득 완료")
    return token


def get_today_price_data(ticker: str, token: str) -> Optional[Dict]:
    """
    당일 가격 데이터 조회 (현재가 / 저가 포함)
    Real_Time_Monitor 의 get_enhanced_price_data 와 동일한 패턴
    """
    try:
        url = f"{KIWOOM_BASE_URL}/api/dostk/chart"
        today = datetime.now().strftime("%Y%m%d")
        integrated_ticker = f"{ticker}_AL"

        headers = {
            "authorization": f"Bearer {token}",
            "Content-Type": "application/json;charset=UTF-8",
            "api-id": "ka10081",
            "cont-yn": "N",
            "next-key": ""
        }
        body = {
            "stk_cd": integrated_ticker,
            "base_dt": today,
            "upd_stkpc_tp": "1",
            "stex_tp": "3"
        }

        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        result = response.json()

        records = result.get("stk_dt_pole_chart_qry")
        if not records:
            return None

        latest = records[0]

        def sf(val, default=0.0):
            try:
                if val is None or val == "":
                    return default
                v = float(str(val).replace(",", ""))
                return v if not (v != v) else default   # NaN check
            except (ValueError, TypeError):
                return default

        data = {
            "current": sf(latest.get("cur_prc")),
            "low":     sf(latest.get("low_pric")),
            "high":    sf(latest.get("high_pric")),
            "open":    sf(latest.get("open_pric")),
        }

        if data["current"] <= 0 and data["low"] <= 0:
            return None

        return data

    except Exception as e:
        logger.warning(f"⚠ {ticker} 가격 조회 실패: {e}")
        return None


# ── 핵심 로직 ─────────────────────────────────────────────────────
def build_midday_rows(signal_file: str, token: str) -> List[Dict]:
    """
    시그널 파일 읽기 → 당일 저가 조회 → 이격도 계산 → 5% 이내 필터
    Returns list sorted by 이격도 ascending.
    """
    df = pd.read_excel(signal_file, sheet_name="Summary")
    rows = []

    total = len(df)
    for idx, row in df.iterrows():
        ticker = str(row.get("티커", "")).zfill(6)
        name   = str(row.get("종목명", ""))
        status = str(row.get("매수상태", "NONE") or "NONE")

        # 다음 매수 목표선 결정 (익일 기준 = 당일 적용)
        if status == "NONE":
            buy_line = row.get("1차매수선(익일)")
            차수 = "1차"
        elif status == "BOUGHT_1":
            buy_line = row.get("2차매수선(익일)")
            차수 = "2차"
        elif status == "BOUGHT_2":
            buy_line = row.get("3차매수선(익일)")
            차수 = "3차"
        else:
            # BOUGHT_3, SOLD 등: 더 이상 매수 없음 → 스킵
            continue

        try:
            buy_line = float(buy_line)
        except (TypeError, ValueError):
            continue
        if buy_line <= 0:
            continue

        logger.info(f"  [{idx+1}/{total}] {name} ({ticker}) 조회 중...")
        price_data = get_today_price_data(ticker, token)
        time.sleep(0.2)   # API 레이트 리미트

        if not price_data:
            logger.warning(f"    ⚠ 가격 데이터 없음 — 스킵")
            continue

        low = price_data["low"]
        if low <= 0:
            logger.warning(f"    ⚠ 저가 0 — 스킵")
            continue

        # 이격도 = (저가 - 매수선) / 매수선 * 100
        # 양수 = 저가가 아직 매수선 위 (매수 미체결)
        # 음수 = 저가가 매수선 터치/하회 (체결 가능성)
        dist = (low - buy_line) / buy_line * 100

        # 0% < dist ≤ 5% 인 경우만 포함
        if 0 < dist <= MIDDAY_THRESHOLD:
            rows.append({
                "종목명": name,
                "차수":   차수,
                "저가":   low,
                "매수가": buy_line,
                "이격도": dist,
            })
            logger.info(f"    ✅ 포함: 저가 {low:,.0f}  매수가 {buy_line:,.0f}  이격도 {dist:.1f}%")
        else:
            logger.info(f"    — 제외: 이격도 {dist:.1f}%")

    # 이격도 오름차순 정렬 (가장 임박한 종목이 맨 위)
    rows.sort(key=lambda x: x["이격도"])
    return rows


# ── 메시지 전송 ───────────────────────────────────────────────────
def send_midday_telegram(rows: List[Dict], system_label: str, total_stocks: int):
    now = datetime.now().strftime("%H:%M")

    msg  = f"🔍 <b>[{system_label}] 11:30 중간 점검</b>\n"
    msg += f"🕐 {now}  총 {total_stocks}종목\n"
    msg += "─────────────────────\n\n"

    if not rows:
        msg += "✅ 5% 이내 인접 종목 없음\n"
    else:
        msg += f"5% 이내 인접 <b>{len(rows)}종목</b>\n\n"
        for r in rows:
            low_s  = f"{int(r['저가']):,}"
            buy_s  = f"{int(r['매수가']):,}"
            dist_s = f"{r['이격도']:.1f}%"
            label  = f"{r['종목명']}({r['차수']})"
            msg += f"• {label}  저가 {low_s} → {buy_s}  <i>({dist_s})</i>\n"

    send_telegram_message(msg, recipients=["all"])
    logger.info(f"✓ [{system_label}] 텔레그램 중간 점검 전송 완료")


def send_midday_slack(rows: List[Dict], system_label: str, total_stocks: int):
    now = datetime.now().strftime("%H:%M")

    blocks = []
    blocks.append({
        "type": "header",
        "text": {"type": "plain_text",
                 "text": f"🔍 [{system_label}] 11:30 중간 점검", "emoji": True}
    })
    blocks.append({
        "type": "context",
        "elements": [{"type": "mrkdwn",
                      "text": f"🕐 {now}  총 {total_stocks}종목"}]
    })
    blocks.append({"type": "divider"})

    if not rows:
        body = "✅ 5% 이내 인접 종목 없음"
    else:
        lines = [f"*5% 이내 인접 {len(rows)}종목*"]
        for r in rows:
            low_s  = f"{int(r['저가']):,}"
            buy_s  = f"{int(r['매수가']):,}"
            dist_s = f"{r['이격도']:.1f}%"
            label  = f"{r['종목명']}({r['차수']})"
            lines.append(f"• *{label}*  저가 {low_s} → {buy_s}  _({dist_s})_")
        body = "\n".join(lines)

    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": body}})
    blocks.append({"type": "divider"})

    fallback = f"🔍 [{system_label}] 11:30 중간 점검 - {now}"
    send_slack_message(fallback, parse_html=False, blocks=blocks)
    logger.info(f"✓ [{system_label}] 슬랙 중간 점검 전송 완료")


# ── 메인 ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="11:30 중간 점검 리포트")
    parser.add_argument("--appkey",  required=True, help="Kiwoom API App Key")
    parser.add_argument("--secret",  required=True, help="Kiwoom API Secret Key")
    parser.add_argument("--label",   type=str, default="S12",
                        help="시스템 라벨 (S1/S12). 기본: S12")
    parser.add_argument("--signal",  type=str, default=None,
                        help="시그널 파일 경로 (미지정 시 label 기반 자동 결정)")
    parser.add_argument("--force",   action="store_true",
                        help="거래일 체크 무시하고 강제 실행")
    args = parser.parse_args()

    # 시그널 파일 경로 결정
    if args.signal:
        signal_file = args.signal
    elif args.label == "S1":
        signal_file = DEFAULT_S1_SIGNAL
    else:
        signal_file = DEFAULT_S12_SIGNAL

    system_label = args.label

    logger.info("=" * 70)
    logger.info(f"중간 점검 리포트 시작  [{system_label}]")
    logger.info(f"시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"시그널 파일: {signal_file}")
    logger.info("=" * 70)

    # 거래일 체크
    if not args.force and not is_trading_day():
        logger.info("📅 비거래일 — 중간 점검 스킵")
        return

    # 시그널 파일 존재 확인
    if not os.path.exists(signal_file):
        logger.error(f"시그널 파일 없음: {signal_file}")
        sys.exit(1)

    # API 토큰 획득
    try:
        token = os.getenv("KIWOOM_TOKEN") or get_api_token(args.appkey, args.secret)
    except Exception as e:
        logger.error(f"API 토큰 획득 실패: {e}")
        sys.exit(1)

    # 종목 처리
    try:
        df_summary = pd.read_excel(signal_file, sheet_name="Summary")
        total_stocks = len(df_summary)
        logger.info(f"✓ 종목 수: {total_stocks}")
    except Exception as e:
        logger.error(f"시그널 파일 읽기 실패: {e}")
        sys.exit(1)

    rows = build_midday_rows(signal_file, token)
    logger.info(f"\n중간 점검 결과: {len(rows)}종목 (5% 이내)")

    # 전송
    try:
        send_midday_telegram(rows, system_label, total_stocks)
    except Exception as e:
        logger.error(f"텔레그램 전송 실패: {e}")

    try:
        send_midday_slack(rows, system_label, total_stocks)
    except Exception as e:
        logger.error(f"슬랙 전송 실패: {e}")

    logger.info("=" * 70)
    logger.info("중간 점검 완료")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
