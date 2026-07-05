# decision — StockCal iOS 포팅: 계산 로직을 StockCalcKit 공유 패키지로 분리

- 날짜: 2026-06-10 / 상태: 계획 승인 (실행 진행도 미확인)
- 출처: raw/inbox/2026-06-10-stockcalc-ios-appstore.md (실제 기록)

## 배경

Windows WinForms 계산기(StockCal v2.9)를 iPhone 앱 + 커스텀 키보드로 포팅. 앱과 키보드 익스텐션이 같은 공식을 써야 함.

## 결정과 근거

- **계산 로직 전부를 `StockCalcKit` Swift 패키지로 분리** — 앱, 키보드 익스텐션, XCTest가 동일 공식 공유 (한 곳만 수정하면 됨)
- 키보드 익스텐션은 `RequestsOpenAccess` false — 네트워크·개인정보 접근 불필요, 심사 리스크 축소
- 컨테이너 앱은 단독으로 유용해야 함 (Apple 심사 요건, 원본 명시)

## 제약

- 빌드·서명·제출은 macOS + Xcode에서만 가능. Windows에서는 소스 작성까지

## 연결

- 이력·현황: [projects/local-first-apps](../projects/local-first-apps.md)
