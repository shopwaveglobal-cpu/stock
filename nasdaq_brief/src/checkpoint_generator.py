"""checkpoint_generator.py — 규칙 기반 AI 체크포인트 생성"""


def _nasdaq(indices):
    for idx in indices:
        if idx["name"] == "NASDAQ":
            return idx
    return {"pct": 0, "price": 0}


def _sp500(indices):
    for idx in indices:
        if idx["name"] == "S&P500":
            return idx
    return {"pct": 0}


def generate_quant_checkpoints(indices, sectors, fear_greed):
    """지수/섹터 기반 체크포인트 2개"""
    nasdaq = _nasdaq(indices)
    sp500 = _sp500(indices)
    pct = nasdaq.get("pct", 0)
    sp_pct = sp500.get("pct", 0)
    fg = fear_greed.get("score", 50)
    top = sectors[0] if sectors else None
    bot = sectors[-1] if sectors else None
    checkpoints = []

    # ── CP1: 나스닥 방향성 ──────────────────────
    if pct >= 2.0:
        t = "강세 지속 확인 — 매수 심리 우위"
        d = (f"나스닥이 {pct:+.2f}% 급등하며 강한 매수세가 유입됐습니다. "
             f"S&P500({sp_pct:+.2f}%) 대비 기술주 초과 강세. "
             f"한국장 시초가 갭업 가능성 높으며, 반도체·IT 섹터 ETF 흐름을 우선 확인하세요.")
    elif pct >= 0.8:
        t = "완만한 반등 — 방향성 탐색 구간"
        d = (f"나스닥 {pct:+.2f}% 소폭 상승 마감. 지속적 상승 추세인지 일회성 반등인지 "
             f"오늘 한국 기술주 ETF 시초가로 확인 필요합니다. 거래량 수반 여부 체크.")
    elif pct >= -0.5:
        t = "보합세 — 방향성 부재, 관망 우세"
        d = (f"나스닥 {pct:+.2f}%, 큰 방향성 없는 혼조 마감. "
             f"공포탐욕지수 {fg}점({fear_greed.get('label_ko', '')})으로 "
             f"{'과열 주의' if fg > 70 else '저점 매수 관망' if fg < 30 else '단기 추세 모니터링'} 구간입니다.")
    elif pct >= -1.5:
        t = "기술적 조정 — 단기 차익실현 우세"
        d = (f"나스닥 {pct:+.2f}% 하락. 특별한 매크로 악재 없는 기술적 조정으로 보이나, "
             f"연속 하락 여부를 확인해야 합니다. "
             f"VIX 급등 수반 여부와 S&P500({sp_pct:+.2f}%) 상대 강도를 비교하세요.")
    else:
        t = "경고 신호 — 리스크오프, 방어 포지션 고려"
        d = (f"나스닥 {pct:+.2f}% 급락. 주요 지지선 훼손 및 공포 심리 확산 가능성. "
             f"한국 기술주 단기 방어적 접근 권고. 오늘 장중 낙폭 회복 여부를 주시하세요.")

    checkpoints.append({"type": "quant", "title": t, "description": d})

    # ── CP2: 섹터 로테이션 ──────────────────────
    if top and bot:
        spread = top["pct"] - bot["pct"]
        if spread >= 3:
            t2 = f"섹터 로테이션 심화 — {top['name']} 집중 유입"
            d2 = (f"{top['name']}({top['etf']}) {top['pct']:+.1f}% vs "
                  f"{bot['name']}({bot['etf']}) {bot['pct']:+.1f}%, 격차 {spread:.1f}%p. "
                  f"자금이 특정 섹터로 집중되는 로테이션 장세입니다. "
                  f"한국 관련 섹터 ETF(예: KODEX 반도체·에너지) 흐름과 연결해 확인하세요.")
        elif spread >= 1.5:
            t2 = f"섹터 차별화 — {top['name']} 강세, {bot['name']} 약세"
            d2 = (f"섹터 간 차이 {spread:.1f}%p. 뚜렷한 로테이션은 아니나 "
                  f"상대 강도 차이가 나타나고 있습니다. 포트폴리오 내 섹터 비중 점검 시점입니다.")
        else:
            direction = "상승" if pct >= 0 else "하락"
            t2 = f"전방위 {direction} — 섹터 쏠림 없는 지수 추종"
            d2 = (f"섹터 간 등락 격차 {spread:.1f}%p로 특정 테마 집중 없이 "
                  f"시장 전반이 고르게 {direction}했습니다. "
                  f"인덱스 ETF 중심의 수동적 전략이 유효한 구간입니다.")
        checkpoints.append({"type": "quant", "title": t2, "description": d2})

    return checkpoints


NEWS_KEYWORDS = {
    "fed": ("연준 발언 주목 — 금리 경로 민감도 높음",
            "연준 관계자 발언이 시장 금리 기대에 영향을 줍니다. "
            "금리 인하/동결 신호에 따라 성장주·채권 변동성이 확대될 수 있습니다."),
    "rate": ("금리 이슈 부각 — 채권-주식 상관관계 주시",
             "금리 관련 뉴스는 기술주 밸류에이션과 직결됩니다. "
             "10년물 국채 금리 방향을 함께 확인하세요."),
    "inflation": ("물가 지표 영향 — 연준 정책 방향 가늠자",
                  "인플레이션 데이터는 연준의 금리 결정에 직접 영향을 줍니다. "
                  "예상치 대비 상회/하회 여부가 시장 방향을 좌우합니다."),
    "earnings": ("실적 시즌 모멘텀 — 개별 종목 변동성 주의",
                 "주요 기업 실적이 섹터 전반 흐름을 주도합니다. "
                 "어닝 서프라이즈/쇼크 여부를 섹터 ETF 흐름과 연결해 확인하세요."),
    "nvidia": ("AI·반도체 모멘텀 직결 — 국내 하이닉스 연동 체크",
               "NVIDIA 관련 이슈는 한국 반도체(SK하이닉스·삼성전자)와 직접 연동됩니다. "
               "XLK 섹터 흐름 및 SOXX ETF 등락률을 함께 확인하세요."),
    "apple": ("빅테크 방향성 신호 — 나스닥 전체 영향",
              "Apple은 나스닥 시가총액 1위로 지수 방향성을 주도합니다. "
              "XLK 섹터 비중 최대 종목으로 한국 기술주 ETF에도 영향을 줍니다."),
    "china": ("미중 리스크 모니터링 — 반도체·소재 섹터 주의",
              "미중 관계 관련 이슈는 반도체 수출 규제·공급망에 영향을 줍니다. "
              "한국 수출 의존 업종(반도체·2차전지)의 단기 변동성 확대 가능성을 확인하세요."),
    "job": ("고용 지표 영향 — 연준 정책 변수",
            "고용 지표는 연준의 금리 결정에 핵심 변수입니다. "
            "강한 고용 → 금리 인하 지연 우려 → 성장주 부담 흐름을 주시하세요."),
    "oil": ("유가 변동 — 에너지·소비재 섹터 연동",
            "유가 급등락은 에너지 섹터(XLE)와 항공·운송 섹터에 직접 영향을 줍니다. "
            "인플레이션 재점화 우려 여부도 함께 살펴보세요."),
}


def generate_news_checkpoint(news_items):
    """뉴스 기반 체크포인트 1개"""
    if not news_items:
        return {
            "type": "news",
            "title": "주요 이슈 부재 — 지수 기술적 흐름 집중",
            "description": "당일 시장에 영향을 줄 뚜렷한 뉴스 이벤트가 확인되지 않았습니다. "
                           "기술적 지지·저항선과 거래량 변화에 집중하세요.",
        }

    for item in news_items:
        title_lower = item.get("title_en", "").lower()
        for kw, (cp_title, cp_desc) in NEWS_KEYWORDS.items():
            if kw in title_lower:
                return {"type": "news", "title": cp_title, "description": cp_desc}

    # 기본 fallback
    first_title = news_items[0].get("title_en", "")
    short = first_title[:45] + "..." if len(first_title) > 45 else first_title
    return {
        "type": "news",
        "title": "주요 이슈 모니터링 — 전일 뉴스 연속성 체크",
        "description": (f"「{short}」 관련 뉴스가 주목받았습니다. "
                        "섹터 ETF 반응과 연결해 오늘 한국장 영향을 확인하세요."),
    }
