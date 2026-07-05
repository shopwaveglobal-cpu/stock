# concept — 거리 기반 동적 폴링 주기

목표가에 가까울수록 자주, 멀수록 드물게 체크하는 패턴. 두 시스템에서 독립적으로 채택된 검증된 설계.

## 패턴 (사실)

- OMG 가이드 제안: 거리 1% 이내 1분 / 3% 이내 3분 / 10% 이내 10분 / 그 외 30분 (출처: raw/inbox/2025-11-02-omg-realtime-monitoring-guide.md — 제안 단계)
- S12 실운영: 1% 미만 근접 시 1분, 10% 초과 시 30분 (출처: raw/inbox/PORTFOLIO_LOGIC_FULL.md — 운영 중)

## 왜 유효한가 (원본 근거)

- API 호출·리소스 절약 + 근접 구간에서만 정밀 감시 → 지연과 스팸을 동시에 줄임
- WebSocket 실시간 대비 구현 단순 (기존 폴링 코드 수정만)

## 적용 기준 (해석)

- 일봉·추세 기반 전략의 알림에 적합. 초 단위 대응이 필요한 전략에는 부적합 — [decisions/2025-11-omg-polling-over-websocket](../decisions/2025-11-omg-polling-over-websocket.md) 근거 참조

## 연결

- [sources/2025-11-02-omg-realtime-monitoring-guide](../sources/2025-11-02-omg-realtime-monitoring-guide.md)
- [sources/portfolio-logic-full](../sources/portfolio-logic-full.md)
