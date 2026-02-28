# scraper_engine.py

Scraper engine for the Vintage Bag Trend Dashboard. Collects search interest data from Google Trends, sold listing prices from eBay, and trend signals from Pinterest, then writes results to Google Sheets.

---

## Running the Scraper

```bash
python scraper_engine.py
```

Before running, make sure `keywords.json` is up to date:

```bash
python gsheets_sync.py   # pull latest keywords from Google Sheets
python scraper_engine.py # run the scraper
```

---

## Keywords

Keywords are loaded from `keywords.json` (local cache synced from Google Sheets). If the file is missing, the scraper falls back to hardcoded defaults for each category.

| Key | Description |
|---|---|
| `brands` | Standard luxury brand names |
| `vintage_brands` | Vintage-prefixed brand names |
| `colors` | Color keywords |
| `styles` | Style/silhouette keywords |
| `textures` | Material/texture keywords |

To update keywords, edit the `keywords` sheet in the Brandtrack Google Spreadsheet and run `python gsheets_sync.py`. See `docs/gsheets_sync.md` for details.

---

## Scrapers

### GoogleTrendsScraper

Uses the `pytrends` library to fetch search interest from Google Trends. Keywords are sent in batches of 5 (Google Trends API limit). A random 5–15 second delay is added between batches to avoid rate limiting.

Data is returned in long format with columns: `date`, `keyword`, `interest`.

#### Time period

All keyword categories use the same timeframe: **`today 3-m`** (the past 3 months, ~90 days from the current date). Google Trends returns one data point per day for this timeframe. The interest value is a relative score from 0–100, where 100 is the peak search interest for that keyword within the period.

| Method | Keywords used | Sheet written to | Timeframe |
| --- | --- | --- | --- |
| `fetch_all_brand_trends()` | `brands` | `brand_trends` | Last 90 days |
| `fetch_vintage_brand_trends()` | `vintage_brands` | `vintage_brand_trends` | Last 90 days |
| `fetch_color_trends()` | `colors` | `color_trends` | Last 90 days |
| `fetch_style_trends()` | `styles` | `style_trends` | Last 90 days |
| `fetch_texture_trends()` | `textures` | `texture_trends` | Last 90 days |

Each scrape run clears the corresponding sheet before writing fresh data — results are replaced, not appended.

### EbayScraper _(temporarily disabled)_

Scrapes sold/completed listings from eBay for each brand keyword. Prepends "vintage" to queries that don't already include it. Returns up to 20 listings per query with fields: `query`, `title`, `price`, `date_scraped`.

Price ranges are averaged. Results are written to the `price_data` sheet.

### PinterestScraper _(temporarily disabled)_

Uses Playwright (headless Chromium) to load Pinterest search results pages and detect whether pins exist for a given search term. Results are written to the `pinterest_data` sheet.

Requires Playwright to be installed: `playwright install chromium`

---

## run_all_scrapers()

The main entry point. Runs all active scrapers in sequence:

1. Load keywords from `keywords.json`
2. Clear old trends sheets
3. Fetch and save Google Trends for: brands, vintage brands, colors, styles, textures
4. _(eBay and Pinterest are currently disabled)_

---

## Rate Limiting

`polite_delay()` sleeps for a random 5–15 seconds between each batch request. This applies to both Google Trends and eBay scrapers. Do not remove this — Google Trends will block requests if called too rapidly.

---

## Error Handling

All scraper errors are caught and logged to the `error_log` sheet in Google Sheets via `gs.log_error()`. Failed batches return empty DataFrames and are skipped rather than halting the full run.
