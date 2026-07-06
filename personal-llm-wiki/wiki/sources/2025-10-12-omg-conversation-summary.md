# source — OMG 개발 대화 요약 (2025-10-12)

- 원본: raw/inbox/2025-10-12-omg-conversation-summary.md (omg/CONVERSATION_SUMMARY.md에서 복사)
- 날짜: 2025-10-12 (원본 명시) / 유형: 개발 이력 요약
- 주의: 작성 시점 구조 기록 — **이후 2025-11-07 분리 작업으로 일부 구조가 바뀜** ([sources/2025-11-07-omg-separation-summary](2025-11-07-omg-separation-summary.md) 참조)

## 요약

OMG 암호화폐 분석·알림 시스템의 개발 시점 파일 구성과 역할 기록. envelope_alert(단일 실행) / envelope_monitor_loop(연속 10분) / coin_analysis_excel(Top50 분석 엑셀) / auto_debug_builder(Top100 시뮬레이션) / universe_selector(유니버스 관리) 등.

## 핵심 사실 (원본 기재, 2025-10-12 시점)

- Envelope: 45일 이동평균 기준, 이격도 5% 이내 감지, 기본 10분 간격 연속 모니터링
- 매수선: H값 기준 7단계 하락률 (수치는 raw 참조 — 내부 전용 취급)
- 분석 대상: 시총 Top 50(엑셀) / Top 100(debug 시뮬레이션), 래핑·브릿지 토큰 제외
- 실행: Windows 작업 스케줄러용 배치 파일 등록 방식

## 시간순 위치 (해석)

이 문서(2025-10-12) → 모니터링 가이드(~2025-11-02) → 분리 작업(2025-11-07) → 현재 crypto_realtime_monitor 5분 주기 가동. OMG 관련 질문은 **가장 최신인 분리 보고서를 우선** 참조할 것.

## 연결

- [sources/2025-11-07-omg-separation-summary](2025-11-07-omg-separation-summary.md) — 최신 구조
- [concepts/cycle-state-machine](../concepts/cycle-state-machine.md)
- [projects/stock-automation](../projects/stock-automation.md)
