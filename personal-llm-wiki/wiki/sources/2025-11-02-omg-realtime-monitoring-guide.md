# source — OMG 실시간 모니터링 가이드 (폴링 vs WebSocket)

- 원본: raw/inbox/2025-11-02-omg-realtime-monitoring-guide.md (omg/REALTIME_MONITORING_GUIDE.md에서 복사)
- 날짜: 추정 — 본문에 "2025-01-XX", 파일 수정일 2025-11-02. **작성 후 최소 8개월 경과한 오래된 문서**
- 유형: 분석 + 권고 (폴링 주기 설계)

## 요약

크립토 모니터링에서 폴링(10분/1시간) vs WebSocket 실시간을 비교하고, 일봉 기반 전략에는 폴링 유지가 적합하다고 결론. 개선안으로 목표가 거리 기반 동적 주기(1%→1분 … 그 외→30분)를 제안.

## 핵심 사실 (원본 기재 — 작성 시점 기준)

- 당시 구성: Envelope 알림 10분 폴링(45일 MA ±45%, 하단선 5% 이내 알림), 업비트 급락 감시 1시간(-15% 하락 15개 이상, 일 1회 제한)
- WebSocket 비권장 근거: 일봉 기반 전략에 실시간 불필요, 구현 복잡도·리소스·알림 스팸
- 동적 주기 제안: 거리 1% 이내 1분 / 3% 이내 3분 / 10% 이내 10분 / 그 외 30분

## 2026-07-05 검증 — 이 문서는 현재 구성과 다름 (충돌 #5)

- omg/CLAUDE.md는 Envelope·업비트 감시가 별도 저장소(CoinRedS, Upbit1515)로 분리됐고 OMG 자체 모니터는 `crypto_realtime_monitor.py`라고 기재 — 문서 간 충돌
- 단, CoinRedS·Upbit1515는 이 PC의 `Desktop/code` 경로에 없음 (2026-07-05 Test-Path 확인) — **현재 위치·가동 여부 미확인**
- 원본 속 경로 `c:\Coding\omg\Red S\`는 옛 구조로 보임 (현재는 `Desktop\code\omg`) — 해석

## 미확인

- crypto_realtime_monitor.py의 실제 실행 주기 (omg/CLAUDE.md는 30분이라 하나 코드 확인 안 됨 — 코드에는 1분 스케줄 루프 존재)
- Envelope·업비트 감시의 현재 가동 여부

## 연결

- [decisions/2025-11-omg-polling-over-websocket](../decisions/2025-11-omg-polling-over-websocket.md)
- [concepts/dynamic-polling-interval](../concepts/dynamic-polling-interval.md)
- [projects/stock-automation](../projects/stock-automation.md)
