"""토큰 한 번 발급 후 stdout 출력 - run_trading_signal.bat에서 호출"""
import sys
import requests

APPKEY = sys.argv[1] if len(sys.argv) > 1 else ""
SECRET = sys.argv[2] if len(sys.argv) > 2 else ""

try:
    response = requests.post(
        "https://api.kiwoom.com/oauth2/token",
        headers={"Content-Type": "application/json;charset=UTF-8"},
        json={"grant_type": "client_credentials", "appkey": APPKEY, "secretkey": SECRET},
        timeout=20
    )
    data = response.json()
    token = data.get("token") or data.get("access_token")
    if token:
        print(token)
    else:
        sys.stderr.write(f"토큰 획득 실패: {data}\n")
        sys.exit(1)
except Exception as e:
    sys.stderr.write(f"토큰 요청 오류: {e}\n")
    sys.exit(1)
