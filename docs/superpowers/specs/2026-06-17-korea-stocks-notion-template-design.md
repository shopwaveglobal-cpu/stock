# Korea Stocks Notion Template Design

## Goal

Build a sellable Notion stock-trading journal template for all non-SPAC KOSPI and KOSDAQ stocks, delivered first as CSV import files plus setup documentation. The first release supports a one-time purchase product. The data pipeline and database structure must also support a later subscription product that provides weekly updates without overwriting customer-written trading journal fields.

## Product Model

### One-Time Product

The one-time product gives customers a complete Notion-ready stock master database containing current KOSPI and KOSDAQ listings, excluding SPACs. Customers can import the CSV into Notion and use it as a trading journal, watchlist, and stock research base.

Included deliverables:

- `stocks_master.csv`: initial Notion import file.
- `notion_database_schema.md`: property setup guide for Notion.
- `notion_views.md`: recommended filters, sorts, and button-like saved views.
- `customer_setup_guide.md`: plain-language import and usage instructions.

### Subscription Product

The subscription product provides weekly update files for changed stock names, market metadata, market cap buckets, financial summary fields, and theme classifications. It does not include customer-owned trading journal fields.

Included deliverables:

- `stocks_update_weekly.csv`: rows keyed by stock code, containing only provider-managed fields.
- `change_log.md`: readable summary of changed company names, newly listed stocks, removed stocks, theme changes, and financial data refreshes.
- Later optional automation: a Notion API updater that merges provider-managed fields by stock code.

## Core Design Choice

Use `종목코드` as the stable unique key. Human-readable names can change, but stock codes are stable enough for the update workflow and are the best available merge key for a Notion/CSV product.

Separate columns into two ownership groups:

- Provider-managed fields: fields updated by the template seller.
- Customer-managed fields: fields filled in by the customer and never included in weekly update CSV files.

This separation is the main protection against accidentally overwriting customer notes, trade history, tags, and decisions.

## Data Sources

The first implementation should use source adapters so data providers can be swapped later.

Initial adapters:

- KRX listing source: KOSPI/KOSDAQ stock list, market, stock code, company name, listing status, market cap when available.
- DART source: corporate code mapping and financial statement fields for listed companies.
- Optional price source: current price and market cap support if KRX output does not provide a usable value.
- Theme source: manually maintained seed file for themes in version 1.

The old attached script is treated as reference only. Its useful ideas are:

- DART corporate code mapping.
- Annual financial account extraction.
- Static financial ratios.
- Excel/CSV generation pipeline.

The new project should not copy its broken encoding, hard-coded local paths, or API key.

## Exclusions

SPACs should be excluded from the customer-facing master CSV by default.

Version 1 SPAC detection:

- Exclude rows whose name contains `스팩`, `기업인수목적`, `SPAC`, or `Special Purpose Acquisition`.
- Keep an internal `excluded_stocks.csv` audit file so the seller can review what was removed.

Future versions may add ETF, ETN, REIT, preferred share, and KONEX controls, but version 1 only commits to excluding SPACs from KOSPI/KOSDAQ stocks.

## Notion Database Schema

### Identity Fields

- `종목명`: title property.
- `종목코드`: text property, six-digit zero-padded code.
- `시장`: select, values `KOSPI` and `KOSDAQ`.
- `데이터 기준일`: date.
- `상태`: select, values `정상`, `신규상장`, `상장폐지`, `종목명변경`, `검토필요`.

### Provider-Managed Fields

- `업종`: select or text.
- `테마`: multi-select.
- `시가총액`: number.
- `시총구간`: select, values `5조 이상`, `1조-5조`, `5천억-1조`, `1천억-5천억`, `1천억 미만`, `미분류`.
- `시총 5조 이상`: checkbox.
- `현재가`: number.
- `발행주식수`: number.
- `DART코드`: text.
- `자본총계`: number.
- `부채총계`: number.
- `유동자산`: number.
- `유동부채`: number.
- `재고자산`: number.
- `매출액 최근연도`: number.
- `영업이익 최근연도`: number.
- `당기순이익 최근연도`: number.
- `부채비율`: number.
- `유동비율`: number.
- `당좌비율`: number.
- `자본잠식 여부`: checkbox.
- `재무주의`: checkbox.
- `분석메모_공급자`: text.

### Customer-Managed Fields

- `관심도`: select.
- `보유여부`: checkbox.
- `매수예정가`: number.
- `목표가`: number.
- `손절가`: number.
- `매수일`: date.
- `매도일`: date.
- `투자아이디어`: text.
- `리스크메모`: text.
- `매매복기`: text.
- `내 태그`: multi-select.

Weekly update CSV files must never include customer-managed fields.

## Notion Views

Notion buttons have limited support for complex database filtering across duplicated customer templates, so version 1 should use named views that act like button presets.

Recommended views:

- `전체 종목`: all rows, sorted by market cap descending.
- `KOSPI`: market equals KOSPI.
- `KOSDAQ`: market equals KOSDAQ.
- `시총 5조 이상`: `시총 5조 이상` checked.
- `대형주`: `시총구간` equals `5조 이상` or `1조-5조`.
- `재무주의`: `재무주의` checked.
- `테마별 보기`: grouped by `테마`.
- `내 관심종목`: `관심도` is not empty.
- `보유 종목`: `보유여부` checked.
- `매매일지`: rows where `매수일` or `매도일` is not empty.

Future versions can add a Notion API setup script that creates the database and views automatically.

## Theme Classification

Version 1 should start with a manually editable theme seed file:

`data/theme_seed.csv`

Columns:

- `종목코드`
- `종목명`
- `테마`
- `테마근거`
- `검수상태`

The generated master CSV maps `테마` into a Notion multi-select compatible comma-separated value. Example: Samsung Electronics can have `반도체`.

The first release may ship with a partial theme map as long as the documentation clearly labels unclassified rows as `미분류`. A later subscription value proposition is continuous theme curation.

## Update Strategy

Version 1 weekly updates are delivered as CSV plus instructions:

1. Customers keep their original trading journal database.
2. The seller provides `stocks_update_weekly.csv`.
3. Customers import the update CSV into a separate temporary Notion database.
4. Customers manually review changed fields and newly listed rows.
5. The seller may provide a guided copy/paste workflow for changed rows only.

This is not the final best experience, but it avoids promising more than Notion CSV import can reliably do.

Version 2 should add a Notion API updater:

- Customer shares their database with the integration.
- Updater reads rows by `종목코드`.
- Updater changes provider-managed properties only.
- Updater skips customer-managed properties.
- Updater adds newly listed stocks.
- Updater marks delisted stocks as `상장폐지` instead of deleting them.

Deletion should never be the default behavior because customers may have trade notes attached to old rows.

## Generated File Structure

Create a new project folder:

```text
notion_korea_stocks_template/
  README.md
  data/
    theme_seed.csv
    excluded_stocks.csv
  output/
    stocks_master.csv
    stocks_update_weekly.csv
    change_log.md
  scripts/
    build_stocks_master.py
    build_weekly_update.py
  docs/
    notion_database_schema.md
    notion_views.md
    update_strategy.md
    customer_setup_guide.md
```

## Implementation Principles

- Keep data-source code separate from transformation code.
- Do not hard-code API keys or local absolute paths.
- Generate deterministic CSV column order for Notion imports.
- Use UTF-8 with BOM for CSV files so Korean text opens cleanly in Excel.
- Treat network collection failures as recoverable row-level errors.
- Produce an audit file for excluded SPACs and rows with missing critical data.
- Prefer a small first version that can be sold and updated over a large unfinished automation system.

## Validation

The first implementation is successful when:

- A sample run generates `stocks_master.csv` with the agreed schema.
- SPAC-like names are excluded and listed in `excluded_stocks.csv`.
- Customer-managed fields exist in the master CSV but are absent from the weekly update CSV.
- The generated docs explain Notion import, views, and update limitations honestly.
- Tests verify SPAC filtering, market cap bucketing, column ownership separation, and CSV column order.

