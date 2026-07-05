# StockCalc iOS App Store Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an App Store-ready iPhone stock calculator with a fast SwiftUI app, one-tap copy actions, and a custom keyboard extension for entering calculated prices or quantities inside trading apps.

**Architecture:** Put all calculation behavior in a shared `StockCalcKit` Swift package so the app, keyboard extension, and tests use the same formulas. Build the containing app as the complete calculator and settings surface; build the keyboard extension as a compact numeric/calculation entry surface with no network access and a required next-keyboard button.

**Tech Stack:** Swift 6, SwiftUI, UIKit keyboard extension, XCTest, Xcode 16+, iOS 17+ deployment target.

---

## Source Context

- Decompiled calculator source: `stockcal_decompiled/StockCal/Form1.cs`
- Core formula locations:
  - Target price: `stockcal_decompiled/StockCal/Form1.cs:3369`
  - Return rate: `stockcal_decompiled/StockCal/Form1.cs:4961`
  - Buying quantity: `stockcal_decompiled/StockCal/Form1.cs:5129`
  - Tick size: `stockcal_decompiled/StockCal/Form1.cs:6900`
  - Average/profit: `stockcal_decompiled/StockCal/Form1.cs:6367`

## Files

- Create: `StockCalcIOS/StockCalcKit/Package.swift`
- Create: `StockCalcIOS/StockCalcKit/Sources/StockCalcKit/StockCalcEngine.swift`
- Create: `StockCalcIOS/StockCalcKit/Tests/StockCalcKitTests/StockCalcEngineTests.swift`
- Create: `StockCalcIOS/StockCalcApp/StockCalcApp.swift`
- Create: `StockCalcIOS/StockCalcApp/ContentView.swift`
- Create: `StockCalcIOS/StockCalcApp/CalculatorViewModel.swift`
- Create: `StockCalcIOS/StockCalcApp/ClipboardClient.swift`
- Create: `StockCalcIOS/StockCalcApp/SettingsStore.swift`
- Create: `StockCalcIOS/StockCalcKeyboard/KeyboardViewController.swift`
- Create: `StockCalcIOS/StockCalcKeyboard/Info.plist`
- Create: `StockCalcIOS/AppStore/README.md`

## Constraints

- This Windows workspace cannot run `xcodebuild`, sign iOS apps, or upload to App Store Connect. Source can be authored here; build/archive/TestFlight/App Store submission must happen on macOS with Xcode.
- Keyboard extension must include a next-keyboard control using `advanceToNextInputMode()`.
- Keyboard extension should keep `RequestsOpenAccess` false. The keyboard does not need network, contacts, location, analytics, or shared keystroke access.
- The containing app must be useful on its own because Apple documents that a keyboard containing app should perform a useful function before App Store submission.
- The app must not present financial advice, recommendations, automated trading, brokerage integration, or market data claims. It is a local calculator.

---

### Task 1: Shared Calculation Engine

**Files:**
- Create: `StockCalcIOS/StockCalcKit/Package.swift`
- Create: `StockCalcIOS/StockCalcKit/Sources/StockCalcKit/StockCalcEngine.swift`
- Test: `StockCalcIOS/StockCalcKit/Tests/StockCalcKitTests/StockCalcEngineTests.swift`

- [ ] **Step 1: Write the failing tests**

Create `StockCalcIOS/StockCalcKit/Tests/StockCalcKitTests/StockCalcEngineTests.swift`:

```swift
import XCTest
@testable import StockCalcKit

final class StockCalcEngineTests: XCTestCase {
    func testTargetPriceAppliesPercentChange() {
        XCTAssertEqual(StockCalcEngine.targetPrice(basePrice: 50_000, percent: 3), 51_500)
        XCTAssertEqual(StockCalcEngine.targetPrice(basePrice: 50_000, percent: -2.5), 48_750)
    }

    func testReturnRateUsesBuyAndSellPrices() {
        XCTAssertEqual(StockCalcEngine.returnRate(buyPrice: 50_000, sellPrice: 51_500), 3, accuracy: 0.0001)
        XCTAssertEqual(StockCalcEngine.returnRate(buyPrice: 50_000, sellPrice: 48_750), -2.5, accuracy: 0.0001)
    }

    func testOrderQuantityTruncatesFractionalShares() {
        XCTAssertEqual(StockCalcEngine.orderQuantity(price: 51_500, budget: 1_000_000), 19)
    }

    func testTickSizeMatchesLegacyCalculator() {
        XCTAssertEqual(StockCalcEngine.tickSize(for: 1_999), 1)
        XCTAssertEqual(StockCalcEngine.tickSize(for: 2_000), 5)
        XCTAssertEqual(StockCalcEngine.tickSize(for: 5_000), 10)
        XCTAssertEqual(StockCalcEngine.tickSize(for: 20_000), 50)
        XCTAssertEqual(StockCalcEngine.tickSize(for: 50_000), 100)
        XCTAssertEqual(StockCalcEngine.tickSize(for: 200_000), 500)
        XCTAssertEqual(StockCalcEngine.tickSize(for: 500_000), 1_000)
    }

    func testTickNavigationRoundsDownThenMovesByCurrentStep() {
        XCTAssertEqual(StockCalcEngine.normalizeToTick(51_555), 51_500)
        XCTAssertEqual(StockCalcEngine.nextTick(after: 51_500), 51_600)
        XCTAssertEqual(StockCalcEngine.previousTick(before: 51_500), 51_400)
    }

    func testAverageAndProfitCalculationIncludesCommissionAndTax() {
        let buyLots = [
            StockLot(price: 50_000, quantity: 10),
            StockLot(price: 48_000, quantity: 10)
        ]
        let sellLots = [
            StockLot(price: 52_000, quantity: 20)
        ]

        let result = StockCalcEngine.profitLoss(
            buyLots: buyLots,
            sellLots: sellLots,
            commissionRatePercent: 0.015,
            taxRatePercent: 0.18
        )

        XCTAssertEqual(result.buyQuantity, 20)
        XCTAssertEqual(result.buyAmount, 980_000, accuracy: 0.001)
        XCTAssertEqual(result.buyAveragePrice, 49_000, accuracy: 0.001)
        XCTAssertEqual(result.sellQuantity, 20)
        XCTAssertEqual(result.sellAmount, 1_040_000, accuracy: 0.001)
        XCTAssertEqual(result.sellAveragePrice, 52_000, accuracy: 0.001)
        XCTAssertEqual(result.commission, 303, accuracy: 0.001)
        XCTAssertEqual(result.tax, 1_872, accuracy: 0.001)
        XCTAssertEqual(result.profit, 57_825, accuracy: 0.001)
        XCTAssertEqual(result.profitRate, 5.9005, accuracy: 0.0001)
    }
}
```

- [ ] **Step 2: Add the Swift package manifest**

Create `StockCalcIOS/StockCalcKit/Package.swift`:

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "StockCalcKit",
    platforms: [.iOS(.v17)],
    products: [
        .library(name: "StockCalcKit", targets: ["StockCalcKit"])
    ],
    targets: [
        .target(name: "StockCalcKit"),
        .testTarget(name: "StockCalcKitTests", dependencies: ["StockCalcKit"])
    ]
)
```

- [ ] **Step 3: Run tests and verify RED**

Run on macOS:

```bash
cd StockCalcIOS/StockCalcKit
swift test
```

Expected: FAIL because `StockCalcKit` and `StockCalcEngine` are not implemented yet.

- [ ] **Step 4: Implement the calculation engine**

Create `StockCalcIOS/StockCalcKit/Sources/StockCalcKit/StockCalcEngine.swift`:

```swift
import Foundation

public struct StockLot: Equatable {
    public let price: Double
    public let quantity: Int

    public init(price: Double, quantity: Int) {
        self.price = price
        self.quantity = quantity
    }

    public var amount: Double {
        price * Double(quantity)
    }
}

public struct ProfitLossResult: Equatable {
    public let buyQuantity: Int
    public let buyAmount: Double
    public let buyAveragePrice: Double
    public let sellQuantity: Int
    public let sellAmount: Double
    public let sellAveragePrice: Double
    public let commission: Double
    public let tax: Double
    public let profit: Double
    public let profitRate: Double
}

public enum StockCalcEngine {
    public static func targetPrice(basePrice: Double, percent: Double) -> Double {
        basePrice + basePrice * (percent / 100)
    }

    public static func returnRate(buyPrice: Double, sellPrice: Double) -> Double {
        guard buyPrice != 0 else { return 0 }
        return (sellPrice - buyPrice) / buyPrice * 100
    }

    public static func orderQuantity(price: Double, budget: Double) -> Int {
        guard price > 0, budget > 0 else { return 0 }
        return Int(floor(budget / price))
    }

    public static func tickSize(for price: Double) -> Double {
        switch price {
        case ...1_999: return 1
        case 2_000...4_999: return 5
        case 5_000...19_999: return 10
        case 20_000...49_999: return 50
        case 50_000...199_999: return 100
        case 200_000...499_999: return 500
        default: return 1_000
        }
    }

    public static func normalizeToTick(_ price: Double) -> Double {
        let step = tickSize(for: price)
        return price - price.truncatingRemainder(dividingBy: step)
    }

    public static func nextTick(after price: Double) -> Double {
        price + tickSize(for: price)
    }

    public static func previousTick(before price: Double) -> Double {
        let step = tickSize(for: price - 1)
        return max(0, price - step)
    }

    public static func weightedAverage(lots: [StockLot]) -> (quantity: Int, amount: Double, average: Double) {
        let quantity = lots.reduce(0) { $0 + max(0, $1.quantity) }
        let amount = lots.reduce(0) { $0 + (max(0, $1.price) * Double(max(0, $1.quantity))) }
        return (quantity, amount, quantity > 0 ? amount / Double(quantity) : 0)
    }

    public static func profitLoss(
        buyLots: [StockLot],
        sellLots: [StockLot],
        commissionRatePercent: Double,
        taxRatePercent: Double
    ) -> ProfitLossResult {
        let buy = weightedAverage(lots: buyLots)
        let sell = weightedAverage(lots: sellLots)
        let commission = buy.amount * (commissionRatePercent / 100) + sell.amount * (commissionRatePercent / 100)
        let tax = sell.amount * (taxRatePercent / 100)
        let profit = (sell.average - buy.average) * Double(min(buy.quantity, sell.quantity)) - commission - tax
        let invested = buy.average * Double(min(buy.quantity, sell.quantity))
        let profitRate = invested > 0 ? profit / invested * 100 : 0

        return ProfitLossResult(
            buyQuantity: buy.quantity,
            buyAmount: buy.amount,
            buyAveragePrice: buy.average,
            sellQuantity: sell.quantity,
            sellAmount: sell.amount,
            sellAveragePrice: sell.average,
            commission: commission,
            tax: tax,
            profit: profit,
            profitRate: profitRate
        )
    }
}
```

- [ ] **Step 5: Run tests and verify GREEN**

Run on macOS:

```bash
cd StockCalcIOS/StockCalcKit
swift test
```

Expected: PASS, 6 tests.

- [ ] **Step 6: Commit**

```bash
git add StockCalcIOS/StockCalcKit
git commit -m "feat: add shared stock calculation engine"
```

---

### Task 2: SwiftUI Containing App MVP

**Files:**
- Create: `StockCalcIOS/StockCalcApp/StockCalcApp.swift`
- Create: `StockCalcIOS/StockCalcApp/ContentView.swift`
- Create: `StockCalcIOS/StockCalcApp/CalculatorViewModel.swift`
- Create: `StockCalcIOS/StockCalcApp/ClipboardClient.swift`
- Create: `StockCalcIOS/StockCalcApp/SettingsStore.swift`

- [ ] **Step 1: Write view-model tests in the Xcode app test target**

Create `StockCalcIOS/StockCalcAppTests/CalculatorViewModelTests.swift`:

```swift
import XCTest
@testable import StockCalcApp

final class CalculatorViewModelTests: XCTestCase {
    func testTargetPriceCopyTextRemovesGroupingSeparators() {
        let model = CalculatorViewModel()
        model.basePriceText = "50000"
        model.percentText = "3"
        XCTAssertEqual(model.targetPriceText, "51,500")
        XCTAssertEqual(model.targetPriceCopyValue, "51500")
    }

    func testQuantityCopyTextIsIntegerOnly() {
        let model = CalculatorViewModel()
        model.quantityPriceText = "51500"
        model.budgetText = "1000000"
        XCTAssertEqual(model.orderQuantityText, "19")
        XCTAssertEqual(model.orderQuantityCopyValue, "19")
    }
}
```

- [ ] **Step 2: Run tests and verify RED**

Run on macOS after Xcode project creation:

```bash
xcodebuild test -scheme StockCalcApp -destination 'platform=iOS Simulator,name=iPhone 16'
```

Expected: FAIL because `CalculatorViewModel` does not exist.

- [ ] **Step 3: Implement `CalculatorViewModel`**

Create `StockCalcIOS/StockCalcApp/CalculatorViewModel.swift`:

```swift
import Foundation
import StockCalcKit

@MainActor
final class CalculatorViewModel: ObservableObject {
    @Published var basePriceText = ""
    @Published var percentText = ""
    @Published var buyPriceText = ""
    @Published var sellPriceText = ""
    @Published var quantityPriceText = ""
    @Published var budgetText = ""

    private let numberFormatter: NumberFormatter = {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.maximumFractionDigits = 1
        return formatter
    }()

    var targetPriceText: String {
        formatWon(StockCalcEngine.targetPrice(basePrice: number(basePriceText), percent: number(percentText)))
    }

    var targetPriceCopyValue: String {
        ungrouped(targetPriceText)
    }

    var returnRateText: String {
        String(format: "%.2f%%", StockCalcEngine.returnRate(buyPrice: number(buyPriceText), sellPrice: number(sellPriceText)))
    }

    var orderQuantityText: String {
        "\(StockCalcEngine.orderQuantity(price: number(quantityPriceText), budget: number(budgetText)))"
    }

    var orderQuantityCopyValue: String {
        orderQuantityText
    }

    func number(_ text: String) -> Double {
        Double(text.replacingOccurrences(of: ",", with: "")) ?? 0
    }

    func formatWon(_ value: Double) -> String {
        numberFormatter.string(from: NSNumber(value: value)) ?? "0"
    }

    func ungrouped(_ text: String) -> String {
        text.replacingOccurrences(of: ",", with: "").replacingOccurrences(of: "%", with: "")
    }
}
```

- [ ] **Step 4: Implement clipboard and settings clients**

Create `StockCalcIOS/StockCalcApp/ClipboardClient.swift`:

```swift
import UIKit

struct ClipboardClient {
    func copy(_ value: String) {
        UIPasteboard.general.string = value
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
    }
}
```

Create `StockCalcIOS/StockCalcApp/SettingsStore.swift`:

```swift
import Foundation

@MainActor
final class SettingsStore: ObservableObject {
    @Published var commissionRatePercent: Double {
        didSet { UserDefaults.standard.set(commissionRatePercent, forKey: "commissionRatePercent") }
    }

    @Published var taxRatePercent: Double {
        didSet { UserDefaults.standard.set(taxRatePercent, forKey: "taxRatePercent") }
    }

    init() {
        let defaults = UserDefaults.standard
        let savedCommission = defaults.object(forKey: "commissionRatePercent") as? Double
        let savedTax = defaults.object(forKey: "taxRatePercent") as? Double
        self.commissionRatePercent = savedCommission ?? 0.015
        self.taxRatePercent = savedTax ?? 0.18
    }
}
```

- [ ] **Step 5: Implement app entry and main UI**

Create `StockCalcIOS/StockCalcApp/StockCalcApp.swift`:

```swift
import SwiftUI

@main
struct StockCalcApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

Create `StockCalcIOS/StockCalcApp/ContentView.swift`:

```swift
import SwiftUI

struct ContentView: View {
    @StateObject private var model = CalculatorViewModel()
    private let clipboard = ClipboardClient()

    var body: some View {
        NavigationStack {
            Form {
                Section("목표가") {
                    TextField("기준가", text: $model.basePriceText)
                        .keyboardType(.numberPad)
                    TextField("등락률 %", text: $model.percentText)
                        .keyboardType(.decimalPad)
                    ResultRow(title: "계산가", value: model.targetPriceText) {
                        clipboard.copy(model.targetPriceCopyValue)
                    }
                }

                Section("수익률") {
                    TextField("매수가", text: $model.buyPriceText)
                        .keyboardType(.numberPad)
                    TextField("매도가", text: $model.sellPriceText)
                        .keyboardType(.numberPad)
                    Text(model.returnRateText)
                        .font(.title2.bold())
                        .foregroundStyle(model.returnRateText.hasPrefix("-") ? .blue : .red)
                }

                Section("주문 수량") {
                    TextField("현재가", text: $model.quantityPriceText)
                        .keyboardType(.numberPad)
                    TextField("투입금액", text: $model.budgetText)
                        .keyboardType(.numberPad)
                    ResultRow(title: "주문 가능", value: model.orderQuantityText) {
                        clipboard.copy(model.orderQuantityCopyValue)
                    }
                }
            }
            .navigationTitle("주식계산기")
        }
    }
}

private struct ResultRow: View {
    let title: String
    let value: String
    let copy: () -> Void

    var body: some View {
        HStack {
            Text(title)
            Spacer()
            Text(value)
                .font(.title3.monospacedDigit().bold())
            Button("복사", action: copy)
                .buttonStyle(.borderedProminent)
        }
    }
}
```

- [ ] **Step 6: Run tests and verify GREEN**

Run on macOS:

```bash
xcodebuild test -scheme StockCalcApp -destination 'platform=iOS Simulator,name=iPhone 16'
```

Expected: PASS for `CalculatorViewModelTests` and `StockCalcKitTests`.

- [ ] **Step 7: Commit**

```bash
git add StockCalcIOS/StockCalcApp StockCalcIOS/StockCalcAppTests
git commit -m "feat: add fast stock calculator iOS app"
```

---

### Task 3: Custom Keyboard Extension Proof of Concept

**Files:**
- Create: `StockCalcIOS/StockCalcKeyboard/KeyboardViewController.swift`
- Create: `StockCalcIOS/StockCalcKeyboard/Info.plist`

- [ ] **Step 1: Write manual acceptance test**

Create `StockCalcIOS/AppStore/keyboard-acceptance.md`:

```markdown
# Keyboard Acceptance Test

1. Install app on iPhone from Xcode.
2. Enable keyboard in Settings > General > Keyboard > Keyboards.
3. Open Notes and place cursor in a normal text field.
4. Switch to "주식계산기" keyboard.
5. Enter `50000`, tap `+3%`, tap `입력`.
6. Expected inserted text: `51500`.
7. Tap globe key.
8. Expected: system switches to the next keyboard.
9. Open a secure password field.
10. Expected: iOS replaces custom keyboard with system keyboard.
```

- [ ] **Step 2: Implement keyboard Info.plist**

Create `StockCalcIOS/StockCalcKeyboard/Info.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSExtension</key>
    <dict>
        <key>NSExtensionAttributes</key>
        <dict>
            <key>IsASCIICapable</key>
            <true/>
            <key>PrefersRightToLeft</key>
            <false/>
            <key>PrimaryLanguage</key>
            <string>ko-KR</string>
            <key>RequestsOpenAccess</key>
            <false/>
        </dict>
        <key>NSExtensionPointIdentifier</key>
        <string>com.apple.keyboard-service</string>
        <key>NSExtensionPrincipalClass</key>
        <string>$(PRODUCT_MODULE_NAME).KeyboardViewController</string>
    </dict>
</dict>
</plist>
```

- [ ] **Step 3: Implement compact keyboard controller**

Create `StockCalcIOS/StockCalcKeyboard/KeyboardViewController.swift`:

```swift
import UIKit
import StockCalcKit

final class KeyboardViewController: UIInputViewController {
    private var input = ""
    private var result = ""
    private let display = UILabel()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        buildKeyboard()
    }

    private func buildKeyboard() {
        display.font = .monospacedDigitSystemFont(ofSize: 24, weight: .bold)
        display.textAlignment = .right
        display.text = "0"

        let rows: [[String]] = [
            ["🌐", "⌫", "C", "입력"],
            ["7", "8", "9", "+3%"],
            ["4", "5", "6", "-2%"],
            ["1", "2", "3", "+5%"],
            ["0", "00", ".", "수량"]
        ]

        let stack = UIStackView()
        stack.axis = .vertical
        stack.spacing = 6
        stack.translatesAutoresizingMaskIntoConstraints = false

        stack.addArrangedSubview(display)

        for row in rows {
            let rowStack = UIStackView()
            rowStack.axis = .horizontal
            rowStack.distribution = .fillEqually
            rowStack.spacing = 6

            for title in row {
                let button = UIButton(type: .system)
                button.setTitle(title, for: .normal)
                button.titleLabel?.font = .systemFont(ofSize: 18, weight: .semibold)
                button.backgroundColor = .secondarySystemBackground
                button.layer.cornerRadius = 8
                button.addAction(UIAction { [weak self] _ in self?.tap(title) }, for: .touchUpInside)
                rowStack.addArrangedSubview(button)
            }

            stack.addArrangedSubview(rowStack)
        }

        view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 8),
            stack.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -8),
            stack.topAnchor.constraint(equalTo: view.topAnchor, constant: 8),
            stack.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -8)
        ])
    }

    private func tap(_ key: String) {
        switch key {
        case "🌐":
            advanceToNextInputMode()
        case "⌫":
            if input.isEmpty {
                textDocumentProxy.deleteBackward()
            } else {
                input.removeLast()
                refresh()
            }
        case "C":
            input = ""
            result = ""
            refresh()
        case "입력":
            textDocumentProxy.insertText(result.isEmpty ? input : result)
        case "+3%", "-2%", "+5%":
            let percent = Double(key.replacingOccurrences(of: "%", with: "")) ?? 0
            let value = StockCalcEngine.targetPrice(basePrice: Double(input) ?? 0, percent: percent)
            result = String(Int(value.rounded()))
            refresh()
        case "수량":
            result = input
            refresh()
        default:
            input.append(key)
            result = ""
            refresh()
        }
    }

    private func refresh() {
        display.text = result.isEmpty ? (input.isEmpty ? "0" : input) : result
    }
}
```

- [ ] **Step 4: Run manual acceptance test**

Run on macOS with a physical iPhone:

```bash
xcodebuild build -scheme StockCalcApp -destination 'platform=iOS,name=<DEVICE_NAME>'
```

Expected: build succeeds. Then complete `StockCalcIOS/AppStore/keyboard-acceptance.md` manually.

- [ ] **Step 5: Commit**

```bash
git add StockCalcIOS/StockCalcKeyboard StockCalcIOS/AppStore/keyboard-acceptance.md
git commit -m "feat: add stock calculator keyboard extension"
```

---

### Task 4: Xcode Project Assembly

**Files:**
- Create via Xcode: `StockCalcIOS/StockCalcIOS.xcodeproj`
- Modify via Xcode: app target build settings
- Modify via Xcode: keyboard extension target build settings

- [ ] **Step 1: Create Xcode project**

Run on macOS:

```text
Xcode > File > New > Project > iOS App
Product Name: StockCalc
Interface: SwiftUI
Language: Swift
Include Tests: Yes
Location: StockCalcIOS
```

Expected: `StockCalcIOS/StockCalcIOS.xcodeproj` exists.

- [ ] **Step 2: Add shared package**

In Xcode:

```text
File > Add Package Dependencies > Add Local...
Choose: StockCalcIOS/StockCalcKit
Add product StockCalcKit to StockCalc app target.
Add product StockCalcKit to StockCalcKeyboard target.
```

Expected: both targets can `import StockCalcKit`.

- [ ] **Step 3: Add keyboard extension target**

In Xcode:

```text
File > New > Target > iOS > Custom Keyboard Extension
Product Name: StockCalcKeyboard
Embed in Application: StockCalc
```

Expected: keyboard extension target exists and is embedded in the containing app.

- [ ] **Step 4: Replace generated files with planned files**

Move or copy:

```text
StockCalcIOS/StockCalcApp/*.swift -> app target membership: StockCalc
StockCalcIOS/StockCalcKeyboard/*.swift -> target membership: StockCalcKeyboard
StockCalcIOS/StockCalcKeyboard/Info.plist -> keyboard target Info.plist
```

Expected: generated duplicate app/keyboard files are removed from target membership.

- [ ] **Step 5: Configure bundle identifiers**

Set:

```text
App bundle identifier: com.<developer-domain>.stockcalc
Keyboard bundle identifier: com.<developer-domain>.stockcalc.keyboard
Display name: 주식계산기
Keyboard display name: 주식계산기
Deployment target: iOS 17.0
```

Expected: Xcode signing panel shows both targets with valid bundle IDs.

- [ ] **Step 6: Run full Xcode tests**

Run:

```bash
xcodebuild test -scheme StockCalc -destination 'platform=iOS Simulator,name=iPhone 16'
```

Expected: all unit tests pass.

- [ ] **Step 7: Commit**

```bash
git add StockCalcIOS
git commit -m "chore: assemble App Store iOS project"
```

---

### Task 5: App Store Readiness

**Files:**
- Create: `StockCalcIOS/AppStore/README.md`
- Create: `StockCalcIOS/AppStore/review-notes-ko.md`

- [ ] **Step 1: Create App Store checklist**

Create `StockCalcIOS/AppStore/README.md`:

```markdown
# App Store Readiness

## Required

- Apple Developer Program membership is active.
- Bundle ID `com.<developer-domain>.stockcalc` is registered.
- Bundle ID `com.<developer-domain>.stockcalc.keyboard` is registered.
- App target and keyboard extension target use automatic signing or valid provisioning profiles.
- Privacy nutrition labels declare no data collection.
- Support URL is live and contains contact information.
- Marketing URL is optional.
- App category is Finance or Utilities.
- Age rating has no restricted content.
- Screenshots are prepared for required iPhone sizes.
- App Review notes explain the custom keyboard and that it performs local calculation only.

## Archive

Run in Xcode:

1. Select Any iOS Device.
2. Product > Archive.
3. Validate App.
4. Distribute App > App Store Connect > Upload.

## TestFlight

1. Wait for build processing in App Store Connect.
2. Add internal testers.
3. Test app launch, copy actions, keyboard enablement, and keyboard insertion.
4. Fix crashes or confusing review flows before public submission.
```

- [ ] **Step 2: Create App Review notes**

Create `StockCalcIOS/AppStore/review-notes-ko.md`:

```markdown
# App Review Notes

이 앱은 주식 주문 시 가격, 수량, 평단, 손익을 빠르게 계산하는 로컬 계산기입니다.

앱은 계좌 연동, 주문 실행, 자동매매, 투자 추천, 시세 제공 기능을 포함하지 않습니다.
모든 계산은 기기 내에서 수행됩니다.
서버, 로그인, 광고, 분석 SDK, 개인정보 수집 기능이 없습니다.

커스텀 키보드 확장은 사용자가 가격 또는 수량 입력칸에 계산 결과를 빠르게 입력할 수 있도록 제공됩니다.
키보드 확장은 네트워크 접근 권한을 요청하지 않으며 `RequestsOpenAccess`를 false로 유지합니다.
키보드의 지구본 버튼을 누르면 다음 키보드로 전환됩니다.

테스트 방법:

1. 앱을 실행하여 목표가, 수익률, 주문 수량 계산을 확인합니다.
2. 결과값 옆의 복사 버튼을 눌러 클립보드 복사를 확인합니다.
3. 설정 앱에서 `주식계산기` 키보드를 활성화합니다.
4. Notes 앱의 일반 텍스트 입력칸에서 키보드를 선택합니다.
5. `50000`, `+3%`, `입력`을 눌러 `51500`이 입력되는지 확인합니다.
```

- [ ] **Step 3: Verify App Store checklist**

Run through every checkbox in `StockCalcIOS/AppStore/README.md`.

Expected: every required item has an owner or is completed before App Store submission.

- [ ] **Step 4: Commit**

```bash
git add StockCalcIOS/AppStore
git commit -m "docs: add App Store submission checklist"
```

---

## Self-Review

- Spec coverage: The plan covers legacy formula extraction, Swift shared logic, fast iOS app, one-tap copy, custom keyboard extension, and App Store submission preparation.
- Placeholder scan: The only `<developer-domain>` and `<DEVICE_NAME>` values are environment-specific values that must be supplied by the Apple Developer account and connected device. No implementation task depends on unspecified code.
- Type consistency: `StockCalcEngine`, `StockLot`, `ProfitLossResult`, and `CalculatorViewModel` names are consistent across tasks.

