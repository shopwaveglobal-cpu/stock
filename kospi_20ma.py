import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import time
from datetime import datetime
import holidays

# 슬랙 설정
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

CRIT_EMOJI = "🔥"


def send_slack_message(message: str):
    try:
        requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": message},
            timeout=10
        )
    except Exception as e:
        print(f"⚠️ 슬랙 전송 실패: {e}")


def download_kospi_ohlcv_naver(days: int = 120) -> pd.DataFrame:
    base_url = "https://finance.naver.com/sise/sise_index_day.naver?code=KOSPI&page={}"
    dfs = []
    page = 1
    max_pages = 20

    while page <= max_pages:
        url = base_url.format(page)
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.select_one("table.type_1")

        if table is None:
            print(f"⚠️ 테이블을 찾을 수 없습니다 (페이지 {page})")
            break

        try:
            df = pd.read_html(StringIO(str(table)), header=0)[0].dropna()
            df['일자'] = pd.to_datetime(df['날짜'])
            df['종가'] = df['체결가'].astype(str).str.replace(",", "", regex=False).astype(float)
            dfs.append(df[['일자', '종가']])
        except Exception as e:
            print(f"⚠️ 데이터 파싱 실패 (페이지 {page}): {e}")
            break

        if sum(len(d) for d in dfs) >= days:
            break

        page += 1
        time.sleep(0.5)

    if not dfs:
        raise ValueError("❌ 유효한 데이터를 가져오지 못했습니다.")

    df_all = pd.concat(dfs, ignore_index=True).sort_values('일자')
    return df_all.tail(days).reset_index(drop=True)


def detect_20ma_break(df: pd.DataFrame):
    df = df.sort_values('일자').reset_index(drop=True)
    df['20일선'] = df['종가'].rolling(window=20).mean()
    df['이탈'] = df['종가'] < df['20일선']

    latest_idx = len(df) - 1
    latest = df.iloc[latest_idx]

    if not bool(latest['이탈']):
        print("✅ 이탈 없음 - 메시지 미발송")
        return

    # 현재 이탈 구간 시작점 탐색
    i = latest_idx
    while i > 0 and bool(df.iloc[i - 1]['이탈']):
        i -= 1
    start_idx = i

    base_20ma = float(df.iloc[start_idx]['20일선'])
    start_date = df.iloc[start_idx]['일자']
    biz_days_ago = latest_idx - start_idx

    close_today = float(latest['종가'])
    drop_today = (close_today - base_20ma) / base_20ma * 100

    if drop_today <= -10.0:
        header_emoji = CRIT_EMOJI
    elif drop_today <= -5.0:
        header_emoji = "🟥"
    elif drop_today <= -3.0:
        header_emoji = "🟨"
    else:
        header_emoji = "🟩"

    DATE_W  = 10
    CLOSE_W = 11
    DELTA_W = 8
    SIG_W   = 2

    table_header = (
        f"{'날짜':^{DATE_W}} {'종가':^{CLOSE_W-2}} {'Δ%':^{DELTA_W-2}}\n"
        + "-" * (DATE_W + CLOSE_W + DELTA_W + SIG_W + 4) + "\n"
    )
    table_body = ""

    for j in range(start_idx, len(df)):
        row = df.iloc[j]
        close = float(row['종가'])
        ma20  = float(row['20일선']) if not pd.isna(row['20일선']) else None
        drop  = (close - base_20ma) / base_20ma * 100

        if drop <= -10.0:
            flag = CRIT_EMOJI
        elif drop <= -5.0:
            flag = "🟥"
        elif drop <= -3.0:
            flag = "🟨"
        else:
            flag = "🟩"

        table_body += (
            f"{row['일자'].date().isoformat():^{DATE_W}} "
            f"{close:^{CLOSE_W},.2f} "
            f"{drop:^{DELTA_W-1}.2f}% {flag}\n"
        )

        if ma20 is not None and close > ma20:
            table_body += (
                "-" * (DATE_W + CLOSE_W + DELTA_W + SIG_W + 4) + "\n"
                f"복구일 {row['일자'].date()} 종가 {close:,.2f} > 20MA {ma20:,.2f}\n"
            )
            break

    message = (
        f"{header_emoji} *KOSPI 20MA 이탈 추적*\n"
        f"기준일 : {start_date.date()} ({biz_days_ago}영업일 전)\n"
        f"기준선 : {base_20ma:,.2f}\n"
        "───────────────\n"
        f"```\n{table_header}{table_body}```"
    )

    send_slack_message(message)
    print("📨 슬랙 메시지 발송 완료")


def is_trading_day() -> bool:
    today = datetime.today().date()
    if today.weekday() >= 5:  # 토(5), 일(6)
        return False
    kr_holidays = holidays.country_holidays("KR", years=today.year)
    return today not in kr_holidays


def main():
    today = datetime.today().date()
    if not is_trading_day():
        print(f"⏭️ 오늘({today})은 휴장일 - 스킵")
        return

    print("KOSPI 20MA 이탈 체크 시작")
    df = download_kospi_ohlcv_naver(120)
    detect_20ma_break(df)
    print("완료")


if __name__ == '__main__':
    main()
