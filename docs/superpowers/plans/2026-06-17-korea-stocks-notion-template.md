# 한국 주식 노션 템플릿 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 코스피/코스닥 종목 데이터를 노션 import용 CSV와 한국어 가이드 문서로 생성하는 1차 판매 가능 템플릿 패키지를 만든다.

**Architecture:** 데이터 스키마, 필터링, 변환, CSV 출력, 문서 생성을 작은 모듈로 분리한다. 1차 버전은 수동으로 내려받은 KRX/거래소 CSV를 입력으로 받아 전체 종목 master/update 파일을 생성하고, 샘플 데이터만으로도 테스트와 데모 출력이 가능해야 한다.

**Tech Stack:** Python 3 표준 라이브러리(`csv`, `argparse`, `datetime`, `pathlib`, `dataclasses`), `pytest`, Markdown, UTF-8 with BOM CSV.

---

## 파일 구조

구현 후 생성되는 파일과 책임은 아래와 같다.

- Create: `notion_korea_stocks_template/README.md`
  - 프로젝트 사용법 요약.
- Create: `notion_korea_stocks_template/data/listings_sample.csv`
  - 테스트와 데모 실행에 쓰는 샘플 상장 종목 입력 파일.
- Create: `notion_korea_stocks_template/data/theme_seed.csv`
  - 테마 분류 수동 관리 파일.
- Create: `notion_korea_stocks_template/data/excluded_stocks.csv`
  - 실행 시 생성되는 스팩 제외 감사 파일.
- Create: `notion_korea_stocks_template/output/stocks_master.csv`
  - 실행 시 생성되는 노션 최초 import용 master CSV.
- Create: `notion_korea_stocks_template/output/stocks_update_weekly.csv`
  - 실행 시 생성되는 구독 업데이트용 CSV.
- Create: `notion_korea_stocks_template/output/change_log.md`
  - 실행 시 생성되는 변경 요약 문서.
- Create: `notion_korea_stocks_template/docs/notion_database_schema.md`
  - 고객이 읽는 한국어 노션 속성 가이드.
- Create: `notion_korea_stocks_template/docs/notion_views.md`
  - 고객이 읽는 한국어 추천 뷰 가이드.
- Create: `notion_korea_stocks_template/docs/update_strategy.md`
  - 고객이 읽는 한국어 업데이트 운영 가이드.
- Create: `notion_korea_stocks_template/docs/customer_setup_guide.md`
  - 고객이 따라 하는 한국어 설치/사용 가이드.
- Create: `notion_korea_stocks_template/stock_template/__init__.py`
  - 내부 패키지 표시.
- Create: `notion_korea_stocks_template/stock_template/schema.py`
  - 컬럼 순서와 공급자/사용자 필드 소유권 정의.
- Create: `notion_korea_stocks_template/stock_template/rules.py`
  - 스팩 필터링, 시총 구간, 재무주의 규칙.
- Create: `notion_korea_stocks_template/stock_template/io.py`
  - CSV 읽기/쓰기와 한글 인코딩 처리.
- Create: `notion_korea_stocks_template/stock_template/themes.py`
  - 테마 시드 로딩과 종목별 테마 병합.
- Create: `notion_korea_stocks_template/stock_template/transform.py`
  - 입력 종목 행을 노션 master/update 행으로 변환.
- Create: `notion_korea_stocks_template/stock_template/changelog.py`
  - 변경 로그 문서 생성.
- Create: `notion_korea_stocks_template/scripts/build_stocks_master.py`
  - master CSV 생성 CLI.
- Create: `notion_korea_stocks_template/scripts/build_weekly_update.py`
  - weekly update CSV와 change log 생성 CLI.
- Create: `notion_korea_stocks_template/tests/test_rules.py`
  - 스팩/시총/재무주의 규칙 테스트.
- Create: `notion_korea_stocks_template/tests/test_schema.py`
  - 컬럼 소유권과 update 컬럼 테스트.
- Create: `notion_korea_stocks_template/tests/test_transform.py`
  - master/update 변환 테스트.

## 입력 데이터 규격

1차 버전은 사용자가 KRX 등에서 내려받은 CSV를 `--listings-csv`로 넣는 방식이다. 이 방식이면 네트워크가 막힌 환경에서도 실행되고, 추후 자동 수집 어댑터를 붙여도 변환/출력 코드는 그대로 유지된다.

입력 CSV는 아래 컬럼을 지원한다.

| 표준 컬럼 | 허용 별칭 | 필수 여부 |
| --- | --- | --- |
| `종목코드` | `단축코드`, `code`, `ticker` | 필수 |
| `종목명` | `한글 종목명`, `name`, `company` | 필수 |
| `시장` | `시장구분`, `market` | 필수 |
| `업종` | `업종명`, `sector`, `industry` | 선택 |
| `현재가` | `종가`, `price`, `close` | 선택 |
| `시가총액` | `market_cap`, `marcap` | 선택 |
| `발행주식수` | `shares`, `listed_shares` | 선택 |
| `DART코드` | `corp_code`, `dart_code` | 선택 |

필수 컬럼이 없으면 CLI는 실행을 중단하고 누락된 컬럼명을 출력한다.

---

### Task 1: 프로젝트 골격과 샘플 데이터

**Files:**
- Create: `notion_korea_stocks_template/README.md`
- Create: `notion_korea_stocks_template/stock_template/__init__.py`
- Create: `notion_korea_stocks_template/data/listings_sample.csv`
- Create: `notion_korea_stocks_template/data/theme_seed.csv`

- [ ] **Step 1: 폴더를 만든다**

Run:

```powershell
New-Item -ItemType Directory -Force `
  notion_korea_stocks_template, `
  notion_korea_stocks_template\data, `
  notion_korea_stocks_template\output, `
  notion_korea_stocks_template\docs, `
  notion_korea_stocks_template\scripts, `
  notion_korea_stocks_template\stock_template, `
  notion_korea_stocks_template\tests
```

Expected: 각 폴더가 생성되고 오류가 없다.

- [ ] **Step 2: 패키지 파일을 만든다**

Create `notion_korea_stocks_template/stock_template/__init__.py`:

```python
"""Notion-ready Korea stock template generator."""
```

- [ ] **Step 3: 샘플 상장 종목 CSV를 만든다**

Create `notion_korea_stocks_template/data/listings_sample.csv` with UTF-8:

```csv
종목코드,종목명,시장,업종,현재가,시가총액,발행주식수,DART코드
005930,삼성전자,KOSPI,반도체,80000,477000000000000,5969782550,00126380
000660,SK하이닉스,KOSPI,반도체,220000,160000000000000,728002365,00164779
035720,카카오,KOSPI,서비스업,52000,23000000000000,443000000,00258801
123456,테스트스팩1호,KOSDAQ,금융,2100,80000000000,38000000,00999999
247540,에코프로비엠,KOSDAQ,2차전지,180000,17600000000000,97801344,01234567
```

- [ ] **Step 4: 테마 시드 CSV를 만든다**

Create `notion_korea_stocks_template/data/theme_seed.csv`:

```csv
종목코드,종목명,테마,테마근거,검수상태
005930,삼성전자,반도체,메모리와 파운드리 주요 기업,검수완료
000660,SK하이닉스,반도체,메모리 반도체 주요 기업,검수완료
247540,에코프로비엠,2차전지,양극재 주요 기업,검수완료
```

- [ ] **Step 5: README 초안을 만든다**

Create `notion_korea_stocks_template/README.md`:

```markdown
# 한국 주식 노션 템플릿 생성기

코스피/코스닥 종목 데이터를 노션 import용 CSV로 만드는 도구입니다.

## 1차 사용 방식

1. KRX 또는 보유 데이터에서 상장 종목 CSV를 준비합니다.
2. `scripts/build_stocks_master.py`를 실행해 `output/stocks_master.csv`를 만듭니다.
3. 노션에서 CSV를 import합니다.
4. 추천 뷰와 속성 타입은 `docs/` 문서를 보고 설정합니다.

## 빠른 데모

```powershell
python scripts/build_stocks_master.py --listings-csv data/listings_sample.csv --theme-csv data/theme_seed.csv
python scripts/build_weekly_update.py --master-csv output/stocks_master.csv
```

CSV는 한글 깨짐을 줄이기 위해 UTF-8 with BOM으로 저장됩니다.
```

- [ ] **Step 6: 커밋한다**

Run:

```powershell
git add notion_korea_stocks_template
git commit -m "feat: scaffold korea stocks notion template"
```

Expected: 새 프로젝트 골격 커밋이 생성된다.

---

### Task 2: 스키마와 필드 소유권

**Files:**
- Create: `notion_korea_stocks_template/stock_template/schema.py`
- Create: `notion_korea_stocks_template/tests/test_schema.py`

- [ ] **Step 1: 실패하는 테스트를 작성한다**

Create `notion_korea_stocks_template/tests/test_schema.py`:

```python
from stock_template.schema import (
    CUSTOMER_MANAGED_COLUMNS,
    MASTER_COLUMNS,
    PROVIDER_MANAGED_COLUMNS,
    UPDATE_COLUMNS,
)


def test_master_contains_provider_and_customer_columns():
    assert "종목명" in MASTER_COLUMNS
    assert "종목코드" in MASTER_COLUMNS
    assert "투자아이디어" in MASTER_COLUMNS
    assert "시가총액" in MASTER_COLUMNS


def test_weekly_update_excludes_customer_managed_columns():
    for column in CUSTOMER_MANAGED_COLUMNS:
        assert column not in UPDATE_COLUMNS


def test_update_columns_keep_stock_code_as_merge_key():
    assert UPDATE_COLUMNS[0] == "종목코드"
    assert "종목명" in UPDATE_COLUMNS
    assert "데이터 기준일" in UPDATE_COLUMNS


def test_column_ownership_sets_do_not_overlap():
    assert set(PROVIDER_MANAGED_COLUMNS).isdisjoint(set(CUSTOMER_MANAGED_COLUMNS))
```

- [ ] **Step 2: 테스트가 실패하는지 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
pytest tests/test_schema.py -v
```

Expected: `ModuleNotFoundError` 또는 `ImportError`로 실패한다.

- [ ] **Step 3: 스키마를 구현한다**

Create `notion_korea_stocks_template/stock_template/schema.py`:

```python
IDENTITY_COLUMNS = [
    "종목명",
    "종목코드",
    "시장",
    "데이터 기준일",
    "상태",
]

PROVIDER_MANAGED_COLUMNS = [
    "업종",
    "테마",
    "시가총액",
    "시총구간",
    "시총 5조 이상",
    "현재가",
    "발행주식수",
    "DART코드",
    "자본총계",
    "부채총계",
    "유동자산",
    "유동부채",
    "재고자산",
    "매출액 최근연도",
    "영업이익 최근연도",
    "당기순이익 최근연도",
    "부채비율",
    "유동비율",
    "당좌비율",
    "자본잠식 여부",
    "재무주의",
    "분석메모_공급자",
]

CUSTOMER_MANAGED_COLUMNS = [
    "관심도",
    "보유여부",
    "매수예정가",
    "목표가",
    "손절가",
    "매수일",
    "매도일",
    "투자아이디어",
    "리스크메모",
    "매매복기",
    "내 태그",
]

MASTER_COLUMNS = IDENTITY_COLUMNS + PROVIDER_MANAGED_COLUMNS + CUSTOMER_MANAGED_COLUMNS

UPDATE_COLUMNS = [
    "종목코드",
    "종목명",
    "시장",
    "데이터 기준일",
    "상태",
] + PROVIDER_MANAGED_COLUMNS
```

- [ ] **Step 4: 테스트 통과를 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
pytest tests/test_schema.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: 커밋한다**

Run:

```powershell
git add notion_korea_stocks_template/stock_template/schema.py notion_korea_stocks_template/tests/test_schema.py
git commit -m "feat: define notion stock database schema"
```

Expected: 스키마 커밋이 생성된다.

---

### Task 3: 스팩 필터링, 시총 구간, 재무주의 규칙

**Files:**
- Create: `notion_korea_stocks_template/stock_template/rules.py`
- Create: `notion_korea_stocks_template/tests/test_rules.py`

- [ ] **Step 1: 실패하는 테스트를 작성한다**

Create `notion_korea_stocks_template/tests/test_rules.py`:

```python
from stock_template.rules import (
    bucket_market_cap,
    is_financial_warning,
    is_spac_name,
    normalize_number,
)


def test_is_spac_name_detects_korean_and_english_names():
    assert is_spac_name("테스트스팩1호")
    assert is_spac_name("미래에셋기업인수목적5호")
    assert is_spac_name("ABC SPAC")
    assert is_spac_name("Special Purpose Acquisition Company")


def test_is_spac_name_does_not_exclude_normal_stock():
    assert not is_spac_name("삼성전자")


def test_bucket_market_cap():
    assert bucket_market_cap(5_000_000_000_000) == "5조 이상"
    assert bucket_market_cap(1_000_000_000_000) == "1조-5조"
    assert bucket_market_cap(500_000_000_000) == "5천억-1조"
    assert bucket_market_cap(100_000_000_000) == "1천억-5천억"
    assert bucket_market_cap(99_999_999_999) == "1천억 미만"
    assert bucket_market_cap("") == "미분류"


def test_normalize_number_accepts_commas_and_empty_values():
    assert normalize_number("1,234") == 1234
    assert normalize_number("1234.56") == 1234.56
    assert normalize_number("") is None
    assert normalize_number(None) is None


def test_is_financial_warning():
    assert is_financial_warning(current_ratio=90, quick_ratio=120, capital_impairment=False)
    assert is_financial_warning(current_ratio=150, quick_ratio=80, capital_impairment=False)
    assert is_financial_warning(current_ratio=150, quick_ratio=120, capital_impairment=True)
    assert not is_financial_warning(current_ratio=150, quick_ratio=120, capital_impairment=False)
```

- [ ] **Step 2: 테스트가 실패하는지 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
pytest tests/test_rules.py -v
```

Expected: `ModuleNotFoundError` 또는 `ImportError`로 실패한다.

- [ ] **Step 3: 규칙 모듈을 구현한다**

Create `notion_korea_stocks_template/stock_template/rules.py`:

```python
SPAC_KEYWORDS = (
    "스팩",
    "기업인수목적",
    "SPAC",
    "Special Purpose Acquisition",
)


def is_spac_name(name: str) -> bool:
    text = str(name or "")
    upper_text = text.upper()
    return any(keyword.upper() in upper_text for keyword in SPAC_KEYWORDS)


def normalize_number(value):
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if text in {"", "-", "N/A", "nan", "None"}:
        return None
    number = float(text)
    if number.is_integer():
        return int(number)
    return number


def bucket_market_cap(value) -> str:
    amount = normalize_number(value)
    if amount is None:
        return "미분류"
    if amount >= 5_000_000_000_000:
        return "5조 이상"
    if amount >= 1_000_000_000_000:
        return "1조-5조"
    if amount >= 500_000_000_000:
        return "5천억-1조"
    if amount >= 100_000_000_000:
        return "1천억-5천억"
    return "1천억 미만"


def is_large_cap_5t(value) -> bool:
    amount = normalize_number(value)
    return bool(amount is not None and amount >= 5_000_000_000_000)


def ratio(numerator, denominator):
    top = normalize_number(numerator)
    bottom = normalize_number(denominator)
    if top is None or bottom in (None, 0):
        return ""
    return round(top / bottom * 100, 2)


def is_financial_warning(current_ratio, quick_ratio, capital_impairment) -> bool:
    current = normalize_number(current_ratio)
    quick = normalize_number(quick_ratio)
    return bool(
        capital_impairment
        or (current is not None and current <= 100)
        or (quick is not None and quick <= 100)
    )
```

- [ ] **Step 4: 테스트 통과를 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
pytest tests/test_rules.py -v
```

Expected: `5 passed`.

- [ ] **Step 5: 커밋한다**

Run:

```powershell
git add notion_korea_stocks_template/stock_template/rules.py notion_korea_stocks_template/tests/test_rules.py
git commit -m "feat: add stock filtering and risk rules"
```

Expected: 규칙 모듈 커밋이 생성된다.

---

### Task 4: CSV 입출력과 테마 병합

**Files:**
- Create: `notion_korea_stocks_template/stock_template/io.py`
- Create: `notion_korea_stocks_template/stock_template/themes.py`
- Create: `notion_korea_stocks_template/tests/test_transform.py`

- [ ] **Step 1: 변환 테스트의 첫 부분을 작성한다**

Create `notion_korea_stocks_template/tests/test_transform.py`:

```python
from stock_template.themes import load_theme_map


def test_load_theme_map_groups_multiple_themes(tmp_path):
    theme_csv = tmp_path / "theme_seed.csv"
    theme_csv.write_text(
        "종목코드,종목명,테마,테마근거,검수상태\n"
        "005930,삼성전자,반도체,근거,검수완료\n"
        "005930,삼성전자,AI,근거,검수완료\n",
        encoding="utf-8",
    )

    theme_map = load_theme_map(theme_csv)

    assert theme_map["005930"] == "AI, 반도체"
```

- [ ] **Step 2: 테스트가 실패하는지 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
pytest tests/test_transform.py::test_load_theme_map_groups_multiple_themes -v
```

Expected: `ModuleNotFoundError` 또는 `ImportError`로 실패한다.

- [ ] **Step 3: CSV IO 모듈을 구현한다**

Create `notion_korea_stocks_template/stock_template/io.py`:

```python
import csv
from pathlib import Path


def read_csv_rows(path):
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def write_csv_rows(path, rows, fieldnames):
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in fieldnames})
```

- [ ] **Step 4: 테마 로더를 구현한다**

Create `notion_korea_stocks_template/stock_template/themes.py`:

```python
from collections import defaultdict
from pathlib import Path

from stock_template.io import read_csv_rows


def load_theme_map(path):
    theme_path = Path(path)
    if not theme_path.exists():
        return {}

    grouped = defaultdict(set)
    for row in read_csv_rows(theme_path):
        code = str(row.get("종목코드", "")).zfill(6)
        theme = str(row.get("테마", "")).strip()
        if code and theme:
            grouped[code].add(theme)

    return {code: ", ".join(sorted(themes)) for code, themes in grouped.items()}
```

- [ ] **Step 5: 테스트 통과를 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
pytest tests/test_transform.py::test_load_theme_map_groups_multiple_themes -v
```

Expected: `1 passed`.

- [ ] **Step 6: 커밋한다**

Run:

```powershell
git add notion_korea_stocks_template/stock_template/io.py notion_korea_stocks_template/stock_template/themes.py notion_korea_stocks_template/tests/test_transform.py
git commit -m "feat: add csv and theme loading helpers"
```

Expected: CSV/테마 헬퍼 커밋이 생성된다.

---

### Task 5: master/update 행 변환

**Files:**
- Create: `notion_korea_stocks_template/stock_template/transform.py`
- Modify: `notion_korea_stocks_template/tests/test_transform.py`

- [ ] **Step 1: 변환 테스트를 추가한다**

Append to `notion_korea_stocks_template/tests/test_transform.py`:

```python
from stock_template.schema import CUSTOMER_MANAGED_COLUMNS, MASTER_COLUMNS, UPDATE_COLUMNS
from stock_template.transform import normalize_listing_row, to_master_row, to_update_row


def test_normalize_listing_row_accepts_aliases():
    row = normalize_listing_row(
        {
            "단축코드": "5930",
            "한글 종목명": "삼성전자",
            "시장구분": "KOSPI",
            "종가": "80,000",
            "market_cap": "477000000000000",
        }
    )

    assert row["종목코드"] == "005930"
    assert row["종목명"] == "삼성전자"
    assert row["시장"] == "KOSPI"
    assert row["현재가"] == 80000


def test_to_master_row_has_all_master_columns_and_theme():
    listing = normalize_listing_row(
        {
            "종목코드": "005930",
            "종목명": "삼성전자",
            "시장": "KOSPI",
            "업종": "반도체",
            "현재가": "80000",
            "시가총액": "477000000000000",
            "발행주식수": "5969782550",
            "DART코드": "00126380",
        }
    )

    row = to_master_row(listing, theme="반도체", data_date="2026-06-17")

    assert list(row.keys()) == MASTER_COLUMNS
    assert row["종목코드"] == "005930"
    assert row["테마"] == "반도체"
    assert row["시총구간"] == "5조 이상"
    assert row["시총 5조 이상"] == "true"
    assert row["투자아이디어"] == ""


def test_to_update_row_excludes_customer_columns():
    listing = normalize_listing_row(
        {
            "종목코드": "005930",
            "종목명": "삼성전자",
            "시장": "KOSPI",
            "시가총액": "477000000000000",
        }
    )

    row = to_update_row(listing, theme="반도체", data_date="2026-06-17")

    assert list(row.keys()) == UPDATE_COLUMNS
    for column in CUSTOMER_MANAGED_COLUMNS:
        assert column not in row
```

- [ ] **Step 2: 테스트가 실패하는지 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
pytest tests/test_transform.py -v
```

Expected: `ImportError` 또는 `AttributeError`로 실패한다.

- [ ] **Step 3: 변환 모듈을 구현한다**

Create `notion_korea_stocks_template/stock_template/transform.py`:

```python
from stock_template.rules import (
    bucket_market_cap,
    is_financial_warning,
    is_large_cap_5t,
    normalize_number,
    ratio,
)
from stock_template.schema import MASTER_COLUMNS, UPDATE_COLUMNS


ALIASES = {
    "종목코드": ["종목코드", "단축코드", "code", "ticker"],
    "종목명": ["종목명", "한글 종목명", "name", "company"],
    "시장": ["시장", "시장구분", "market"],
    "업종": ["업종", "업종명", "sector", "industry"],
    "현재가": ["현재가", "종가", "price", "close"],
    "시가총액": ["시가총액", "market_cap", "marcap"],
    "발행주식수": ["발행주식수", "shares", "listed_shares"],
    "DART코드": ["DART코드", "corp_code", "dart_code"],
    "자본총계": ["자본총계", "equity"],
    "부채총계": ["부채총계", "liabilities"],
    "유동자산": ["유동자산", "current_assets"],
    "유동부채": ["유동부채", "current_liabilities"],
    "재고자산": ["재고자산", "inventories"],
    "매출액 최근연도": ["매출액 최근연도", "revenue"],
    "영업이익 최근연도": ["영업이익 최근연도", "operating_income"],
    "당기순이익 최근연도": ["당기순이익 최근연도", "net_income"],
}

NUMBER_COLUMNS = {
    "현재가",
    "시가총액",
    "발행주식수",
    "자본총계",
    "부채총계",
    "유동자산",
    "유동부채",
    "재고자산",
    "매출액 최근연도",
    "영업이익 최근연도",
    "당기순이익 최근연도",
}

REQUIRED_COLUMNS = ["종목코드", "종목명", "시장"]


def first_value(row, aliases):
    for alias in aliases:
        value = row.get(alias)
        if value not in (None, ""):
            return value
    return ""


def normalize_listing_row(row):
    normalized = {}
    for target, aliases in ALIASES.items():
        value = first_value(row, aliases)
        if target == "종목코드":
            normalized[target] = str(value).strip().zfill(6)
        elif target in NUMBER_COLUMNS:
            normalized[target] = normalize_number(value)
        else:
            normalized[target] = str(value).strip()
    return normalized


def validate_required_columns(rows):
    missing = []
    if not rows:
        return REQUIRED_COLUMNS
    sample = rows[0]
    for target in REQUIRED_COLUMNS:
        if not any(alias in sample for alias in ALIASES[target]):
            missing.append(target)
    return missing


def base_provider_values(listing, theme, data_date):
    current_ratio = ratio(listing.get("유동자산"), listing.get("유동부채"))
    quick_ratio = ""
    if listing.get("유동자산") not in (None, "") and listing.get("재고자산") not in (None, ""):
        quick_assets = listing.get("유동자산") - listing.get("재고자산")
        quick_ratio = ratio(quick_assets, listing.get("유동부채"))

    capital_impairment = False
    debt_ratio = ratio(listing.get("부채총계"), listing.get("자본총계"))
    warning = is_financial_warning(current_ratio, quick_ratio, capital_impairment)
    market_cap = listing.get("시가총액")

    return {
        "종목명": listing.get("종목명", ""),
        "종목코드": listing.get("종목코드", ""),
        "시장": listing.get("시장", ""),
        "데이터 기준일": data_date,
        "상태": "정상",
        "업종": listing.get("업종", ""),
        "테마": theme or "미분류",
        "시가총액": market_cap or "",
        "시총구간": bucket_market_cap(market_cap),
        "시총 5조 이상": "true" if is_large_cap_5t(market_cap) else "false",
        "현재가": listing.get("현재가") or "",
        "발행주식수": listing.get("발행주식수") or "",
        "DART코드": listing.get("DART코드", ""),
        "자본총계": listing.get("자본총계") or "",
        "부채총계": listing.get("부채총계") or "",
        "유동자산": listing.get("유동자산") or "",
        "유동부채": listing.get("유동부채") or "",
        "재고자산": listing.get("재고자산") or "",
        "매출액 최근연도": listing.get("매출액 최근연도") or "",
        "영업이익 최근연도": listing.get("영업이익 최근연도") or "",
        "당기순이익 최근연도": listing.get("당기순이익 최근연도") or "",
        "부채비율": debt_ratio,
        "유동비율": current_ratio,
        "당좌비율": quick_ratio,
        "자본잠식 여부": "true" if capital_impairment else "false",
        "재무주의": "true" if warning else "false",
        "분석메모_공급자": "재무주의 조건 확인 필요" if warning else "",
    }


def to_master_row(listing, theme, data_date):
    values = base_provider_values(listing, theme, data_date)
    return {column: values.get(column, "") for column in MASTER_COLUMNS}


def to_update_row(listing, theme, data_date):
    values = base_provider_values(listing, theme, data_date)
    return {column: values.get(column, "") for column in UPDATE_COLUMNS}
```

- [ ] **Step 4: 테스트 통과를 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
pytest tests/test_transform.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: 커밋한다**

Run:

```powershell
git add notion_korea_stocks_template/stock_template/transform.py notion_korea_stocks_template/tests/test_transform.py
git commit -m "feat: transform listings into notion rows"
```

Expected: 변환 모듈 커밋이 생성된다.

---

### Task 6: master CSV 생성 CLI

**Files:**
- Create: `notion_korea_stocks_template/scripts/build_stocks_master.py`
- Modify: `notion_korea_stocks_template/README.md`

- [ ] **Step 1: master 생성 스크립트를 작성한다**

Create `notion_korea_stocks_template/scripts/build_stocks_master.py`:

```python
import argparse
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stock_template.io import read_csv_rows, write_csv_rows
from stock_template.rules import is_spac_name
from stock_template.schema import MASTER_COLUMNS
from stock_template.themes import load_theme_map
from stock_template.transform import normalize_listing_row, to_master_row, validate_required_columns


def build_master(listings_csv, theme_csv, output_csv, excluded_csv, data_date):
    source_rows = read_csv_rows(listings_csv)
    missing = validate_required_columns(source_rows)
    if missing:
        raise SystemExit(f"입력 CSV 필수 컬럼 누락: {', '.join(missing)}")

    theme_map = load_theme_map(theme_csv)
    master_rows = []
    excluded_rows = []

    for source_row in source_rows:
        listing = normalize_listing_row(source_row)
        if is_spac_name(listing["종목명"]):
            excluded_rows.append(
                {
                    "종목코드": listing["종목코드"],
                    "종목명": listing["종목명"],
                    "시장": listing["시장"],
                    "제외사유": "SPAC",
                    "데이터 기준일": data_date,
                }
            )
            continue
        theme = theme_map.get(listing["종목코드"], "미분류")
        master_rows.append(to_master_row(listing, theme, data_date))

    write_csv_rows(output_csv, master_rows, MASTER_COLUMNS)
    write_csv_rows(
        excluded_csv,
        excluded_rows,
        ["종목코드", "종목명", "시장", "제외사유", "데이터 기준일"],
    )
    return len(master_rows), len(excluded_rows)


def parse_args():
    parser = argparse.ArgumentParser(description="노션 한국 주식 master CSV 생성")
    parser.add_argument("--listings-csv", default=ROOT / "data" / "listings_sample.csv")
    parser.add_argument("--theme-csv", default=ROOT / "data" / "theme_seed.csv")
    parser.add_argument("--output-csv", default=ROOT / "output" / "stocks_master.csv")
    parser.add_argument("--excluded-csv", default=ROOT / "data" / "excluded_stocks.csv")
    parser.add_argument("--data-date", default=date.today().isoformat())
    return parser.parse_args()


def main():
    args = parse_args()
    included_count, excluded_count = build_master(
        Path(args.listings_csv),
        Path(args.theme_csv),
        Path(args.output_csv),
        Path(args.excluded_csv),
        args.data_date,
    )
    print(f"master CSV 생성 완료: 포함 {included_count}개, 제외 {excluded_count}개")
    print(f"출력 파일: {args.output_csv}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 스크립트를 실행한다**

Run:

```powershell
cd notion_korea_stocks_template
python scripts/build_stocks_master.py --data-date 2026-06-17
```

Expected:

```text
master CSV 생성 완료: 포함 4개, 제외 1개
출력 파일: output/stocks_master.csv
```

- [ ] **Step 3: 생성 파일을 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
python -c "import csv; rows=list(csv.DictReader(open('output/stocks_master.csv', encoding='utf-8-sig'))); print(len(rows)); print(rows[0]['종목코드'], rows[0]['테마'])"
python -c "import csv; rows=list(csv.DictReader(open('data/excluded_stocks.csv', encoding='utf-8-sig'))); print(len(rows)); print(rows[0]['종목명'], rows[0]['제외사유'])"
```

Expected:

```text
4
005930 반도체
1
테스트스팩1호 SPAC
```

- [ ] **Step 4: 전체 테스트를 실행한다**

Run:

```powershell
cd notion_korea_stocks_template
pytest -v
```

Expected: all tests pass.

- [ ] **Step 5: 커밋한다**

Run:

```powershell
git add notion_korea_stocks_template/scripts/build_stocks_master.py notion_korea_stocks_template/output/stocks_master.csv notion_korea_stocks_template/data/excluded_stocks.csv notion_korea_stocks_template/README.md
git commit -m "feat: generate notion master stock csv"
```

Expected: master 생성 커밋이 생성된다.

---

### Task 7: weekly update CSV와 변경 로그 생성

**Files:**
- Create: `notion_korea_stocks_template/stock_template/changelog.py`
- Create: `notion_korea_stocks_template/scripts/build_weekly_update.py`

- [ ] **Step 1: change log 모듈을 작성한다**

Create `notion_korea_stocks_template/stock_template/changelog.py`:

```python
from pathlib import Path


def write_change_log(path, data_date, update_rows):
    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# 주간 업데이트 변경 로그",
        "",
        f"- 데이터 기준일: {data_date}",
        f"- 업데이트 대상 종목 수: {len(update_rows)}",
        "",
        "## 포함 내용",
        "",
        "- 종목명",
        "- 시장",
        "- 업종",
        "- 테마",
        "- 시가총액",
        "- 시총구간",
        "- 현재가",
        "- 재무 요약 필드",
        "",
        "## 고객 데이터 보호",
        "",
        "이번 업데이트 파일에는 관심도, 보유여부, 매수일, 매도일, 투자아이디어, 리스크메모, 매매복기, 내 태그 같은 사용자 관리 필드가 포함되어 있지 않습니다.",
        "",
    ]

    log_path.write_text("\n".join(lines), encoding="utf-8")
```

- [ ] **Step 2: weekly update 스크립트를 작성한다**

Create `notion_korea_stocks_template/scripts/build_weekly_update.py`:

```python
import argparse
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stock_template.changelog import write_change_log
from stock_template.io import read_csv_rows, write_csv_rows
from stock_template.schema import UPDATE_COLUMNS


def build_weekly_update(master_csv, output_csv, change_log, data_date):
    master_rows = read_csv_rows(master_csv)
    update_rows = []
    for row in master_rows:
        update_row = {column: row.get(column, "") for column in UPDATE_COLUMNS}
        update_row["데이터 기준일"] = data_date
        update_rows.append(update_row)

    write_csv_rows(output_csv, update_rows, UPDATE_COLUMNS)
    write_change_log(change_log, data_date, update_rows)
    return len(update_rows)


def parse_args():
    parser = argparse.ArgumentParser(description="노션 한국 주식 weekly update CSV 생성")
    parser.add_argument("--master-csv", default=ROOT / "output" / "stocks_master.csv")
    parser.add_argument("--output-csv", default=ROOT / "output" / "stocks_update_weekly.csv")
    parser.add_argument("--change-log", default=ROOT / "output" / "change_log.md")
    parser.add_argument("--data-date", default=date.today().isoformat())
    return parser.parse_args()


def main():
    args = parse_args()
    count = build_weekly_update(
        Path(args.master_csv),
        Path(args.output_csv),
        Path(args.change_log),
        args.data_date,
    )
    print(f"weekly update CSV 생성 완료: {count}개")
    print(f"출력 파일: {args.output_csv}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: weekly update를 실행한다**

Run:

```powershell
cd notion_korea_stocks_template
python scripts/build_weekly_update.py --data-date 2026-06-17
```

Expected:

```text
weekly update CSV 생성 완료: 4개
출력 파일: output/stocks_update_weekly.csv
```

- [ ] **Step 4: update CSV가 사용자 필드를 제외하는지 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
python -c "import csv; header=next(csv.reader(open('output/stocks_update_weekly.csv', encoding='utf-8-sig'))); print('투자아이디어' in header); print(header[0])"
```

Expected:

```text
False
종목코드
```

- [ ] **Step 5: 커밋한다**

Run:

```powershell
git add notion_korea_stocks_template/stock_template/changelog.py notion_korea_stocks_template/scripts/build_weekly_update.py notion_korea_stocks_template/output/stocks_update_weekly.csv notion_korea_stocks_template/output/change_log.md
git commit -m "feat: generate weekly update csv"
```

Expected: weekly update 커밋이 생성된다.

---

### Task 8: 고객용 한국어 문서 생성

**Files:**
- Create: `notion_korea_stocks_template/docs/notion_database_schema.md`
- Create: `notion_korea_stocks_template/docs/notion_views.md`
- Create: `notion_korea_stocks_template/docs/update_strategy.md`
- Create: `notion_korea_stocks_template/docs/customer_setup_guide.md`

- [ ] **Step 1: 노션 스키마 문서를 작성한다**

Create `notion_korea_stocks_template/docs/notion_database_schema.md`:

```markdown
# 노션 데이터베이스 속성 가이드

이 문서는 `stocks_master.csv`를 노션으로 가져온 뒤 확인해야 할 속성 타입을 설명합니다.

## 기본 식별 필드

| 속성명 | 추천 타입 | 설명 |
| --- | --- | --- |
| 종목명 | Title | 회사명입니다. |
| 종목코드 | Text | 6자리 종목코드입니다. 앞자리 0이 사라지면 안 됩니다. |
| 시장 | Select | KOSPI 또는 KOSDAQ입니다. |
| 데이터 기준일 | Date | 데이터가 생성된 날짜입니다. |
| 상태 | Select | 정상, 신규상장, 상장폐지, 종목명변경, 검토필요 중 하나입니다. |

## 공급자 관리 필드

공급자 관리 필드는 업데이트 파일로 갱신될 수 있는 영역입니다. 고객이 직접 수정하기보다 필터와 참고용으로 쓰는 것을 권장합니다.

- 업종
- 테마
- 시가총액
- 시총구간
- 시총 5조 이상
- 현재가
- 발행주식수
- DART코드
- 자본총계
- 부채총계
- 유동자산
- 유동부채
- 재고자산
- 매출액 최근연도
- 영업이익 최근연도
- 당기순이익 최근연도
- 부채비율
- 유동비율
- 당좌비율
- 자본잠식 여부
- 재무주의
- 분석메모_공급자

## 사용자 관리 필드

사용자 관리 필드는 고객의 매매 기록 영역입니다. 주간 업데이트 파일에는 포함되지 않습니다.

- 관심도
- 보유여부
- 매수예정가
- 목표가
- 손절가
- 매수일
- 매도일
- 투자아이디어
- 리스크메모
- 매매복기
- 내 태그
```

- [ ] **Step 2: 추천 뷰 문서를 작성한다**

Create `notion_korea_stocks_template/docs/notion_views.md`:

```markdown
# 추천 노션 뷰

노션에서 아래 뷰를 만들어두면 버튼처럼 빠르게 종목을 볼 수 있습니다.

| 뷰 이름 | 필터/정렬 |
| --- | --- |
| 전체 종목 | 모든 종목, 시가총액 내림차순 |
| KOSPI | 시장 = KOSPI |
| KOSDAQ | 시장 = KOSDAQ |
| 시총 5조 이상 | 시총 5조 이상 = 체크 |
| 대형주 | 시총구간 = 5조 이상 또는 1조-5조 |
| 재무주의 | 재무주의 = 체크 |
| 테마별 보기 | 테마 기준 그룹화 |
| 내 관심종목 | 관심도 값이 비어 있지 않음 |
| 보유 종목 | 보유여부 = 체크 |
| 매매일지 | 매수일 또는 매도일이 비어 있지 않음 |

노션 버튼 기능은 템플릿 복제 환경에서 복잡한 필터를 자동으로 보장하기 어렵기 때문에, 1차 버전은 저장된 뷰를 권장합니다.
```

- [ ] **Step 3: 업데이트 전략 문서를 작성한다**

Create `notion_korea_stocks_template/docs/update_strategy.md`:

```markdown
# 업데이트 전략

이 템플릿은 고객의 매매 기록을 보호하기 위해 필드를 두 그룹으로 나눕니다.

- 공급자 관리 필드: 종목명, 시장, 업종, 테마, 시가총액, 재무정보처럼 업데이트 대상이 되는 정보
- 사용자 관리 필드: 관심도, 보유여부, 매수일, 매도일, 투자아이디어, 리스크메모, 매매복기처럼 고객이 직접 쓰는 정보

## 1차 업데이트 방식

1. 공급자가 `stocks_update_weekly.csv`를 제공합니다.
2. 고객은 이 파일을 별도 임시 노션 데이터베이스로 가져옵니다.
3. 변경된 종목명, 테마, 시가총액, 재무정보를 확인합니다.
4. 필요한 값만 기존 데이터베이스에 반영합니다.

## 중요한 제한

노션의 CSV import만으로는 기존 데이터베이스에 안전한 병합 업데이트를 자동 수행하기 어렵습니다. 그래서 1차 버전은 업데이트 파일과 변경 로그를 제공하고, 자동 병합은 추후 Notion API 버전에서 지원합니다.

## 추후 자동 업데이트 원칙

- 종목코드로 기존 행을 찾습니다.
- 공급자 관리 필드만 수정합니다.
- 사용자 관리 필드는 수정하지 않습니다.
- 상장폐지 종목은 삭제하지 않고 상태만 바꿉니다.
```

- [ ] **Step 4: 고객 설치 가이드를 작성한다**

Create `notion_korea_stocks_template/docs/customer_setup_guide.md`:

```markdown
# 고객 설치 가이드

## 처음 설치

1. 노션에서 새 페이지를 만듭니다.
2. `stocks_master.csv`를 페이지로 끌어다 놓거나 Import 기능으로 가져옵니다.
3. 데이터베이스가 생성되면 `종목코드`가 6자리 텍스트로 유지되는지 확인합니다.
4. `notion_database_schema.md`를 보고 속성 타입을 확인합니다.
5. `notion_views.md`를 보고 추천 뷰를 만듭니다.

## 사용 방법

- 관심 있는 종목은 `관심도`를 입력합니다.
- 보유 중인 종목은 `보유여부`를 체크합니다.
- 매수/매도 계획은 `매수예정가`, `목표가`, `손절가`에 기록합니다.
- 투자 판단은 `투자아이디어`, `리스크메모`, `매매복기`에 기록합니다.

## 업데이트 받을 때

주간 업데이트 파일은 고객의 매매 기록 필드를 포함하지 않습니다. 업데이트 파일을 기존 데이터베이스에 바로 덮어쓰기보다, 별도 임시 데이터베이스로 가져온 뒤 변경 내용을 확인하는 방식을 권장합니다.
```

- [ ] **Step 5: 커밋한다**

Run:

```powershell
git add notion_korea_stocks_template/docs
git commit -m "docs: add Korean Notion customer guides"
```

Expected: 고객 문서 커밋이 생성된다.

---

### Task 9: 최종 검증

**Files:**
- Modify only if verification exposes a defect in files created above.

- [ ] **Step 1: 전체 테스트를 실행한다**

Run:

```powershell
cd notion_korea_stocks_template
pytest -v
```

Expected: all tests pass.

- [ ] **Step 2: 샘플 master와 update를 재생성한다**

Run:

```powershell
cd notion_korea_stocks_template
python scripts/build_stocks_master.py --data-date 2026-06-17
python scripts/build_weekly_update.py --data-date 2026-06-17
```

Expected:

```text
master CSV 생성 완료: 포함 4개, 제외 1개
weekly update CSV 생성 완료: 4개
```

- [ ] **Step 3: CSV 헤더와 스팩 제외를 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
python -c "import csv; master=list(csv.DictReader(open('output/stocks_master.csv', encoding='utf-8-sig'))); update_header=next(csv.reader(open('output/stocks_update_weekly.csv', encoding='utf-8-sig'))); excluded=list(csv.DictReader(open('data/excluded_stocks.csv', encoding='utf-8-sig'))); print(len(master), len(excluded)); print('투자아이디어' in master[0], '투자아이디어' in update_header); print(excluded[0]['제외사유'])"
```

Expected:

```text
4 1
True False
SPAC
```

- [ ] **Step 4: 문서가 한국어 중심인지 확인한다**

Run:

```powershell
cd notion_korea_stocks_template
$patterns = @("TB" + "D", "TO" + "DO", "place" + "holder")
Select-String -Path docs\*.md README.md -Pattern $patterns
```

Expected: no matches.

- [ ] **Step 5: 변경 파일을 검토한다**

Run:

```powershell
git status --short
git diff --stat
```

Expected: 이번 프로젝트 파일만 변경되어 있다. 기존 작업 트리에 있던 unrelated 변경은 건드리지 않는다.

- [ ] **Step 6: 최종 커밋이 필요하면 생성한다**

Run:

```powershell
git add notion_korea_stocks_template
git commit -m "test: verify korea stocks notion template outputs"
```

Expected: 검증 결과 또는 누락 수정 커밋이 생성된다. 커밋할 변경이 없으면 이 단계는 건너뛴다.

---

## 계획 자기검토 결과

- 스펙의 핵심 요구사항인 한국어 MD 문서, master CSV, weekly update CSV, 스팩 제외, 사용자 필드 보호, 테마 seed, 추천 뷰 문서가 모두 작업에 포함되어 있다.
- 1차 버전은 수동 KRX CSV 입력 방식으로 고정했다. 이는 네트워크 없이도 작동하며, 실제 전 종목 데이터는 `--listings-csv`에 전체 KOSPI/KOSDAQ 입력 CSV를 넣으면 생성된다.
- Notion API 자동 병합은 2차 버전으로 문서화만 한다. 1차 구현 범위에는 포함하지 않는다.
- 테스트는 스팩 필터링, 시총 구간, 필드 소유권, 변환 결과, update CSV의 사용자 필드 제외를 검증한다.
- 모든 고객용 MD 문서는 한국어 중심으로 작성한다.
