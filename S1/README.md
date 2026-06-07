# S1 — 시가총액 기반 실시간 매수선 모니터링 시스템

시가총액 1.3조원 이상 종목을 자동 선정하고, MA20 기반 매수선에 접근하면 실시간 알람을 발송하는 시스템.

---

## 시스템 구조

```
1단계: 종목 선정 (S1 전용)
  Daily_MarketCap_Tracker.py
  → 시가총액 1.3조+ 종목 필터 (코스피/코스닥)
  → output/marketcap_universe.xlsx

         ↓ (매일 20:15 자동 실행)

2단계: 매수선 계산 [S12와 공유 코드]
  Trading_Signal_System.py --label S1
  → MA20, 1/2/3차 매수선, 1/2/3차 매도선 계산
  → output/trading_signals_s1.xlsx (Summary + History 탭)
  → 텔레그램/슬랙 일일 리포트 발송 [S1]

         ↓ (상시 실행, 거래일 08:00-20:00)

3단계: 실시간 감시 [S12와 공유 코드]
  Real_Time_Monitor.py --label S1 --signal-file output/trading_signals_s1.xlsx
  → 60초마다 전 종목 현재가/저가 조회 (키움 API)
  → 저가 기준 매수선 5%/3%/1% 인접 → 알람
  → 저가 <= 매수선 → 체결 알람
  → 텔레그램 + 슬랙 발송 [S1]
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

## 실행 방법

### 수동 실행

```bat
# 1단계: 유니버스 갱신 + 매수선 계산
RUN_S1_DAILY.bat

# 개별 실행
python Daily_MarketCap_Tracker.py --appkey APPKEY --secret SECRET
python Trading_Signal_System.py --appkey APPKEY --secret SECRET --label S1 --universe output/marketcap_universe.xlsx --signal output/trading_signals_s1.xlsx

# 실시간 모니터 (수동 시작)
python Real_Time_Monitor.py --appkey APPKEY --secret SECRET --label S1 --signal-file output/trading_signals_s1.xlsx --interval 60
```

### 자동 실행 (Task Scheduler)

| 태스크 | 시각 | 내용 |
|--------|------|------|
| `S1_Daily_Trading_Signal` | 매일 20:15 | 유니버스 갱신 + 매수선 계산 + 일일 리포트 |
| `S1_Realtime_Monitor` | 로그인 시 | 실시간 모니터 시작 (watchdog 포함) |
| `S1_S12_Daily_Restart_7h` | 매일 07:00 | 토큰 갱신을 위한 모니터 재시작 |

---

## 파일 구조

```
S1/
├── Daily_MarketCap_Tracker.py      # 1단계: 시가총액 유니버스 수집 (S1 전용)
├── Trading_Signal_System.py        # 2단계: 매수선 계산 [S12와 공유, S12가 소스]
├── Real_Time_Monitor.py            # 3단계: 실시간 감시 [S12와 공유, S12가 소스]
├── telegram_notifier.py            # 텔레그램 알람 모듈
├── slack_notifier.py               # 슬랙 알람 모듈 (Block Kit)
├── trading_day_utils.py            # 거래일 체크 유틸리티
│
├── RUN_S1_DAILY.bat                # 2단계 수동/자동 실행
├── S1_self_restart.bat             # 3단계 자동 재시작 루프
├── S1_smart_restart.ps1            # watchdog용 스마트 재시작
├── S1_restart_monitor.ps1          # 07:00 일일 재시작용 kill 스크립트
├── S1_start_monitor.vbs            # 백그라운드 시작 (Session 0 대응)
│
├── output/
│   ├── marketcap_universe.xlsx     # 유니버스 (1단계 출력)
│   └── trading_signals_s1.xlsx     # 매수선 + 알람 상태 (2단계 출력, 3단계 입력)
│
├── alert_history.json              # 당일 알람 발송 기록 (자정 초기화)
├── realtime_monitor.lock           # 중복 실행 방지 락 파일
└── logs/
    └── s1_daily_YYYYMMDD.log       # 2단계 실행 로그
```

> **주의**: `Trading_Signal_System.py`, `Real_Time_Monitor.py`는 S12 디렉토리가 소스입니다.
> 코드 수정 시 S12에서 수정 후 이 폴더로 복사하세요.
> ```powershell
> Copy-Item ..\S12\Real_Time_Monitor.py .\Real_Time_Monitor.py -Force
> Copy-Item ..\S12\Trading_Signal_System.py .\Trading_Signal_System.py -Force
> ```

---

## S12와의 차이

| 항목 | S1 | S12 |
|------|-----|------|
| 종목 선정 | 시가총액 1.3조+ 자동 편입 | 수동 큐레이션 (`add_stocks.py`) |
| 유니버스 | `marketcap_universe.xlsx` | `turnover_universe.xlsx` |
| 신호 파일 | `trading_signals_s1.xlsx` | `trading_signals.xlsx` |
| 알람 라벨 | `[S1]` | `[S12]` |
| 2/3단계 코드 | S12와 동일 | 소스 |
