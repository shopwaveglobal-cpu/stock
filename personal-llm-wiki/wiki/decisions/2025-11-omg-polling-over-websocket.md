# decision — OMG 크립토 모니터: WebSocket 대신 폴링 유지

- 날짜: 2025-11 이전 (추정 — 원본 파일 수정일 기준) / 상태: **유효하나 재검증 필요** (이후 시스템 구성이 바뀜, 충돌 #5)
- 출처: raw/inbox/2025-11-02-omg-realtime-monitoring-guide.md (실제 기록)

## 배경

크립토 알림을 실시간(WebSocket)으로 바꿀지 검토.

## 결정과 근거

- **폴링 유지 (WebSocket 비권장)**
- 근거: 전략이 일봉 기반이라 초 단위 지연 개선의 실익 없음, 연결 관리·재연결 등 구현 복잡도와 리소스 소모, 알림 스팸 위험
- 개선 방향으로 목표가 거리 기반 동적 주기 채택을 권고 → [concepts/dynamic-polling-interval](../concepts/dynamic-polling-interval.md)

## 재검토 조건

- 초 단위 대응이 필요한 전략(스캘핑·손절 즉시 대응)을 실제로 운용하게 될 때
- 현재 모니터 구성이 문서와 달라졌으므로, OMG 재정비 시 이 결정의 전제(일봉 기반) 유지 여부 확인
