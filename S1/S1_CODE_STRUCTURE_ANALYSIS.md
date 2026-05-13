# S1 폴더 코드 구조 분석 결과

## 📁 1. 전체 파일 구조

### 핵심 실행 파일 (Python)
- `Real_Time_Monitor.py` - 실시간 모니터링 (BAT에서 `--signal-file`로 오버라이드)
- `Real_Time_Monitor_S1.py` - 실시간 모니터링 (독립 버전, 기본값 `trading_signals_s1.xlsx`)
- `Trading_Signal_System_S1.py` - 일일 리포트 생성 (매매 시그널 분석)
- `Daily_MarketCap_Tracker.py` - 일일 시가총액 추적

### 실행 스크립트 (BAT)
- **실시간 모니터링:**
  - `run_real_time_monitor_s1.bat` - 백그라운드 실행 (대시보드용)
  - `run_s1_realtime.bat` - 표시 모드 실행 (스케줄러용, `Real_Time_Monitor_S1.py` 사용)
  - `run_s1_realtime_with_display.bat` - 표시 모드 실행 (대체 버전)

- **일일 리포트:**
  - `RUN_S1_DAILY.bat` - 일일 리포트 실행 (20:15 스케줄러용)
  - `UPDATE_EXCEL_NOW_S1.bat` - 수동 실행용 일일 리포트

- **스케줄러 설정:**
  - `setup_scheduler_s1.bat` - 스케줄러 설정 실행
  - `setup_windows_scheduler_s1.ps1` - PowerShell 스케줄러 설정 스크립트

### 유틸리티 파일
- `trading_day_utils.py` - 거래일 체크 유틸리티
- `telegram_notifier.py` - 텔레그램 알림 (S1 폴더 내 독립)
- `slack_notifier.py` - Slack 알림 (S1 폴더 내 독립)
- `contact_price_calculator.py` - 가격 계산 유틸리티
- `create_empty_files.py` - 빈 Excel 파일 생성

### 서브 폴더
- `s1/` - 시가총액 필터 관련 모듈들
  - `market_cap_filter.py`
  - `market_cap_filter_krx.py`
  - `market_cap_filter_krx_simple.py`
  - `market_cap_filter_pykrx.py`
  - `market_cap_filter_real.py`

---

## 🔍 2. 경로 참조 분석

### ✅ 모든 경로가 S1 폴더 내에서 처리됨

#### Import 경로
- `from trading_day_utils import ...` → S1 폴더 내
- `from telegram_notifier import ...` → S1 폴더 내
- `from slack_notifier import ...` → S1 폴더 내
- **S12 폴더 참조 없음** ✅

#### 파일 경로
- `output/trading_signals_s1.xlsx` → S1 폴더 내
- `output/marketcap_universe.xlsx` → S1 폴더 내
- `logs/` → S1 폴더 내 (로그 파일)
- 모든 경로가 상대 경로로 처리됨 ✅

#### 환경 변수
- `.env` 파일 → S1 폴더 내 독립 파일
- S1과 S12의 웹훅 URL이 다름 (의도된 동작) ✅

---

## 📊 3. 실행 파일 분석

### 실시간 모니터링

#### 옵션 1: `run_real_time_monitor_s1.bat` (대시보드용)
```bat
pythonw Real_Time_Monitor.py ^
  --signal-file output/trading_signals_s1.xlsx
```
- **Python 파일**: `Real_Time_Monitor.py`
- **BAT 파일**: `run_real_time_monitor_s1.bat`
- **실행 방식**: 백그라운드 (`pythonw`)
- **Excel 파일**: `output/trading_signals_s1.xlsx` (BAT에서 지정)
- **대시보드 설정**: `monitor_dashboard.py`에서 이 BAT 사용

#### 옵션 2: `run_s1_realtime.bat` (스케줄러용)
```bat
python Real_Time_Monitor_S1.py ^
  --appkey ... --secret ... --interval 60
```
- **Python 파일**: `Real_Time_Monitor_S1.py`
- **BAT 파일**: `run_s1_realtime.bat`
- **실행 방식**: 표시 모드 (`python`)
- **Excel 파일**: `output/trading_signals_s1.xlsx` (기본값)
- **스케줄러 설정**: Windows 작업 스케줄러에서 이 BAT 사용

#### ⚠️ 주의사항
- `Real_Time_Monitor.py`의 기본값은 `output/trading_signals.xlsx` (S12용)
- 하지만 BAT 파일에서 `--signal-file output/trading_signals_s1.xlsx`로 오버라이드함
- 따라서 실제로는 `output/trading_signals_s1.xlsx`를 사용 ✅

### 일일 리포트 (Daily Report)

#### `RUN_S1_DAILY.bat` (20:15 스케줄러용)
```bat
REM Step 1: 시가총액 기준 유니버스 업데이트
python Daily_MarketCap_Tracker.py ...

REM Step 2: trading_signals_s1.xlsx 업데이트
python Trading_Signal_System_S1.py ...
```
- **Python 파일 1**: `Daily_MarketCap_Tracker.py`
- **Python 파일 2**: `Trading_Signal_System_S1.py`
- **BAT 파일**: `RUN_S1_DAILY.bat`
- **실행 시간**: 매일 20:15 (Windows 작업 스케줄러)
- **출력 파일**: 
  - `output/marketcap_universe.xlsx`
  - `output/trading_signals_s1.xlsx`

#### `UPDATE_EXCEL_NOW_S1.bat` (수동 실행용)
- 동일한 로직을 수동 실행할 수 있는 버전

---

## ⚙️ 4. 스케줄러 설정

### Windows 작업 스케줄러 설정 (`setup_windows_scheduler_s1.ps1`)

#### 작업 1: S1_Daily_Trading_Signal
- **실행 파일**: `RUN_S1_DAILY.bat`
- **실행 시간**: 매일 20:15
- **설명**: S1 매일 시가총액 + 시그널 분석

#### 작업 2: S1_Realtime_Monitor
- **실행 파일**: `run_s1_realtime.bat`
- **실행 시간**: 평일 08:00
- **설명**: S1 실시간 주식 모니터링 (표시 모드)

---

## ✅ 5. 최종 확인 사항

### 경로 독립성
- ✅ 모든 import가 S1 폴더 내 파일 참조
- ✅ 모든 파일 경로가 상대 경로 (S1 폴더 기준)
- ✅ S12 폴더 참조 없음
- ✅ `.env` 파일 독립적

### 실행 파일 구조
- ✅ 실시간 모니터링: **PY + BAT 분리됨**
  - PY: `Real_Time_Monitor.py` 또는 `Real_Time_Monitor_S1.py`
  - BAT: `run_real_time_monitor_s1.bat` 또는 `run_s1_realtime.bat`

- ✅ 일일 리포트: **PY + BAT 분리됨**
  - PY: `Daily_MarketCap_Tracker.py` + `Trading_Signal_System_S1.py`
  - BAT: `RUN_S1_DAILY.bat`

### 파일 중복
- ⚠️ `Real_Time_Monitor.py`와 `Real_Time_Monitor_S1.py` 두 파일이 존재
  - `Real_Time_Monitor.py`: 대시보드용 (BAT에서 경로 오버라이드)
  - `Real_Time_Monitor_S1.py`: 스케줄러용 (기본값 사용)
  - 두 파일의 기능은 동일하지만 기본값이 다름

---

## 📝 6. 권장 사항

### 개선 제안
1. **파일 통합**: `Real_Time_Monitor.py`와 `Real_Time_Monitor_S1.py`를 하나로 통합
   - 기본값을 `output/trading_signals_s1.xlsx`로 변경
   - BAT 파일에서 경로 지정 불필요하게 만듦

2. **대시보드 일관성**: 대시보드와 스케줄러가 동일한 BAT 파일 사용하도록 통일
   - 현재: 대시보드 → `run_real_time_monitor_s1.bat` (백그라운드)
   - 현재: 스케줄러 → `run_s1_realtime.bat` (표시 모드)
   - 권장: 하나의 BAT 파일로 통일 (옵션으로 모드 선택)

---

## 🎯 결론

### ✅ S1 폴더는 완전히 독립적으로 작동합니다
- 모든 파일이 S1 폴더 내에 있음
- 모든 import가 S1 폴더 내 파일 참조
- 모든 경로가 S1 폴더 기준 상대 경로
- S12 폴더와의 의존성 없음

### ✅ 실행 파일 구조가 명확합니다
- 실시간 모니터링: PY + BAT 분리 ✅
- 일일 리포트: PY + BAT 분리 ✅
- 스케줄러 설정: 별도 스크립트로 관리 ✅

### ⚠️ 주의사항
- 두 개의 실시간 모니터링 파일이 존재 (기능은 동일, 기본값만 다름)
- 대시보드와 스케줄러가 다른 BAT 파일 사용 (의도된 동작일 수 있음)

---

*분석 일시: 2024년*
*분석 범위: C:\Users\log\Desktop\Code\S1 폴더 전체*











