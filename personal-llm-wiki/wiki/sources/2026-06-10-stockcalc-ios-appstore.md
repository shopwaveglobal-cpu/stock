# source — StockCal iOS App Store 포팅 계획

- 원본: raw/inbox/2026-06-10-stockcalc-ios-appstore.md (docs/superpowers/plans/에서 복사)
- 날짜: 2026-06-10 (파일명 기준) / 유형: 구현 계획
- **이 문서로 stockcalc의 실체 확인: C# WinForms 데스크톱 앱 (가상 샘플의 "vanilla JS 웹앱"과 충돌 → index 충돌 현황 #4)**

## 요약

Windows용 StockCal(WinForms, 디컴파일 소스 `stockcal_decompiled/StockCal/Form1.cs`)의 계산 로직을 Swift로 포팅해 App Store용 iPhone 계산기 + 커스텀 키보드 익스텐션을 만드는 계획. 계산 로직은 `StockCalcKit` 공유 패키지로 앱·키보드·테스트가 공용.

## 핵심 사실

- 원본 계산 로직 위치: Form1.cs (목표가 3369행, 수익률 4961행, 수량 5129행, 호가 6900행, 평단·손익 6367행) — 계획 문서 기준, 코드 변경 시 어긋날 수 있음
- 스택: Swift 6, SwiftUI, UIKit 키보드 익스텐션, iOS 17+, Xcode 16+
- 제약: 이 Windows 환경에서는 xcodebuild·서명·업로드 불가 — 빌드는 macOS 필요
- 키보드 익스텐션: `advanceToNextInputMode()` 필수, `RequestsOpenAccess` false 유지(네트워크 접근 없음)
- 앱 스토어 제약: 투자 조언·매매 권유·시세 제공 주장 금지, 로컬 계산기로 포지셔닝
- 호가 단위 테스트가 [concepts/krx-tick-size](../concepts/krx-tick-size.md) 표와 동일 값 사용

## 미확인

- 계획의 실행 여부·진행 단계 — 이 문서는 계획이며 완료 기록 아님

## 연결

- [decisions/2026-06-10-stockcalc-ios-port](../decisions/2026-06-10-stockcalc-ios-port.md)
- [projects/local-first-apps](../projects/local-first-apps.md)
- [concepts/krx-tick-size](../concepts/krx-tick-size.md)
