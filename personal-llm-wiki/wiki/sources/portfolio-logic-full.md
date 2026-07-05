# source — 전체 프로젝트 로직 (실수치 포함, 내부 전용)

- 원본: raw/inbox/PORTFOLIO_LOGIC_FULL.md (C:\Users\log\Desktop\code\PORTFOLIO_LOGIC_FULL.md에서 복사)
- 날짜: 미상 — 2026-07-05 인입 시점에 존재 확인 (원본에 작성일 없음, 추정 불가)
- 유형: 스펙 총람 (10개 시스템의 실제 조건·상수)
- **⚠ 내부 전용: 원본에 "외부 공유 금지, 노션 공개본은 기호로 마스킹" 명시. 이 wiki 밖으로 내보내지 않는다**
- **git 미추적**: 원격(GitHub)이 공개 저장소라 raw 사본을 .gitignore에 등재 (2026-07-06). 파일은 로컬 디스크에만 존재 — 없으면 원위치(C:\Users\log\Desktop\code\PORTFOLIO_LOGIC_FULL.md)에서 다시 복사

## 요약

운영 중인 10개 시스템의 실제 로직 총람: S1(시총 기반 매수선), S12(거래대금 기반 매수선), OMG(크립토 사이클), Taesan Scanner(Kiwoom), Morning Brief, NASDAQ Brief, KOSPI 20MA 백테스트, 한국주식 노션 템플릿, StockCal iOS 포팅, 1IM Video Tool. 매수선 공식·사이클 상수 등 실수치는 이 요약에 옮기지 않는다 — **수치가 필요하면 반드시 raw 원본을 직접 읽는다**.

## 핵심 구조 (사실, 수치 제외)

- S1: 시총 필터 유니버스, MA20 전일 확정값 기반 1~3차 매수선, 3단계 매도선, 단계별 접근 알람
- S12: 수동 큐레이션 + 거래대금 필터, 계산 로직은 S1과 코드 공유(S12가 소스), 중복 방지 알람, 동적 모니터링 주기
- OMG: 저점/고점 추적 상태기계(none/wait/high), 7단계 매수선 + 손절선, Phase 1.5 매도
- Taesan: 사이클 리셋/매수 대기/분할 매수·매도 상수는 `taesan/config.py`, `taesan/state_machine.py`에 실재
- 한국 주식 호가 단위 표 포함 (공개 정보) → [concepts/krx-tick-size](../concepts/krx-tick-size.md)로 분리

## 충돌

- 가상 샘플의 "KRX 거래대금 급증 알림(250종목, 5분 간격)"은 실제 시스템 목록에 없음 → **index 충돌 현황 #3** (실제 기록 채택, 샘플은 테스트 데이터로 유지)

## 연결

- [projects/stock-automation](../projects/stock-automation.md)
- [concepts/krx-tick-size](../concepts/krx-tick-size.md)
- [sources/2026-06-13-s1-s12-monitor-supervisor](2026-06-13-s1-s12-monitor-supervisor.md) — S1/S12 실행 관리
