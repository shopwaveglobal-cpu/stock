"""
실제 거래 예시 알림 테스트
"""
from slack_notifier import send_slack_alert, send_slack_buy_execution_alert

def test_realistic_scenario():
    """실제 거래 시나리오 테스트"""
    print("=" * 60)
    print("실제 거래 예시 시나리오")
    print("=" * 60)

    # 시나리오 1: Bitcoin B3 매수 목표 접근 (일반)
    print("\n[시나리오 1] Bitcoin B3 매수선 접근 (5% 이내)")
    print("-" * 60)

    btc_alert = {
        'symbol': 'BTC',
        'name': 'Bitcoin',
        'rank': 1,
        'current_price': 41567.89,
        'target_price': 41000.00,
        'target': 'B3',
        'divergence': 1.38,
        'h_value': 89123.45,
        'is_first': False
    }

    print(f"코인: {btc_alert['name']} ({btc_alert['symbol']})")
    print(f"현재가: ${btc_alert['current_price']:,.2f}")
    print(f"목표가: B3 - ${btc_alert['target_price']:,.2f}")
    print(f"이격도: {btc_alert['divergence']}%")
    print(f"기준 고점: ${btc_alert['h_value']:,.2f}")

    if send_slack_alert:
        send_slack_alert(btc_alert)
        print("Slack 전송 완료\n")

    import time
    time.sleep(2)

    # 시나리오 2: Solana B1 매수 목표 접근 (첫 자리)
    print("[시나리오 2] Solana B1 매수선 접근 - 첫 자리!")
    print("-" * 60)

    sol_alert = {
        'symbol': 'SOL',
        'name': 'Solana',
        'rank': 5,
        'current_price': 112.45,
        'target_price': 110.00,
        'target': 'B1',
        'divergence': 2.23,
        'h_value': 196.43,
        'is_first': True  # 첫 자리
    }

    print(f"코인: {sol_alert['name']} ({sol_alert['symbol']})")
    print(f"현재가: ${sol_alert['current_price']:,.2f}")
    print(f"목표가: B1 - ${sol_alert['target_price']:,.2f}")
    print(f"이격도: {sol_alert['divergence']}%")
    print(f"기준 고점: ${sol_alert['h_value']:,.2f}")
    print(f"첫 자리 진입!")

    if send_slack_alert:
        send_slack_alert(sol_alert)
        print("Slack 전송 완료\n")

    time.sleep(2)

    # 시나리오 3: 작은 가격 코인 (PEPE) - 매수 체결
    print("[시나리오 3] PEPE B2 매수 체결!")
    print("-" * 60)

    pepe_execution = {
        'symbol': 'PEPE',
        'name': 'Pepe',
        'rank': 24,
        'target': 'B2',
        'target_price': 0.00000856,
        'candle_low': 0.00000851,
        'h_value': 0.00001643
    }

    pepe_price_data = {
        'avg_buy_price': 0.00000854,
        'sell_price': 0.00001002,
        'sell_threshold': 17.3
    }

    current_price = 0.00000855

    print(f"코인: {pepe_execution['name']} ({pepe_execution['symbol']})")
    print(f"매수 목표: {pepe_execution['target']} - ${pepe_execution['target_price']:.8f}")
    print(f"5분봉 저가: ${pepe_execution['candle_low']:.8f}")
    print(f"현재가: ${current_price:.8f}")
    print(f"평균매수가: ${pepe_price_data['avg_buy_price']:.8f}")
    print(f"예상 매도가: ${pepe_price_data['sell_price']:.8f} (+{pepe_price_data['sell_threshold']}%)")

    if send_slack_buy_execution_alert:
        send_slack_buy_execution_alert(pepe_execution, pepe_price_data, current_price)
        print("Slack 전송 완료\n")

    time.sleep(2)

    # 시나리오 4: Ethereum B5 매수 체결 (깊은 레벨)
    print("[시나리오 4] Ethereum B5 매수 체결 (깊은 레벨)")
    print("-" * 60)

    eth_execution = {
        'symbol': 'ETH',
        'name': 'Ethereum',
        'rank': 2,
        'target': 'B5',
        'target_price': 1825.00,
        'candle_low': 1819.50,
        'h_value': 5214.36
    }

    eth_price_data = {
        'avg_buy_price': 1822.00,
        'sell_price': 2782.00,
        'sell_threshold': 52.7
    }

    current_price = 1828.00

    print(f"코인: {eth_execution['name']} ({eth_execution['symbol']})")
    print(f"매수 목표: {eth_execution['target']} - ${eth_execution['target_price']:,.2f}")
    print(f"5분봉 저가: ${eth_execution['candle_low']:,.2f}")
    print(f"현재가: ${current_price:,.2f}")
    print(f"평균매수가: ${eth_price_data['avg_buy_price']:,.2f}")
    print(f"예상 매도가: ${eth_price_data['sell_price']:,.2f} (+{eth_price_data['sell_threshold']}%)")

    if send_slack_buy_execution_alert:
        send_slack_buy_execution_alert(eth_execution, eth_price_data, current_price)
        print("Slack 전송 완료\n")

    print("=" * 60)
    print("모든 예시 알림 전송 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_realistic_scenario()
