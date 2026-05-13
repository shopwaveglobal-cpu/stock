"""
S12 Slack Block Kit 실시간 알림 테스트
"""
from slack_notifier import send_slack_realtime_alert_block_kit

def test_buy_approach_alert():
    """1차 매수선 5% 인접 알림 테스트"""
    print("=" * 60)
    print("테스트 1: 1차 매수선 5% 인접 알림 (Block Kit)")
    print("=" * 60)

    result = send_slack_realtime_alert_block_kit(
        alert_type="1차 매수선 5% 인접",
        stock_name="삼성전자",
        ticker="005930",
        current_price=72000,
        target_price=70000,
        distance_pct=2.86,
        system_label="S2"
    )

    if result:
        print("[성공] Slack Block Kit 전송 성공!")
    else:
        print("[실패] Slack Block Kit 전송 실패!")

    return result


def test_buy_execution_alert():
    """1차 매수 체결 알림 테스트"""
    print("\n" + "=" * 60)
    print("테스트 2: 1차 매수 체결 알림 (Block Kit)")
    print("=" * 60)

    sell_prices = {
        'sell1': 72100,  # +3%
        'sell2': 73500,  # +5%
        'sell3': 74900   # +7%
    }

    result = send_slack_realtime_alert_block_kit(
        alert_type="1차 매수 체결!",
        stock_name="삼성전자",
        ticker="005930",
        current_price=70050,
        target_price=70000,
        distance_pct=0.07,
        sell_prices=sell_prices,
        system_label="S2"
    )

    if result:
        print("[성공] Slack Block Kit 전송 성공!")
    else:
        print("[실패] Slack Block Kit 전송 실패!")

    return result


def test_2nd_buy_approach():
    """2차 매수선 3% 인접 알림 테스트"""
    print("\n" + "=" * 60)
    print("테스트 3: 2차 매수선 3% 인접 알림 (Block Kit)")
    print("=" * 60)

    result = send_slack_realtime_alert_block_kit(
        alert_type="2차 매수선 3% 인접",
        stock_name="SK하이닉스",
        ticker="000660",
        current_price=145000,
        target_price=140000,
        distance_pct=3.57,
        system_label="S2"
    )

    if result:
        print("[성공] Slack Block Kit 전송 성공!")
    else:
        print("[실패] Slack Block Kit 전송 실패!")

    return result


def test_3rd_buy_execution():
    """3차 매수 체결 알림 테스트"""
    print("\n" + "=" * 60)
    print("테스트 4: 3차 매수 체결 알림 (Block Kit)")
    print("=" * 60)

    sell_prices = {
        'sell1': 94600,  # +3%
        'sell2': 96500,  # +5%
        'sell3': 98100   # +7%
    }

    result = send_slack_realtime_alert_block_kit(
        alert_type="3차 매수 체결!",
        stock_name="NAVER",
        ticker="035420",
        current_price=91800,
        target_price=91700,
        distance_pct=0.11,
        sell_prices=sell_prices,
        system_label="S2",
        low_price=91600
    )

    if result:
        print("[성공] Slack Block Kit 전송 성공!")
    else:
        print("[실패] Slack Block Kit 전송 실패!")

    return result


def main():
    """모든 테스트 실행"""
    print("\n" + "=" * 60)
    print("S12 Slack Block Kit 실시간 알림 테스트")
    print("=" * 60)

    results = []

    # 테스트 1: 1차 매수선 접근
    results.append(("1차 매수선 5% 인접", test_buy_approach_alert()))

    # 테스트 2: 1차 매수 체결
    results.append(("1차 매수 체결", test_buy_execution_alert()))

    # 테스트 3: 2차 매수선 접근
    results.append(("2차 매수선 3% 인접", test_2nd_buy_approach()))

    # 테스트 4: 3차 매수 체결
    results.append(("3차 매수 체결", test_3rd_buy_execution()))

    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)

    for test_name, success in results:
        status = "[성공]" if success else "[실패]"
        print(f"  {test_name}: {status}")

    total = len(results)
    passed = sum(1 for _, success in results if success)

    print(f"\n총 {total}개 테스트 중 {passed}개 성공")

    if passed == total:
        print("\n[완료] 모든 테스트 성공!")
    else:
        print(f"\n[경고] {total - passed}개 테스트 실패")

    return passed == total


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n[오류] 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
