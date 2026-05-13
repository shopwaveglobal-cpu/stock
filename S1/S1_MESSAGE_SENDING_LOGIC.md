# S1 텔레그램/슬랙 메시지 전송 로직 (S12와 동일)

## 전체 흐름

```
Real_Time_Monitor.py
    ↓
check_simplified_alert() 함수 내부
    ↓
    ├─→ send_realtime_alert() (telegram_notifier.py)
    │       └─→ 텔레그램 메시지 전송
    │
    └─→ send_slack_realtime_alert_block_kit() (slack_notifier.py)
            └─→ 슬랙 Block Kit 메시지 전송
```

## 1. Real_Time_Monitor.py에서 호출

### 위치
- 파일: `C:\Users\log\Desktop\Code\S1\Real_Time_Monitor.py`
- 함수: `check_simplified_alert()` (565줄부터)
- 호출 위치: 여러 알람 조건마다 호출 (628줄, 685줄, 788줄 등)

### system_label 자동 감지

```python
# 시스템 라벨 감지: SIGNAL_FILE에 따라 S1 또는 S2 설정
system_label = None
if "s1" in SIGNAL_FILE.lower() or "s1_signals" in SIGNAL_FILE.lower():
    system_label = "S1"
elif "trading_signals" in SIGNAL_FILE.lower():
    system_label = "S2"
```

S1의 경우 `SIGNAL_FILE = "output/trading_signals_s1.xlsx"`이므로 `system_label = "S1"`로 자동 설정됩니다.

### 호출 예시 (1차 매수 체결)

```python
# 텔레그램 전송
send_realtime_alert(
    alert_type=alert_type,           # "1차 매수 체결!"
    stock_name=stock_name,            # 종목명
    ticker=ticker,                    # 티커
    current_price=current_price,      # 현재가
    target_price=buy1,                # 목표가 (매수선)
    distance_pct=low_dist_buy1,       # 이격도
    recipients=["all"],               # 수신자 (모두)
    sell_prices=sell_prices,          # 매도가 정보
    system_label=system_label,        # "S1" (자동 감지)
    low_price=low_price               # 저가
)

# 슬랙 Block Kit 전송
from slack_notifier import send_slack_realtime_alert_block_kit
send_slack_realtime_alert_block_kit(
    alert_type=alert_type,
    stock_name=stock_name,
    ticker=ticker,
    current_price=current_price,
    target_price=buy1,
    distance_pct=low_dist_buy1,
    sell_prices=sell_prices,
    system_label=system_label,        # "S1"
    low_price=low_price
)
```

### 특징
- **텔레그램과 슬랙을 분리해서 호출** (S12와 동일)
- `telegram_notifier.py`는 텔레그램만 담당
- `slack_notifier.py`는 슬랙만 담당
- 두 모듈은 독립적으로 작동
- **모든 import는 S1 폴더 내에서 해결**

---

## 2. 텔레그램 전송 (telegram_notifier.py)

### 함수: `send_realtime_alert()`
- **위치**: `telegram_notifier.py` 280줄
- **기본값**: `system_label: str = "S1"`

### 메시지 포맷

```
{emoji} [S1] {alert_type}
🕐 {시간}
───────────
종목: {종목명}
현재가: {현재가:,}원
저가: {저가:,}원        (선택적, 있을 때만)
목표가: {목표가:,}원
이격도: {이격도:+.2f}%

(매수 체결 시 추가)
3% 매도가: {가격:,}원
5% 매도가: {가격:,}원
7% 매도가: {가격:,}원
───────────
```

### 이모지 매핑 (S12와 동일)

```python
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
```

### 수신자 처리

```python
# recipients 파라미터
- None 또는 지정 안함 → ["me"] (본인만)
- ["all"] → 모든 수신자 (me, yoonjoo, minjeong, jumeoni)
- ["me", "yoonjoo"] → 지정된 수신자만
```

### API 호출

```python
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

payload = {
    "chat_id": chat_id,
    "text": message,
    "parse_mode": "HTML"  # HTML 포맷 사용
}

response = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
```

### 중요 사항

- **Slack 전송은 하지 않음** (355-356줄 주석)
- 텔레그램 전송만 담당
- `send_telegram_message()` 함수를 내부에서 호출
- **S1 폴더 내에서 모든 경로 해결**

---

## 3. 슬랙 전송 (slack_notifier.py)

### 함수: `send_slack_realtime_alert_block_kit()`
- **위치**: `slack_notifier.py` 100줄
- **기본값**: `system_label: str = "S1"`

### Block Kit 형식

슬랙 Block Kit API를 사용하여 구조화된 메시지 전송 (S12와 동일)

### 메시지 구조

#### 매수선 인접 알람 (매수 체결이 아닌 경우)

```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "{emoji} {alert_type}",
        "emoji": true
      }
    },
    {
      "type": "rich_text",
      "elements": [
        {
          "type": "rich_text_preformatted",
          "elements": [
            {
              "type": "text",
              "text": "종목: {종목명}\n현재가: {현재가:,}원\n목표가: {목표가:,}원\n이격도: {이격도:+.2f}%"
            }
          ]
        }
      ]
    },
    {
      "type": "divider"
    }
  ]
}
```

#### 매수 체결 알람

```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "{emoji} {alert_type}",
        "emoji": true
      }
    },
    {
      "type": "rich_text",
      "elements": [
        {
          "type": "rich_text_preformatted",
          "elements": [
            {
              "type": "text",
              "text": "종목: {종목명}\n현재가: {현재가:,}원\n목표가: {목표가:,}원\n이격도: {이격도:+.2f}%\n\n3% 매도가: {가격:,}원\n5% 매도가: {가격:,}원\n7% 매도가: {가격:,}원"
            }
          ]
        }
      ]
    },
    {
      "type": "divider"
    }
  ]
}
```

### API 호출

```python
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # S1 폴더의 .env에서 로드

payload = {
    "blocks": blocks,
    "text": fallback_text  # Fallback 텍스트
}

response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
```

### 특징

- **Block Kit 형식 사용**: 구조화된 메시지
- **이모지 지원**: Header에 이모지 포함
- **Preformatted 텍스트**: 종목 정보를 preformatted 형식으로 표시
- **시스템 라벨 제외**: Header에는 시스템 라벨 없이 알람 타입만 표시
- **S1 폴더 내에서 모든 경로 해결**

---

## 4. 환경 변수 설정

### 텔레그램 (.env)

```env
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID_ME=your_chat_id
TELEGRAM_CHAT_ID_YOONJOO=your_chat_id
TELEGRAM_CHAT_ID_MINJEONG=your_chat_id
TELEGRAM_CHAT_ID_JUMEONI=your_chat_id
```

### 슬랙 (.env)

```env
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
```

**주의**: S1과 S12의 `.env` 파일은 다릅니다. 각각 독립적인 웹훅 URL을 사용합니다.

---

## 5. 호출 시나리오

### 시나리오 1: 1차 매수 체결

```python
# Real_Time_Monitor.py에서
send_realtime_alert(
    alert_type="1차 매수 체결!",
    stock_name="삼성전자",
    ticker="005930",
    current_price=70000,
    target_price=69000,
    distance_pct=-1.43,
    recipients=["all"],
    sell_prices={"sell1": 72100, "sell2": 72450, "sell3": 72800},
    system_label="S1",  # 자동 감지
    low_price=68900
)

# 슬랙도 동시에 호출
send_slack_realtime_alert_block_kit(...)
```

**결과:**
- 텔레그램: ✅ [S1] 1차 매수 체결! 메시지 전송 (모든 수신자)
- 슬랙: ✅ 1차 매수 체결! Block Kit 메시지 전송

### 시나리오 2: 1차 매수선 1% 인접

```python
send_realtime_alert(
    alert_type="1차 매수선 1% 인접",
    stock_name="삼성전자",
    ticker="005930",
    current_price=69700,
    target_price=69000,
    distance_pct=1.01,
    recipients=["all"],
    sell_prices=None,
    system_label="S1",
    low_price=69600
)
```

**결과:**
- 텔레그램: 🔴 [S1] 1차 매수선 1% 인접 메시지 전송
- 슬랙: 🔴 1차 매수선 1% 인접 Block Kit 메시지 전송

---

## 6. 주요 차이점 요약 (S12와 비교)

| 항목 | 텔레그램 | 슬랙 |
|------|---------|------|
| **형식** | HTML 텍스트 | Block Kit (JSON) |
| **이모지** | 텍스트에 포함 | Header에 포함 |
| **시스템 라벨** | 메시지에 포함 `[S1]` | Header에 없음 |
| **저가 정보** | 표시 (있을 때) | 표시 안 함 |
| **매도가 정보** | 매수 체결 시 표시 | 매수 체결 시 표시 |
| **수신자** | 여러 명 지원 | Webhook URL로 전송 |
| **API** | Telegram Bot API | Slack Incoming Webhook |

---

## 7. S12와의 차이점

### 동일한 점
1. 호출 방식 동일
2. 메시지 포맷 동일
3. 이모지 매핑 동일
4. Block Kit 구조 동일

### 다른 점
1. **system_label 기본값**: S1은 "S1", S12는 "S2"
2. **환경 변수**: 각각 독립적인 `.env` 파일 사용
3. **파일 경로**: S1 폴더 내에서 모든 경로 해결

---

## 8. 에러 처리

### 텔레그램

```python
try:
    telegram_success = send_telegram_message(message, recipients)
    if not telegram_success:
        logger.warning(f"텔레그램 전송 실패: {alert_type} - {stock_name}")
except Exception as e:
    logger.error(f"텔레그램 전송 중 오류 발생: {e}")
```

### 슬랙

```python
try:
    response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()
    return True
except Exception as e:
    logger.error(f"Slack 알림 전송 실패: {e}")
    return False
```

---

## 9. 핵심 포인트

1. **독립적인 호출**: 텔레그램과 슬랙은 각각 독립적으로 호출
2. **분리된 책임**: `telegram_notifier.py`는 텔레그램만, `slack_notifier.py`는 슬랙만
3. **동일한 파라미터**: 두 함수 모두 동일한 파라미터를 받음
4. **에러 독립성**: 하나가 실패해도 다른 하나는 계속 작동
5. **함수 내부 import**: `Real_Time_Monitor.py`에서 함수 내부에서 import (`from slack_notifier import ...`)
6. **S1 폴더 독립성**: 모든 경로가 S1 폴더 내에서 해결됨

---

## 10. 수정 사항 요약

### 변경 전
- `telegram_notifier.py`에서 Slack 처리 시도 (복잡한 import)
- emoji_map이 간단함 (5% 인접만)
- low_price 표시 없음

### 변경 후
- `telegram_notifier.py`에서 Slack 처리 제거 (S12와 동일)
- emoji_map을 상세하게 수정 (1%, 3%, 5% 인접)
- low_price 표시 추가
- S12와 완전히 동일한 로직 적용

---

*작성일: 2024년*
*파일 위치: S1 폴더*
*참고: S12와 동일한 로직이지만 system_label만 "S1"로 설정*











