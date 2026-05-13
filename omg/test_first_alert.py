"""
첫 자리 알림 테스트 (파란색 체크박스)
"""
from slack_notifier import send_slack_alert

def test_first_alert():
    """첫 자리 알림 테스트"""
    print("=" * 60)
    print("테스트: 첫 자리 매수 목표 접근 알림 (파란색 체크박스)")
    print("=" * 60)

    alert_data = {
        'symbol': 'ETH',
        'name': 'Ethereum',
        'rank': 2,
        'current_price': 2856.34,
        'target_price': 2800.00,
        'target': 'B2',
        'divergence': 2.01,
        'h_value': 5384.62,
        'is_first': True  # 첫 자리
    }

    print(f"\n알림 데이터:")
    print(f"  코인명: {alert_data['name']} ({alert_data['symbol']})")
    print(f"  현재가: ${alert_data['current_price']}")
    print(f"  매수목표: {alert_data['target']} - ${alert_data['target_price']}")
    print(f"  첫 자리: {alert_data['is_first']}")

    print(f"\nSlack 전송 중...")
    success = send_slack_alert(alert_data)

    if success:
        print("[성공] Slack 전송 성공! (파란색 체크박스 확인)")
    else:
        print("[실패] Slack 전송 실패!")

    return success

if __name__ == "__main__":
    test_first_alert()
