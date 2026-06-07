"""
텔레그램 알람 전송 모듈
"""
import os
import requests
import logging
from typing import List, Optional
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

# 텔레그램 설정
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage" if TELEGRAM_TOKEN else None

# Chat IDs
CHAT_IDS = {
    "me": os.getenv("TELEGRAM_CHAT_ID_ME"),
    "yoonjoo": os.getenv("TELEGRAM_CHAT_ID_YOONJOO"),
    "minjeong": os.getenv("TELEGRAM_CHAT_ID_MINJEONG"),
    "jumeoni": os.getenv("TELEGRAM_CHAT_ID_JUMEONI")
}


def send_telegram_message(message: str, recipients: List[str] = None, parse_mode: str = "HTML") -> bool:
    """
    텔레그램 메시지 전송
    
    Args:
        message: 전송할 메시지
        recipients: 수신자 리스트 (기본값: ["me"] - 본인만)
                   예: ["me", "yoonjoo"] 또는 ["all"]
        parse_mode: 메시지 포맷 ("Markdown" 또는 "HTML")
    
    Returns:
        bool: 전송 성공 여부
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_API_URL:
        logger.error("텔레그램 토큰이 설정되지 않았습니다.")
        return False
    
    # 기본값: 본인만
    if recipients is None:
        recipients = ["me"]
    
    # "all" 이면 모든 사람에게
    if "all" in recipients:
        recipients = list(CHAT_IDS.keys())
    
    success = True
    for recipient in recipients:
        chat_id = CHAT_IDS.get(recipient)
        if not chat_id:
            logger.warning(f"알 수 없는 수신자: {recipient}")
            continue
        
        try:
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✓ 텔레그램 전송 성공: {recipient}")
        
        except Exception as e:
            logger.error(f"✗ 텔레그램 전송 실패 ({recipient}): {e}")
            success = False
    
    return success


def send_daily_report(results: List[dict], total_stocks: int, recipients: List[str] = None,
                      system_label: str = "S12"):
    """
    일일 리포트 전송 (20:10 실행 시) — 표 형식 4섹션

    Args:
        results:      전체 종목 분석 결과 리스트 (alerts 아님)
        total_stocks: 총 종목 수
        recipients:   수신자 리스트
        system_label: 시스템 라벨 (S1/S12)
    """
    from datetime import datetime

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── 데이터 분류 ──────────────────────────────────────────────────
    체결_rows: List[dict] = []   # 매수 완료 행 (차수별 1행씩)
    인접_1:   List[dict] = []   # 종가 기준 1% 이내
    인접_3:   List[dict] = []   # 1~3%
    인접_5:   List[dict] = []   # 3~5%

    for r in (results or []):
        status   = r.get("매수상태", "NONE") or "NONE"
        close    = r.get("종가", 0) or 0
        name     = r.get("종목명", "")
        buy1_nxt = r.get("1차매수선(익일)") or 0
        buy2_nxt = r.get("2차매수선(익일)") or 0
        buy3_nxt = r.get("3차매수선(익일)") or 0

        # ── 체결 섹션: 완료된 차수별 1행씩 ──
        # '내일의 매수가' = 해당 차수의 익일 매수선 (현재 재계산값)
        if status in ("BOUGHT_1", "BOUGHT_2", "BOUGHT_3"):
            체결_rows.append({"name": f"{name}(1차)", "close": close, "buy": buy1_nxt})
        if status in ("BOUGHT_2", "BOUGHT_3"):
            체결_rows.append({"name": f"{name}(2차)", "close": close, "buy": buy2_nxt})
        if status == "BOUGHT_3":
            체결_rows.append({"name": f"{name}(3차)", "close": close, "buy": buy3_nxt})

        # ── 인접 섹션: 다음 미체결 매수선 기준 ──
        if   status == "NONE":     next_buy = buy1_nxt
        elif status == "BOUGHT_1": next_buy = buy2_nxt
        elif status == "BOUGHT_2": next_buy = buy3_nxt
        else:                      next_buy = 0   # BOUGHT_3 이상 — 더 살 것 없음

        if next_buy and next_buy > 0 and close > 0:
            dist = (close - next_buy) / next_buy * 100
            row = {"name": name, "close": close, "buy": next_buy, "dist": dist}
            if   0 < dist <= 1: 인접_1.append(row)
            elif 1 < dist <= 3: 인접_3.append(row)
            elif 3 < dist <= 5: 인접_5.append(row)

    # 인접 섹션: 이격도 오름차순 (가장 가까운 종목이 위)
    for lst in (인접_1, 인접_3, 인접_5):
        lst.sort(key=lambda x: x["dist"])

    # ── 메시지 조립 ──────────────────────────────────────────────────
    def fp(p) -> str:
        """가격 포맷"""
        try:
            return f"{int(p):,}" if p else "-"
        except (TypeError, ValueError):
            return "-"

    def fmt_section(rows: list, title: str) -> str:
        if not rows:
            return f"{title} (0건)\n없음\n\n"
        lines = f"{title} ({len(rows)}건)\n"
        for row in rows:
            dist_tag = f"  <i>+{row['dist']:.1f}%</i>" if "dist" in row else ""
            lines += f"• {row['name']}  {fp(row['close'])} → {fp(row['buy'])}{dist_tag}\n"
        return lines + "\n"

    msg  = f"📊 <b>[{system_label}] 일일 리포트</b>\n"
    msg += f"🕐 {now}  총 {total_stocks}종목\n"
    msg += "─────────────────────\n\n"
    msg += fmt_section(체결_rows, "🎯 매수 완료")
    msg += fmt_section(인접_1,   "🔴 1% 인접")
    msg += fmt_section(인접_3,   "🟠 3% 인접")
    msg += fmt_section(인접_5,   "🟡 5% 인접")

    send_telegram_message(msg, recipients)


def send_realtime_alert(alert_type: str, stock_name: str, ticker: str, 
                       current_price: float, target_price: float, 
                       distance_pct: float, recipients: List[str] = None,
                       sell_prices: dict = None, system_label: str = "S2",
                       low_price: float = None):
    """
    실시간 알람 전송 (텔레그램 + Slack)
    
    Args:
        alert_type: "1차 매수선 5% 인접", "2차 매수선 5% 인접", "1차 매수 체결" 등
        stock_name: 종목명
        ticker: 티커
        current_price: 현재가
        target_price: 목표가 (매수선 또는 매도선)
        distance_pct: 이격도 (%)
        recipients: 수신자 리스트
        sell_prices: 매도가 정보 {"sell1": 가격, "sell2": 가격, "sell3": 가격}
        system_label: 시스템 라벨 (기본값: "S2")
        low_price: 저가 (선택적)
    """
    from datetime import datetime
    import pandas as pd
    
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
        "1차 매도선 5% 인접": "🟢",
        "2차 매도선 5% 인접": "💚",
        "3차 매도선 5% 인접": "💰"
    }
    
    emoji = emoji_map.get(alert_type, "🔔")
    
    message = f"{emoji} <b>[{system_label}] {alert_type}</b>\n"
    message += f"🕐 {now}\n"
    message += f"───────────\n"
    message += f"종목: {stock_name}\n"
    message += f"현재가: {int(current_price):,}원\n"
    if low_price is not None:
        message += f"저가: {int(low_price):,}원\n"
    message += f"목표가: {int(round(target_price)) if target_price else 0:,}원\n"
    message += f"이격도: {distance_pct:+.2f}%\n"
    
    # 매수 체결 시 매도가 정보 추가
    if "매수 체결" in alert_type and sell_prices:
        message += f"\n3% 매도가: {int(round(sell_prices.get('sell1', 0))) if sell_prices.get('sell1') else 0:,}원\n"
        message += f"5% 매도가: {int(round(sell_prices.get('sell2', 0))) if sell_prices.get('sell2') else 0:,}원\n"
        message += f"7% 매도가: {int(round(sell_prices.get('sell3', 0))) if sell_prices.get('sell3') else 0:,}원\n"
        message += f"───────────\n"
    
    # 텔레그램 메시지 전송
    telegram_success = False
    try:
        telegram_success = send_telegram_message(message, recipients)
        if not telegram_success:
            logger.warning(f"텔레그램 전송 실패: {alert_type} - {stock_name}")
    except Exception as e:
        logger.error(f"텔레그램 전송 중 오류 발생: {e}")
    
    # Slack 메시지 전송은 Real_Time_Monitor.py에서 직접 호출하므로 여기서는 생략
    # (이미 Real_Time_Monitor.py에서 send_slack_realtime_alert_block_kit을 호출하고 있음)
    
    return telegram_success


def send_error_alert(error_message: str, script_name: str = None, recipients: List[str] = None):
    """
    에러 알람 전송 (텔레그램 + Slack)

    Args:
        error_message: 에러 메시지
        script_name: 스크립트 이름
        recipients: 수신자 리스트 (기본값: 본인만)
    """
    from datetime import datetime

    if recipients is None:
        recipients = ["me"]  # 에러는 본인에게만

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 시스템 라벨 추출 (S1/S12/OMG)
    system_label = "UNKNOWN"
    if script_name:
        if "S1" in script_name or "s1" in script_name:
            system_label = "S1"
        elif "S12" in script_name or "s12" in script_name:
            system_label = "S12"
        elif "omg" in script_name or "OMG" in script_name or "crypto" in script_name:
            system_label = "OMG"

    # 텔레그램 메시지
    telegram_message = f"❌ <b>[{system_label}] 시스템 에러 발생</b>\n"
    telegram_message += f"🕐 {now}\n"
    if script_name:
        telegram_message += f"📝 스크립트: {script_name}\n"
    telegram_message += f"───────────────\n"
    telegram_message += f"<pre>{error_message}</pre>"

    # 텔레그램 전송
    send_telegram_message(telegram_message, recipients)

    # Slack 전송
    try:
        from slack_notifier import send_slack_message
        slack_message = f"❌ *[{system_label}] 시스템 에러 발생*\n"
        slack_message += f"🕐 {now}\n"
        if script_name:
            slack_message += f"📝 스크립트: {script_name}\n"
        slack_message += f"───────────────\n"
        slack_message += f"```{error_message}```"
        send_slack_message(slack_message, parse_html=False)
    except Exception as e:
        # Slack 전송 실패해도 텔레그램은 이미 보냈으므로 무시
        pass


# upbit1515 호환성을 위한 TelegramNotifier 클래스
class TelegramNotifier:
    """텔레그램 알림 시스템 (upbit1515 호환)"""
    
    def __init__(self, bot_token: str = None):
        """텔레그램 알림 초기화"""
        self.bot_token = bot_token or TELEGRAM_TOKEN
        if self.bot_token:
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        else:
            self.base_url = None
        self.logger = logging.getLogger(__name__)
    
    def send_message(self, chat_id: str, message: str) -> bool:
        """텔레그램 메시지 전송"""
        if not self.bot_token:
            self.logger.error("텔레그램 토큰이 설정되지 않았습니다.")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            self.logger.info("텔레그램 메시지 전송 성공")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"텔레그램 메시지 전송 실패: {e}")
            return False
        except Exception as e:
            self.logger.error(f"텔레그램 메시지 전송 중 오류: {e}")
            return False
    
    def test_connection(self, chat_id: str) -> bool:
        """텔레그램 연결 테스트"""
        test_message = "🤖 업비트 모니터링 봇 연결 테스트\n\n✅ 정상적으로 연결되었습니다!"
        return self.send_message(chat_id, test_message)


# 테스트용
if __name__ == "__main__":
    # 간단한 테스트 메시지
    test_msg = "🤖 <b>텔레그램 봇 테스트</b>\n테스트 메시지입니다!"
    
    # 본인에게만 테스트
    print("본인에게 테스트 메시지 전송 중...")
    send_telegram_message(test_msg, recipients=["me"])
