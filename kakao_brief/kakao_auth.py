"""최초 1회: 리프레시 토큰 발급. 사용: python kakao_auth.py <REST_API_KEY> <REDIRECT_URI> [인가코드] [CLIENT_SECRET]
인가코드 없이 실행하면 브라우저로 열 인증 URL을 출력하고, 코드를 받아 다시 실행하면 토큰을 출력한다."""
import sys

import requests

key, redirect = sys.argv[1], sys.argv[2]
code = sys.argv[3] if len(sys.argv) > 3 else None
if not code:
    print(f"https://kauth.kakao.com/oauth/authorize?client_id={key}&redirect_uri={redirect}&response_type=code&scope=talk_message")
    sys.exit()
body = {"grant_type": "authorization_code", "client_id": key, "redirect_uri": redirect, "code": code}
if len(sys.argv) > 4:
    body["client_secret"] = sys.argv[4]
j = requests.post("https://kauth.kakao.com/oauth/token", data=body, timeout=15).json()
print("refresh_token:", j.get("refresh_token"), "\n", {k: v for k, v in j.items() if k not in ("access_token", "refresh_token", "id_token")})
