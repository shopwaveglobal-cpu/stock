# 새 컴퓨터 이전 가이드 (S12 / S1 / OMG 시스템)

작성일: 2026-04-23

---

## 현재 시스템 구성 요약

### 프로젝트 디렉터리
| 경로 | 설명 |
|------|------|
| `C:\Users\log\Desktop\Code\S12` | S12 시스템 (거래량 상위 / 메인) |
| `C:\Users\log\Desktop\Code\S1`  | S1 시스템 (시가총액 기반) |
| `C:\Users\log\Desktop\Code\omg` | OMG 일일 분석 시스템 |

### Python 경로
- **현재**: `C:\Python314\python.exe` (Python 3.14)
- 새 컴퓨터도 동일 경로에 설치 권장 (배치파일 수정 최소화)

### API 키 (Kiwoom)
- **App Key**: `IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU`
- **Secret**: `eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs`

> ⚠️ 영웅문 REST API는 **등록된 PC MAC주소**에 묶여 있음.  
> 새 컴퓨터에서는 **키움증권 앱 개발 포털에서 MAC 주소 재등록 필수**.

---

## STEP 1: 영웅문(키움) 설치 및 API 세팅

### 1-1. 영웅문 HTS 설치
1. [키움증권 홈페이지](https://www.kiwoom.com) → 트레이딩 → 영웅문4 다운로드
2. 설치 후 **기존 아이디로 로그인** 확인
3. 공인인증서 / OTP 설정 (기존 인증서 이전 필요 시 공인인증센터 이용)

### 1-2. REST API MAC 주소 재등록
1. [키움 오픈 API 포털](https://apiportal.kiwoom.com) 접속 → 로그인
2. **내 앱 관리** → 기존 앱 선택
3. **허용 MAC 주소** 항목에서 새 PC의 MAC 주소 추가/변경
4. 새 PC의 MAC 주소 확인:
   ```
   ipconfig /all
   ```
   → "물리적 주소" 항목 값 복사

> ℹ️ 기존 MAC 주소를 새 것으로 **교체**해야 함 (동시 등록 가능 여부는 포털에서 확인)

---

## STEP 2: Python 설치

1. [Python 공식 사이트](https://www.python.org/downloads/) → Python 3.14 다운로드
2. 설치 시 **"Add to PATH" 체크 해제**하고 경로를 `C:\Python314`로 지정
   - 커스텀 설치 → 경로 직접 입력: `C:\Python314`
3. 설치 확인:
   ```
   C:\Python314\python.exe --version
   ```

---

## STEP 3: 코드 파일 이전

### 방법 A: Git Clone (권장)
```bash
# 새 PC에서 실행
mkdir C:\Users\log\Desktop\Code
cd C:\Users\log\Desktop\Code
git clone [원격 저장소 URL] S12
git clone [원격 저장소 URL] S1
git clone [원격 저장소 URL] omg
```

### 방법 B: USB / 외장하드 복사
복사해야 할 폴더:
```
C:\Users\log\Desktop\Code\S12\    (전체)
C:\Users\log\Desktop\Code\S1\     (전체)
C:\Users\log\Desktop\Code\omg\    (전체)
```

> ⚠️ 복사 시 `.env` 파일 포함 확인 (gitignore에 들어있어 git에는 없음)

---

## STEP 4: .env 파일 설정

각 프로젝트 루트에 `.env` 파일 생성:

**`C:\Users\log\Desktop\Code\S12\.env`**
```
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

TELEGRAM_TOKEN=your_telegram_token_here

TELEGRAM_CHAT_ID_ME=7899954374
TELEGRAM_CHAT_ID_YOONJOO=1919123245
TELEGRAM_CHAT_ID_MINJEONG=7278408269
TELEGRAM_CHAT_ID_JUMEONI=7856346144
```

**`C:\Users\log\Desktop\Code\S1\.env`** → S12와 동일한 내용으로 복사

---

## STEP 5: Python 패키지 설치

```cmd
C:\Python314\python.exe -m pip install requests python-dotenv pandas openpyxl schedule holidays
```

또는 requirements.txt로:
```cmd
cd C:\Users\log\Desktop\Code\S12
C:\Python314\python.exe -m pip install -r requirements.txt

cd C:\Users\log\Desktop\Code\S1
C:\Python314\python.exe -m pip install -r requirements.txt
```

---

## STEP 6: 작업 스케줄러 등록

현재 등록된 스케줄 목록 (재등록 필요):

| 작업 이름 | 실행 시간 | 실행 파일 | 상태 |
|-----------|-----------|-----------|------|
| **S12_Trading_Signal_Daily** | 매일 20:10 | `S12\run_trading_signal.bat` | ✅ 활성 |
| **S1_Daily_Trading_Signal** | 매일 20:15 | `S1\RUN_S1_DAILY.bat` | ✅ 활성 |
| **S1_Realtime_Monitor** | 평일 08:00 | `S1\run_s1_realtime.bat` | ✅ 활성 |
| **S1_S12_Daily_Restart_7h** | 평일 07:00 | `S12\daily_restart_7h.bat` | ✅ 활성 |
| **S12_Monitor_Watchdog** | 로그인 시 + 평일 08:00/14:00 | `S12\S12_monitor_watchdog.bat` | ✅ 활성 |
| **Monitor_Watchdog_15min** | 매일 07:00 (15분 반복) | `S12\watchdog_monitors.ps1` | ✅ 활성 |
| **OMG_Daily_Analysis** | 매일 00:10 | `omg\run_daily_analysis.bat` | ✅ 활성 |
| **S2_Daily_Trading_Signal** | 매일 20:10 | `S12\RUN_DAILY_SYSTEM.bat` | ✅ 활성 |
| **S2_Realtime_Monitor** | 평일 08:00 | `S12\run_real_time_monitor.bat` | ❌ 비활성 |

### 스케줄러 등록 방법

**방법 A: PowerShell 스크립트 사용 (권장)**
```powershell
# 관리자 권한으로 PowerShell 실행
cd C:\Users\log\Desktop\Code\S12
.\setup_windows_scheduler.ps1
```

**방법 B: 수동 등록**
1. 작업 스케줄러 열기: `Win + R` → `taskschd.msc`
2. "기본 작업 만들기" 클릭
3. 아래 각 작업을 테이블대로 등록

**방법 C: XML 임포트 (기존 PC에서 내보내기)**
```powershell
# 기존 PC에서 XML 내보내기
schtasks /query /xml /tn "S12_Trading_Signal_Daily" > S12_task.xml
schtasks /query /xml /tn "S1_Daily_Trading_Signal" > S1_daily_task.xml
# ... 각 작업별로 반복

# 새 PC에서 XML 임포트
schtasks /create /xml S12_task.xml /tn "S12_Trading_Signal_Daily"
```

---

## STEP 7: 작업 스케줄러 설정 주의사항

### 사용자 계정
- 현재 PC 사용자: `log` (컴퓨터명: `SERVER-LOG`)
- 새 PC에서 사용자명이 바뀌면 배치파일 내 경로 전체 수정 필요
- **사용자명을 `log`로 동일하게 설정 권장**

### 절전모드 설정
스케줄러가 정상 동작하려면:
1. 제어판 → 전원 옵션 → **절전 모드 "사용 안 함"** 설정
2. 작업 스케줄러 각 작업 속성 → "조건" 탭 → "컴퓨터가 AC 전원에 연결된 경우에만 작업 시작" **해제**
3. 작업 속성 → "설정" 탭 → "배터리 전원 시 중지" **해제**

### PowerShell 실행 정책
```powershell
# 관리자 권한으로 실행
Set-ExecutionPolicy RemoteSigned -Scope LocalMachine
```

---

## STEP 8: 동작 확인 테스트

### 기본 연결 테스트
```cmd
cd C:\Users\log\Desktop\Code\S12
C:\Python314\python.exe get_token_once.py IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs
```
→ 토큰값 출력되면 API 연결 성공

### Telegram 알림 테스트
```cmd
C:\Python314\python.exe -c "from telegram_notifier import TelegramNotifier; n=TelegramNotifier(); n.send_message('테스트 메시지')"
```

### 수동 일일 실행 테스트
```cmd
cd C:\Users\log\Desktop\Code\S12
run_trading_signal.bat
```

### 실시간 모니터 테스트
```cmd
cd C:\Users\log\Desktop\Code\S12
C:\Python314\python.exe Real_Time_Monitor.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --interval 60
```

---

## STEP 9: output 파일 이전 (선택)

기존 누적 데이터를 이어가려면:
```
C:\Users\log\Desktop\Code\S12\output\turnover_universe.xlsx   ← 복사 필수 (누적 데이터)
C:\Users\log\Desktop\Code\S12\output\trading_signals.xlsx     ← 복사 권장
C:\Users\log\Desktop\Code\S1\output\marketcap_universe.xlsx   ← 복사 권장
C:\Users\log\Desktop\Code\S12\alert_history.json              ← 복사 권장 (알림 중복 방지)
```

---

## 이전 작업 체크리스트

```
[ ] 1. 영웅문 HTS 설치 및 로그인 확인
[ ] 2. 키움 API 포털에서 새 PC MAC 주소 등록
[ ] 3. Python 3.14 설치 (C:\Python314 경로)
[ ] 4. 코드 파일 이전 (S12, S1, omg)
[ ] 5. .env 파일 생성 (토큰/채팅ID 포함)
[ ] 6. Python 패키지 설치 (pip install)
[ ] 7. PowerShell 실행 정책 설정
[ ] 8. 절전 모드 해제
[ ] 9. 작업 스케줄러 9개 작업 등록
[ ] 10. API 연결 테스트 (get_token_once.py)
[ ] 11. Telegram 알림 테스트
[ ] 12. 수동 일일 실행 테스트
[ ] 13. output 파일 이전 (turnover_universe.xlsx 특히 중요)
```

---

## 자주 발생하는 문제

### "Token acquisition failed" 오류
→ MAC 주소 미등록. 키움 API 포털에서 새 PC MAC 주소 등록 필요

### Python 경로 오류
→ 배치파일 내 `C:\Python314\python.exe` 경로 확인. Python을 다른 경로에 설치했다면 배치파일 전체 경로 수정:
```
# 수정이 필요한 배치파일들:
run_trading_signal.bat
start_realtime_monitor.bat
RUN_DAILY_SYSTEM.bat
S12\daily_restart_7h.bat
S1\RUN_S1_DAILY.bat
```

### 스케줄러 실행은 되는데 창이 안 뜸
→ 정상 동작 (백그라운드 실행). `run_dashboard.bat`으로 상태 확인

### 작업 스케줄러에서 "사용자 비밀번호 필요" 오류
→ 작업 속성 → "로그온한 경우에만 실행" 선택 권장
