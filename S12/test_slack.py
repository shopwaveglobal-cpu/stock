import requests
from dotenv import load_dotenv
import os

load_dotenv()
url = os.getenv("SLACK_WEBHOOK_URL")
r = requests.post(url, json={"text": "✅ S12 미니PC 테스트 메시지"})
print(r.status_code)