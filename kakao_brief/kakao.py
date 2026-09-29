"""카카오 '나에게 보내기' (REST). 환경변수: KAKAO_REST_API_KEY, KAKAO_REFRESH_TOKEN,
선택: KAKAO_CLIENT_SECRET, KAKAO_LINK_URL(제품 링크 관리에 등록한 웹 도메인)."""
import json
import os

import requests

OAUTH = "https://kauth.kakao.com/oauth/token"
UPLOAD = "https://kapi.kakao.com/v2/api/talk/message/image/upload"
MEMO = "https://kapi.kakao.com/v2/api/talk/memo/default/send"


def _check(r, what):
    if not r.ok:
        raise SystemExit(f"{what} 실패 {r.status_code}: {r.text[:300]}")
    return r.json()


def access_token():
    body = {
        "grant_type": "refresh_token",
        "client_id": os.environ["KAKAO_REST_API_KEY"],
        "refresh_token": os.environ["KAKAO_REFRESH_TOKEN"],
    }
    if os.environ.get("KAKAO_CLIENT_SECRET"):
        body["client_secret"] = os.environ["KAKAO_CLIENT_SECRET"]
    j = _check(requests.post(OAUTH, data=body, timeout=15), "토큰 갱신")
    if j.get("refresh_token"):
        print("주의: 리프레시 토큰이 갱신되었습니다. KAKAO_REFRESH_TOKEN 시크릿을 새 값으로 교체하세요.")
        if os.environ.get("GITHUB_OUTPUT"):
            print("::add-mask::" + j["refresh_token"])
        path = os.environ.get("NEW_REFRESH_TOKEN_FILE")
        if path:
            open(path, "w").write(j["refresh_token"])
    return j["access_token"]


def upload(token, path):
    with open(path, "rb") as f:
        r = requests.post(UPLOAD, headers={"Authorization": f"Bearer {token}"}, files={"file": f}, timeout=60)
    info = _check(r, "이미지 업로드")["infos"]["original"]
    return info["url"], info.get("width", 1080), info.get("height", 1080)


def send_cards(paths, date_text):
    token = access_token()
    link = os.environ.get("KAKAO_LINK_URL", "https://developers.kakao.com")
    for i, p in enumerate(paths, 1):
        url, w, h = upload(token, p)
        tpl = {
            "object_type": "feed",
            "content": {
                "title": f"📊 나스닥 모닝 브리핑 {i}/{len(paths)}",
                "description": date_text,
                "image_url": url,
                "image_width": w,
                "image_height": h,
                "link": {"web_url": link, "mobile_web_url": link},
            },
            "button_title": "자세히 보기",
        }
        r = requests.post(
            MEMO,
            headers={"Authorization": f"Bearer {token}"},
            data={"template_object": json.dumps(tpl, ensure_ascii=False)},
            timeout=15,
        )
        _check(r, f"카드 {i} 발송")
        print(f"카드 {i} 발송 완료")
