---
name: s1-s12-monitor-supervisor
description: "S1/S12 실시간 모니터는 monitor_supervisor.ps1 + *_Supervisor 태스크가 관리(루프 누적 버그 해결, 2026-06-13)"
metadata: 
  node_type: memory
  type: project
  originSessionId: a4b247c1-6e36-4805-8a75-9c494a34b52b
---

S1/S12 실시간 주식 모니터(`Real_Time_Monitor.py`)는 이제 **`S12/monitor_supervisor.ps1`** 단일 슈퍼바이저가 관리한다. 스케줄 태스크 `S1_Supervisor`/`S12_Supervisor`가 1분마다 실행하여 "모니터 python 정확히 1개" 불변식을 강제(0이면 시작, 2+면 락 보유자만 남김, OS 뮤텍스로 레이스 차단, 07시 1회 토큰 위생 재시작). 무동작이면 `supervisor.log`에 기록 안 함.

**해결한 근본 원인:** 과거 진입점 4개(daily_restart_7h / *_smart_restart / watchdog_monitors 15분 / run_real_time_monitor)가 각자 `S{n}_self_restart.bat` 5초 루프를 "체크→비동기 VBS start" 레이스로 띄워, 재부팅/중복 트리거마다 루프가 누적 → 영구히 5초마다 python을 뱉으며 락 충돌 ERROR 스팸. WMI Terminate가 불안정해 기존 python(예: 6/8 PID 22816)을 며칠째 못 죽였음.

**비활성화한 레거시(전부 no-op 처리됨):** `S1/S12_self_restart.bat`, `daily_restart_7h.bat`, `S1/S12_smart_restart.ps1`. `watchdog_monitors.ps1`은 S1/S12 블록 제거하고 OMG 크립토 감시만 남김.

**운영 주의사항(겪은 함정):**
- 모니터는 반드시 **`python.exe`** 로 띄울 것. `pythonw.exe`는 콘솔이 없어 `sys.stdout=None`인데 스크립트가 시작 시 `sys.stdout.buffer`를 접근해 **즉시 크래시**함. 창 숨김은 `-WindowStyle Hidden`.
- 한글 주석이 든 `.ps1`은 **UTF-8 BOM**으로 저장해야 함. Windows PowerShell 5.1은 BOM 없으면 CP949로 읽어 토크나이저가 깨짐.
- 옛 태스크 4개(`S12_Monitor_Watchdog`, `S1_Realtime_Monitor`, `S1_S12_Daily_Restart_7h`, `S2_Realtime_Monitor`)는 관리자 권한 없이는 삭제/비활성화 불가(액세스 거부). 호출 스크립트를 no-op로 만들어 무력화함. 완전 삭제하려면 **관리자 PowerShell**에서 `Unregister-ScheduledTask`. 이름이 "S2"여도 실제론 S12 런처임(이 코드베이스에 S2 시스템 없음).
- 검증 완료(2026-06-13 토): python 죽이면 ~1분 내 스케줄 태스크가 자동 재기동. 알람은 평일 08:00-20:00에만, 주말/공휴일은 "비거래일 대기"가 정상.

관련: [[[s12-trading-system]]]
