# concept — Windows 자동화 함정 (실전 검증됨)

Windows 10 + PowerShell 5.1 + 스케줄 태스크 환경에서 실제로 겪은 함정. 새 자동화를 만들 때 먼저 확인.

## 규칙 (전부 실제 장애에서 도출)

| 규칙 | 이유 | 출처 |
|---|---|---|
| 백그라운드 python은 `python.exe` + `-WindowStyle Hidden`. **pythonw.exe 금지** | pythonw는 콘솔이 없어 sys.stdout=None → `sys.stdout.buffer` 접근 시 즉시 크래시 | raw/inbox/2026-06-13-s1-s12-monitor-supervisor.md |
| 한글 주석 든 `.ps1`은 **UTF-8 BOM** 저장 필수 | PowerShell 5.1이 BOM 없으면 CP949로 읽어 토크나이저 깨짐 | 동일 원본 |
| 한글 든 CSV는 **utf-8-sig(BOM)** 저장 | 엑셀·노션 import에서 한글 깨짐 방지. "깨진 인코딩 금지"가 설계 원칙으로 명문화됨 | raw/inbox/2026-06-17-korea-stocks-notion-template-design.md |
| 프로세스 재시작·작업 트리거는 시스템당 1개 | 다중 진입점 문제가 **2회 발생** — OMG 일일 업데이트 중복(2025-11), S1/S12 루프 누적(2026-06) | [errors/2025-11-07-omg-duplicate-daily-update](../errors/2025-11-07-omg-duplicate-daily-update.md), [errors/2026-06-13-restart-loop-accumulation](../errors/2026-06-13-restart-loop-accumulation.md) |
| 스케줄 태스크 삭제·비활성화는 관리자 권한 필요할 수 있음 | 액세스 거부 시 호출 스크립트를 no-op로 무력화가 차선책 | 동일 원본 |

## 미확인

- WMI Terminate가 불안정했던 정확한 원인 — 원본에 현상만 기록됨

## 연결

- [projects/stock-automation](../projects/stock-automation.md)
- [decisions/2026-06-13-single-supervisor](../decisions/2026-06-13-single-supervisor.md)
