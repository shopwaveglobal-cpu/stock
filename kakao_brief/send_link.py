"""사용: python send_link.py <페이지URL> [제목] [설명]  (카드 미리보기는 샘플 데이터로 생성)"""
import sys

import kakao
import render
import sample

if len(sys.argv) < 2:
    sys.exit("사용법: python send_link.py <페이지URL> [제목] [설명]")
url = sys.argv[1]
title = sys.argv[2] if len(sys.argv) > 2 else "📊 모닝 브리핑"
desc = sys.argv[3] if len(sys.argv) > 3 else "태산 알람 · S 알림 · 지수 · 섹터 · 매크로 · 뉴스"
data = sample.make()
img = render.render_all(data, "cards")[0]
kakao.send_link(url, title, desc, img)
