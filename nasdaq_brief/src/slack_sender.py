"""slack_sender.py — Slack Bot Token으로 이미지 업로드"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

CHANNEL_ID = "C0B8U4NT4EN"  # #news


def send_card(image_path: str, date_str: str) -> bool:
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise EnvironmentError("SLACK_BOT_TOKEN 환경변수가 설정되지 않았습니다.")

    client = WebClient(token=token)
    try:
        result = client.files_upload_v2(
            channel=CHANNEL_ID,
            file=image_path,
            title=f"나스닥 브리핑 {date_str}",
            initial_comment=f"📊 *나스닥 브리핑* | {date_str}",
        )
        print(f"  Slack 전송 완료: {result['file']['permalink']}")
        return True
    except SlackApiError as e:
        print(f"  Slack 전송 실패: {e.response['error']}")
        return False
