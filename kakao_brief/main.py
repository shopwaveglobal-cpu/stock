"""사용: python main.py [--sample] [--dry-run] [--out cards]"""
import argparse
import sys

import fetch
import kakao
import render
import sample


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="가짜 데이터로 렌더링 (네트워크 불필요)")
    ap.add_argument("--dry-run", action="store_true", help="카드만 만들고 카카오 발송은 생략")
    ap.add_argument("--out", default="cards")
    a = ap.parse_args()

    data = sample.make() if a.sample else fetch.collect()
    if not data.get("^IXIC"):
        sys.exit("NASDAQ 데이터를 받지 못해 중단합니다 (휴장·차단 여부 확인)")
    paths = render.render_all(data, a.out)
    print("cards:", *paths)
    if a.dry_run or a.sample:
        return
    kakao.send_cards(paths, render.header_sub(data))


if __name__ == "__main__":
    main()
