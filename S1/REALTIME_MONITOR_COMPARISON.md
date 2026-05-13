# S1 vs S12 실시간 감시 알람 비교 분석

## 발견된 차이점

### 1. telegram_notifier.py의 Slack 처리 방식

#### S12 (정상 작동)
- **위치**: `C:\Users\log\Desktop\Code\S12\telegram_notifier.py` (328-329줄)
- **처리**: Slack 전송을 `telegram_notifier.py`에서 하지 않음
- **코드**: 
  ```python
  # Slack 메시지 전송은 Real_Time_Monitor.py에서 직접 호출하므로 여기서는 생략
  # (이미 Real_Time_Monitor.py에서 send_slack_realtime_alert_block_kit을 호출하고 있음)
  ```
- **결과**: `Real_Time_Monitor.py`에서 직접 호출하여 작동

#### S1 (문제 있음)
- **위치**: `C:\Users\log\Desktop\Code\S1\telegram_notifier.py` (342-368줄)
- **처리**: Slack 전송을 `telegram_notifier.py` 내부에서 처리하려고 시도
- **코드**: 복잡한 import 방식 사용
  ```python
  import importlib.util
  spec = importlib.util.spec_from_file_location("slack_notifier_s1", S1_SLACK_NOTIFIER_PATH)
  ```
- **문제**: 불필요한 복잡성, 실패 가능성 높음

### 2. Real_Time_Monitor.py의 Slack import

#### S12 (정상 작동)
- **코드**: 
  ```python
  from slack_notifier import send_slack_realtime_alert_block_kit
  ```
- **위치**: 함수 내부에서 import (642줄)
- **결과**: 정상 작동

#### S1 (확인 필요)
- **코드**: 
  ```python
  from slack_notifier import send_slack_realtime_alert_block_kit
  ```
- **위치**: 함수 내부에서 import (642줄)
- **문제**: 동일한 코드인데 작동하지 않음

### 3. system_label 설정

#### S1
- **기본값**: `system_label: str = "S1"` (telegram_notifier.py 283줄)
- **로직**: `Real_Time_Monitor.py`에서 SIGNAL_FILE에 따라 자동 감지 (600-605줄)
  ```python
  if "s1" in SIGNAL_FILE.lower() or "s1_signals" in SIGNAL_FILE.lower():
      system_label = "S1"
  elif "trading_signals" in SIGNAL_FILE.lower():
      system_label = "S2"
  ```

#### S12
- **기본값**: `system_label: str = "S2"` (telegram_notifier.py 256줄)
- **로직**: `Real_Time_Monitor.py`에서 SIGNAL_FILE에 따라 자동 감지 (600-605줄)

### 4. emoji_map 차이

#### S12
- 더 상세한 이모지 매핑 (1%, 3%, 5% 인접)
  ```python
  "1차 매수선 5% 인접": "🟡",
  "1차 매수선 3% 인접": "🟠",
  "1차 매수선 1% 인접": "🔴",
  ```

#### S1
- 간단한 이모지 매핑 (5% 인접만)
  ```python
  "1차 매수선 5% 인접": "🟡",
  "2차 매수선 5% 인접": "🟠",
  "3차 매수선 5% 인접": "🔴",
  ```

### 5. low_price 표시

#### S12
- 저가 정보 표시 (307-308줄)
  ```python
  if low_price is not None:
      message += f"저가: {int(low_price):,}원\n"
  ```

#### S1
- 저가 정보 표시 없음

## 문제 진단

### 가능한 원인

1. **Slack import 실패**
   - S1의 `Real_Time_Monitor.py`에서 `from slack_notifier import send_slack_realtime_alert_block_kit`가 실패할 수 있음
   - S1 폴더에서 실행될 때 경로 문제 가능성

2. **telegram_notifier.py의 복잡한 Slack 처리**
   - S1의 `telegram_notifier.py`에서 Slack을 처리하려고 하는데, 이 부분이 실패할 수 있음
   - S12처럼 `Real_Time_Monitor.py`에서 직접 호출하는 방식이 더 안정적

3. **함수 존재 여부**
   - `send_slack_realtime_alert_block_kit` 함수가 S1의 `slack_notifier.py`에 존재하는지 확인 필요

## 해결 방안

1. **S12 방식으로 통일**
   - S1의 `telegram_notifier.py`에서 Slack 처리 부분 제거
   - `Real_Time_Monitor.py`에서 직접 호출하도록 유지 (이미 그렇게 되어 있음)

2. **slack_notifier.py 함수 확인**
   - `send_slack_realtime_alert_block_kit` 함수 존재 확인
   - S12와 동일한지 비교

3. **import 경로 확인**
   - S1 폴더에서 실행 시 `slack_notifier` 모듈을 찾을 수 있는지 확인

4. **에러 로그 확인**
   - S1의 실시간 모니터링 로그에서 import 에러 확인











