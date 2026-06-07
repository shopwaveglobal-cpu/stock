# S12 — 수동 큐레이션 기반 실시간 매수선 모니터링 시스템

직접 선정한 종목에 대해 MA20 기반 매수선에 접근하면 실시간 알람을 발송하는 시스템.
S1과 코드를 공유하며, 이 디렉토리(S12)가 공유 코드의 소스입니다.

---

## 시스템 구조

```
1단계: 종목 선정 (S12 전용)
  add_stocks.py                         ← 수동 종목 추가
  Daily_Turnover_Tracker.py             ← 거래대금 기반 유니버스 갱신
  → output/turnover_universe.xlsx

         ↓ (매일 20:10 자동 실행)

2단계: 매수선 계산 [S1과 공유 코드 — 이 파일이 소스]
  Trading_Signal_System.py --label S12
  → MA20, 1/2/3차 매수선, 1/2/3차 매도선 계산
  → output/trading_signals.xlsx (Summary + History 탭)
  → 텔레그램/슬랙 일일 리포트 발송 [S12]

         ↓ (상시 실행, 거래일 08:00-20:00)

3단계: 실시간 감시 [S1과 공유 코드 — 이 파일이 소스]
  Real_Time_Monitor.py --label S12 --signal-file output/trading_signals.xlsx
  → 60초마다 전 종목 현재가/저가 조회 (키움 API)
  → 저가 기준 매수선 5%/3%/1% 인접 → 알람
  → 저가 <= 매수선 → 체결 알람
  → 텔레그램 + 슬랙 발송 [S12]
```

---

## 매수선 계산 방식

- **기준**: MA20 (20일 이동평균선의 전일 기준값 S19 사용)
- **1차 매수선**: `ceil_tick(S19 / 24)` — 호가 단위 올림
- **2차 매수선**: `ceil_tick(1차 × 0.90)`
- **3차 매수선**: `ceil_tick(2차 × 0.90)`
- **매도선**: 1차 매수가 기준 +3% / +5% / +7%

---

## 알람 조건

| 조건 | 트리거 | 이모지 |
|------|--------|--------|
| 매수선 5% 이내 접근 | 당일 저가 기준 | 🟡 |
| 매수선 3% 이내 접근 | 당일 저가 기준 | 🟠 |
| 매수선 1% 이내 접근 | 당일 저가 기준 | 🔴 |
| 매수선 터치 (체결) | 저가 <= 매수선 | 🎯 |

- 하루 1회 중복 방지 (`alert_history.json`, 자정 초기화)
- 매수 상태에 따라 감시 대상 매수선 자동 전환 (NONE→1차, BOUGHT_1→2차, BOUGHT_2→3차)

---

## 종목 추가 방법

```python
# add_stocks.py 상단 NEW_STOCKS 리스트에 입력
NEW_STOCKS = [
    ('삼성전자', '005930'),
    ('SK하이닉스', '000660'),
]

# 실행
python add_stocks.py           # 신규 종목만 추가 (기존 매수선 불변)
python add_stocks.py --dry-run # 미리보기만 (저장 안 함)
python add_stocks.py --update  # 기존 종목 매수선도 갱신 (주의: "yes" 확인 필요)
```

> **주의**: `--update` 없이 실행하면 기존 종목 매수선은 절대 변경되지 않습니다.
> 장중 실행 시 `data[1:21]` 사용으로 당일 미확정 가격 자동 제외.

---

## 실행 방법

### 수동 실행

```bat
# 2단계: 매수선 계산 + 일일 리포트
RUN_DAILY_SYSTEM.bat

# 개별 실행
python Daily_Turnover_Tracker.py --appkey APPKEY --secret SECRET
python Trading_Signal_System.py --appkey APPKEY --secret SECRET --label S12

# 실시간 모니터 (수동 시작)
python Real_Time_Monitor.py --appkey APPKEY --secret SECRET --label S12 --signal-file output/trading_signals.xlsx --interval 60
```

### 자동 실행 (Task Scheduler)

| 태스크 | 시각 | 내용 |
|--------|------|------|
| `S12_Trading_Signal_Daily` | 매일 20:10 | 유니버스 갱신 + 매수선 계산 + 일일 리포트 |
| `S12_Monitor_Watchdog` | 15분마다 | 모니터 비정상 종료 시 자동 재시작 |
| `S1_S12_Daily_Restart_7h` | 매일 07:00 | 토큰 갱신을 위한 모니터 재시작 |

---

## 파일 구조

```
S12/
├── Trading_Signal_System.py        # 2단계: 매수선 계산 [S1과 공유 — 소스]
├── Real_Time_Monitor.py            # 3단계: 실시간 감시 [S1과 공유 — 소스]
├── Daily_Turnover_Tracker.py       # 1단계: 거래대금 유니버스 갱신 (S12 전용)
├── add_stocks.py                   # 종목 수동 추가 도구
├── telegram_notifier.py            # 텔레그램 알람 모듈
├── slack_notifier.py               # 슬랙 알람 모듈 (Block Kit)
├── trading_day_utils.py            # 거래일 체크 유틸리티
│
├── RUN_DAILY_SYSTEM.bat            # 2단계 수동/자동 실행
├── run_trading_signal.bat          # Trading_Signal_System 직접 실행
├── S12_self_restart.bat            # 3단계 자동 재시작 루프
├── S12_smart_restart.ps1           # watchdog용 스마트 재시작
├── S12_monitor_watchdog.bat        # 15분 watchdog 진입점
├── S12_restart_monitor.ps1         # 07:00 일일 재시작용 kill 스크립트
├── S12_start_monitor.vbs           # 백그라운드 시작 (Session 0 대응)
│
├── output/
│   ├── turnover_universe.xlsx      # 유니버스 (1단계 출력)
│   └── trading_signals.xlsx        # 매수선 + 알람 상태 (2단계 출력, 3단계 입력)
│
├── alert_history.json              # 당일 알람 발송 기록 (자정 초기화)
├── realtime_monitor.lock           # 중복 실행 방지 락 파일
└── logs/
    └── s12_daily_YYYYMMDD.log      # 2단계 실행 로그
```

> **공유 코드 관리**: `Trading_Signal_System.py`, `Real_Time_Monitor.py` 수정 후 S1에 동기화:
> ```powershell
> Copy-Item .\Real_Time_Monitor.py ..\S1\Real_Time_Monitor.py -Force
> Copy-Item .\Trading_Signal_System.py ..\S1\Trading_Signal_System.py -Force
> ```

---

## 토큰 관리

키움 API 토큰은 약 30시간 유효 (다음날 20:10 만료).
다음 3가지 조건 중 하나라도 해당되면 자동 갱신:

1. 토큰 없음 (최초 실행)
2. 날짜 변경 (자정 넘김)
3. 만료 1시간 이내

---

## S1과의 차이

| 항목 | S12 | S1 |
|------|------|-----|
| 종목 선정 | 수동 큐레이션 (`add_stocks.py`) | 시가총액 1.3조+ 자동 편입 |
| 유니버스 | `turnover_universe.xlsx` | `marketcap_universe.xlsx` |
| 신호 파일 | `trading_signals.xlsx` | `trading_signals_s1.xlsx` |
| 알람 라벨 | `[S12]` | `[S1]` |
| 2/3단계 코드 | **소스** | S12에서 복사 |
