# project — Local-first Apps / 개인 도구

로컬에서 동작하는 개인 도구 (데스크톱·모바일·브라우저).

## 현재 상태 (사실)

- **StockCal (주식 계산기)**: C# WinForms 데스크톱 앱 v2.9 (`stockcal_decompiled/`에 디컴파일 소스 실재). iOS 포팅 계획 수립됨 — 진행도는 기록 없음 ([decisions/2026-06-10-stockcalc-ios-port](../decisions/2026-06-10-stockcalc-ios-port.md))
- **1IM Video Tool**: 포맷 변환·압축·음원 추출·트림·병합. bin/에 ffmpeg.exe 수동 동봉 필요, 출력은 `[원본 폴더]\1IM Video Tool Output\[기능명]\` (출처: [sources/portfolio-logic-full](../sources/portfolio-logic-full.md))

## 이력

| 날짜 | 내용 | 출처 |
|---|---|---|
| 2026-06-10 | StockCal iOS 포팅 계획 작성 (StockCalcKit 공유 패키지 구조) | [sources/2026-06-10-stockcalc-ios-appstore](../sources/2026-06-10-stockcalc-ios-appstore.md) |

## 미확인

- StockCal v2.9 이전의 버전 이력 — 기록 없음
- iOS 포팅 실행 여부 — 계획 문서만 존재
