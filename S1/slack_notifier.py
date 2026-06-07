"""
Slack 알람 전송 모듈 (S12 시스템용)
"""
import os
import requests
import logging
from typing import Optional, List
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Slack Webhook URL (환경 변수에서만 읽기)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def convert_html_to_slack_markdown(html_text: str) -> str:
    """
    HTML 태그를 Slack 마크다운으로 변환
    
    Args:
        html_text: HTML 형식의 텍스트
    
    Returns:
        str: Slack 마크다운 형식의 텍스트
    """
    import re
    
    # <b>태그 → *bold*
    text = re.sub(r'<b>(.*?)</b>', r'*\1*', html_text)
    
    # <tg-spoiler>태그 → _spoiler_ (이탤릭체로)
    text = re.sub(r'<tg-spoiler>(.*?)</tg-spoiler>', r'_\1_', text)
    
    # <pre>태그 → ```code block```
    text = re.sub(r'<pre>(.*?)</pre>', r'```\1```', text, flags=re.DOTALL)
    
    # HTML 엔티티 디코딩
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    
    return text


def send_slack_message(message: str, parse_html: bool = True, blocks: list = None) -> bool:
    """
    Slack 메시지 전송 (Incoming Webhook 사용)
    
    Args:
        message: 전송할 메시지 (HTML 태그 포함 가능) - fallback 텍스트로 사용
        parse_html: HTML 태그를 Slack 마크다운으로 변환할지 여부
        blocks: Block Kit blocks 배열 (있으면 blocks 사용, 없으면 text 사용)
    
    Returns:
        bool: 전송 성공 여부
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("Slack Webhook URL이 설정되지 않았습니다. Slack 알림을 건너뜁니다.")
        return False
    
    try:
        if blocks:
            # Block Kit 형식 사용
            payload = {
                "text": message,  # fallback 텍스트
                "blocks": blocks
            }
        else:
            # 일반 텍스트 형식
            if parse_html:
                slack_message = convert_html_to_slack_markdown(message)
            else:
                slack_message = message
            
            payload = {
                "text": slack_message
            }
        
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info("✓ Slack 전송 성공")
        return True
        
    except Exception as e:
        logger.error(f"✗ Slack 전송 실패: {e}")
        return False


def send_slack_realtime_alert_block_kit(
    alert_type: str,
    stock_name: str,
    ticker: str,
    current_price: float,
    target_price: float,
    distance_pct: float,
    sell_prices: dict = None,
    system_label: str = "S2",
    low_price: float = None
) -> bool:
    """
    실시간 알람을 Slack으로 전송 (Block Kit 형식)
    
    Args:
        alert_type: "1차 매수선 5% 인접", "2차 매수선 5% 인접", "1차 매수 체결!" 등
        stock_name: 종목명
        ticker: 티커
        current_price: 현재가
        target_price: 목표가 (매수선 또는 매도선)
        distance_pct: 이격도 (%)
        sell_prices: 매도가 정보 {"sell1": 가격, "sell2": 가격, "sell3": 가격}
        system_label: 시스템 라벨 (기본값: "S2")
        low_price: 저가 (선택적)
    
    Returns:
        bool: 전송 성공 여부
    """
    from datetime import datetime
    
    try:
        now = datetime.now().strftime("%H:%M:%S")
        
        # 알람 타입별 이모지
        emoji_map = {
            "1차 매수선 5% 인접": "🟡",
            "1차 매수선 3% 인접": "🟠",
            "1차 매수선 1% 인접": "🔴",
            "2차 매수선 5% 인접": "🟡",
            "2차 매수선 3% 인접": "🟠",
            "2차 매수선 1% 인접": "🔴",
            "3차 매수선 5% 인접": "🟡",
            "3차 매수선 3% 인접": "🟠",
            "3차 매수선 1% 인접": "🔴",
            "1차 매수 체결": "✅",
            "1차 매수 체결!": "✅",
            "2차 매수 체결": "✅✅",
            "2차 매수 체결!": "✅✅",
            "3차 매수 체결": "✅✅✅",
            "3차 매수 체결!": "✅✅✅",
        }
        
        emoji = emoji_map.get(alert_type, "🔔")
        
        # Block Kit blocks 생성
        blocks = []
        header_text = alert_type  # 기본값 (매수 체결 알람 등)

        # 매수선 인접 알람인 경우 (매수 체결이 아닌 경우)
        if "매수 체결" not in alert_type:
            # 매수선 인접 알람에는 목표가 삽입: "1차 매수선 5% 인접" → "1차 매수선(15,000) 5% 인접"
            if "매수선" in alert_type and target_price:
                header_text = alert_type.replace("매수선 ", f"매수선({int(round(target_price)):,}) ")
            else:
                header_text = alert_type
            # section 블록 1: 헤더 — iOS 알람 미리보기에 이 텍스트가 표시됨
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{emoji} {header_text}*"
                }
            })

            # section 블록 2: 본문 (rich_text 제거 — iOS 알람에 본문이 노출되는 원인)
            low_line = f"\n저가:        {int(low_price):,}원" if low_price else ""
            body_text = (
                f"종목:        *{stock_name}*\n"
                f"현재가:    {int(current_price):,}원"
                f"{low_line}\n"
                f"목표가:    *{int(round(target_price)) if target_price else 0:,}원*\n"
                f"이격도:    {distance_pct:+.2f}%"
            )
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": body_text
                }
            })

            # Divider
            blocks.append({"type": "divider"})

        # 매수 체결 알람인 경우
        else:
            # Section 블록을 첫 번째로: iOS 알람 미리보기가 이 텍스트를 사용
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{emoji} {alert_type} — {stock_name}*"
                }
            })
            
            # section 블록 2: 본문 (rich_text 제거)
            low_line = f"\n저가:        {int(low_price):,}원" if low_price else ""
            body_text = (
                f"종목:        *{stock_name}*\n"
                f"현재가:    {int(current_price):,}원"
                f"{low_line}\n"
                f"목표가:    *{int(round(target_price)) if target_price else 0:,}원*\n"
                f"이격도:    {distance_pct:+.2f}%"
            )

            # 매도가 정보 추가 (매수 체결 시)
            if sell_prices:
                if sell_prices.get('sell1'):
                    body_text += f"\n3% 매도가: {int(round(sell_prices['sell1'])):,}원"
                if sell_prices.get('sell2'):
                    body_text += f"\n5% 매도가: {int(round(sell_prices['sell2'])):,}원"
                if sell_prices.get('sell3'):
                    body_text += f"\n7% 매도가: {int(round(sell_prices['sell3'])):,}원"

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": body_text
                }
            })

            # Divider
            blocks.append({"type": "divider"})
        
        # Fallback 텍스트 (미리보기에 목표가 포함)
        fallback_text = f"{emoji} {header_text} - {stock_name}"
        
        return send_slack_message(fallback_text, parse_html=False, blocks=blocks)
        
    except Exception as e:
        logger.error(f"Slack 알림 포맷팅 실패: {e}")
        return False


def send_slack_realtime_alert(alert_type: str, stock_name: str, ticker: str,
                             current_price: float, target_price: float,
                             distance_pct: float, sell_prices: dict = None,
                             system_label: str = "S1", low_price: float = None) -> bool:
    """
    실시간 알람을 Slack으로 전송 (기존 텍스트 형식 - 호환성 유지)
    
    Args:
        alert_type: "1차 매수선 5% 인접", "2차 매수선 5% 인접", "1차 매수 체결" 등
        stock_name: 종목명
        ticker: 티커
        current_price: 현재가
        target_price: 목표가 (매수선 또는 매도선)
        distance_pct: 이격도 (%)
        sell_prices: 매도가 정보 {"sell1": 가격, "sell2": 가격, "sell3": 가격}
        system_label: 시스템 라벨 (기본값: "S1")
        low_price: 저가 (선택적)
    
    Returns:
        bool: 전송 성공 여부
    """
    from datetime import datetime
    
    try:
        now = datetime.now().strftime("%H:%M:%S")
        
        # 알람 타입별 이모지
        emoji_map = {
            "1차 매수선 5% 인접": "🟡",
            "1차 매수선 3% 인접": "🟠",
            "1차 매수선 1% 인접": "🔴",
            "2차 매수선 5% 인접": "🟡",
            "2차 매수선 3% 인접": "🟠",
            "2차 매수선 1% 인접": "🔴",
            "3차 매수선 5% 인접": "🟡",
            "3차 매수선 3% 인접": "🟠",
            "3차 매수선 1% 인접": "🔴",
            "1차 매수 체결": "✅",
            "1차 매수 체결!": "✅",
            "2차 매수 체결": "✅✅",
            "2차 매수 체결!": "✅✅",
            "3차 매수 체결": "✅✅✅",
            "3차 매수 체결!": "✅✅✅",
        }
        
        emoji = emoji_map.get(alert_type, "🔔")
        
        message = f"{emoji} *[{system_label}] {alert_type}*\n"
        message += f"🕐 {now}\n"
        message += f"────────────\n"
        message += f"종목: {stock_name} ({ticker})\n"
        message += f"현재가: {int(current_price):,}원\n"
        if low_price is not None:
            message += f"저가: {int(low_price):,}원\n"
        message += f"목표가: {int(round(target_price)):,}원\n"
        message += f"이격도: {distance_pct:+.2f}%\n"
        
        # 매수 체결 시 매도가 정보 추가
        if "매수 체결" in alert_type and sell_prices:
            message += f"\n*매도가 정보:*\n"
            if sell_prices.get('sell1'):
                message += f"  • 3% 매도가: {int(round(sell_prices.get('sell1', 0))) if sell_prices.get('sell1') else 0:,}원\n"
            if sell_prices.get('sell2'):
                message += f"  • 5% 매도가: {int(round(sell_prices.get('sell2', 0))) if sell_prices.get('sell2') else 0:,}원\n"
            if sell_prices.get('sell3'):
                message += f"  • 7% 매도가: {int(round(sell_prices.get('sell3', 0))) if sell_prices.get('sell3') else 0:,}원\n"
            message += f"────────────\n"
        
        return send_slack_message(message, parse_html=False)
        
    except Exception as e:
        logger.error(f"Slack 알림 포맷팅 실패: {e}")
        return False


def send_slack_daily_report(results: List[dict], total_stocks: int,
                            system_label: str = "S12") -> bool:
    """
    일일 리포트를 Slack으로 전송 (Block Kit 형식) — 표 형식 4섹션

    Args:
        results:      전체 종목 분석 결과 리스트 (alerts 아님)
        total_stocks: 총 종목 수
        system_label: 시스템 라벨 (S1/S12)

    Returns:
        bool: 전송 성공 여부
    """
    from datetime import datetime

    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # ── 데이터 분류 ────────────────────────────────────────────────
        체결_rows: List[dict] = []
        인접_1:   List[dict] = []
        인접_3:   List[dict] = []
        인접_5:   List[dict] = []

        for r in (results or []):
            status   = r.get("매수상태", "NONE") or "NONE"
            close    = r.get("종가", 0) or 0
            name     = r.get("종목명", "")
            buy1_nxt = r.get("1차매수선(익일)") or 0
            buy2_nxt = r.get("2차매수선(익일)") or 0
            buy3_nxt = r.get("3차매수선(익일)") or 0

            # 체결 섹션: 완료된 차수별 1행
            if status in ("BOUGHT_1", "BOUGHT_2", "BOUGHT_3"):
                체결_rows.append({"name": f"{name}(1차)", "close": close, "buy": buy1_nxt})
            if status in ("BOUGHT_2", "BOUGHT_3"):
                체결_rows.append({"name": f"{name}(2차)", "close": close, "buy": buy2_nxt})
            if status == "BOUGHT_3":
                체결_rows.append({"name": f"{name}(3차)", "close": close, "buy": buy3_nxt})

            # 인접 섹션: 다음 미체결 매수선 기준
            if   status == "NONE":     next_buy = buy1_nxt
            elif status == "BOUGHT_1": next_buy = buy2_nxt
            elif status == "BOUGHT_2": next_buy = buy3_nxt
            else:                      next_buy = 0

            if next_buy and next_buy > 0 and close > 0:
                dist = (close - next_buy) / next_buy * 100
                row = {"name": name, "close": close, "buy": next_buy, "dist": dist}
                if   0 < dist <= 1: 인접_1.append(row)
                elif 1 < dist <= 3: 인접_3.append(row)
                elif 3 < dist <= 5: 인접_5.append(row)

        for lst in (인접_1, 인접_3, 인접_5):
            lst.sort(key=lambda x: x["dist"])

        # ── 헬퍼 ──────────────────────────────────────────────────────
        def fp(p) -> str:
            try:
                return f"{int(p):,}" if p else "-"
            except (TypeError, ValueError):
                return "-"

        def rows_to_mrkdwn(rows: list) -> str:
            if not rows:
                return "없음"
            lines = []
            for row in rows:
                dist_tag = f"  _(+{row['dist']:.1f}%)_" if "dist" in row else ""
                lines.append(f"• *{row['name']}*  {fp(row['close'])} → {fp(row['buy'])}{dist_tag}")
            return "\n".join(lines)

        # ── Block Kit 조립 ────────────────────────────────────────────
        blocks: list = []

        # 헤더
        blocks.append({
            "type": "header",
            "text": {"type": "plain_text",
                     "text": f"📊 [{system_label}] 일일 리포트", "emoji": True}
        })
        blocks.append({
            "type": "context",
            "elements": [{"type": "mrkdwn",
                          "text": f"🕐 {now}  총 {total_stocks}종목"}]
        })
        blocks.append({"type": "divider"})

        # 4개 섹션
        sections = [
            ("🎯 매수 완료",  체결_rows),
            ("🔴 1% 인접",   인접_1),
            ("🟠 3% 인접",   인접_3),
            ("🟡 5% 인접",   인접_5),
        ]
        for title, rows in sections:
            count = len(rows)
            # 섹션 헤더
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn",
                         "text": f"*{title} ({count}건)*"}
            })
            # 종목 목록
            body = rows_to_mrkdwn(rows)
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": body}
            })
            blocks.append({"type": "divider"})

        # ── 전송 (50블록 제한 분할) ──────────────────────────────────
        fallback_text = f"📊 [{system_label}] 일일 리포트 - {now}"
        MAX_BLOCKS = 50

        if len(blocks) <= MAX_BLOCKS:
            return send_slack_message(fallback_text, parse_html=False, blocks=blocks)

        cont_header = [
            {"type": "context",
             "elements": [{"type": "mrkdwn",
                           "text": f"📊 *[{system_label}] 일일 리포트 (계속)*"}]},
            {"type": "divider"}
        ]
        chunks = [blocks[:MAX_BLOCKS]]
        remaining = blocks[MAX_BLOCKS:]
        while remaining:
            avail = MAX_BLOCKS - len(cont_header)
            chunks.append(cont_header + remaining[:avail])
            remaining = remaining[avail:]

        success = True
        for j, chunk in enumerate(chunks):
            ft = fallback_text if j == 0 else f"{fallback_text} (계속 {j+1})"
            if not send_slack_message(ft, parse_html=False, blocks=chunk):
                success = False
        return success

    except Exception as e:
        logger.error(f"Slack 일일 리포트 포맷팅 실패: {e}")
        return False


# 테스트용
if __name__ == "__main__":
    # 간단한 테스트 메시지
    test_msg = "🤖 *Slack 봇 테스트 (S2)*\n테스트 메시지입니다!"
    
    print("Slack 테스트 메시지 전송 중...")
    if send_slack_message(test_msg, parse_html=False):
        print("[SUCCESS] Slack 테스트 메시지 전송 성공!")
    else:
        print("[FAILED] Slack 테스트 메시지 전송 실패")
