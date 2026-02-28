# gsheets_sync.py

Google Sheets synchronization module for the Vintage Bag Trend Dashboard. Handles authentication, reading/writing data to Google Sheets, and managing the local keywords cache.

---

## Authentication

The module supports two authentication modes depending on context:

- **Inside the Streamlit app** — credentials are read from `.streamlit/secrets.toml` via `st.secrets`
- **Standalone (CLI)** — falls back to `credentials.json` (service account key file) in the project root

The `_is_streamlit()` helper detects which context is active and `get_gspread_client()` branches accordingly.

---

## Keywords Workflow

Keywords live in the `keywords` sheet of the Brandtrack Google Spreadsheet. They are the source of truth for what the scraper searches for.

### Sheet layout

| Column | Key | Description |
|--------|-----|-------------|
| A | `textures` | Material/texture keywords (e.g. "Suede bag") |
| B | `colors` | Color keywords (e.g. "Burgundy bag") |
| C | `styles` | Style/trend keywords (e.g. "Hobo bag") |
| D | `brands` | Standard luxury brand keywords (e.g. "Gucci") |
| E | `vintage_brands` | Vintage brand keywords (e.g. "Vintage Gucci") |

Row 1 is the header row and is skipped during sync.

### Updating keywords

1. Edit the `keywords` sheet in the Brandtrack Google Spreadsheet
2. Run the sync script to pull changes into the local cache:

```bash
python gsheets_sync.py
```

This writes `keywords.json` to the project root. The scraper reads from this file at runtime.

`keywords.json` is gitignored — it is a generated local cache, not source-controlled.

---

## Sheet Constants

| Constant | Sheet name | Purpose |
|---|---|---|
| `SHEET_KEYWORDS` | `keywords` | Scraper keyword lists |
| `SHEET_BRAND_TRENDS` | `brand_trends` | Google Trends data for standard brands |
| `SHEET_VINTAGE_BRAND_TRENDS` | `vintage_brand_trends` | Google Trends data for vintage brands |
| `SHEET_COLOR_TRENDS` | `color_trends` | Google Trends data for colors |
| `SHEET_STYLE_TRENDS` | `style_trends` | Google Trends data for styles |
| `SHEET_TEXTURE_TRENDS` | `texture_trends` | Google Trends data for textures/materials |
| `SHEET_PRICES` | `price_data` | eBay sold listing prices |
| `SHEET_PINTEREST` | `pinterest_data` | Pinterest trend data |
| `SHEET_ERRORS` | `error_log` | Runtime error log |

---

## Key Functions

### `get_keywords()`
Reads all keyword columns directly from the Google Sheet and returns a dict with keys `textures`, `colors`, `styles`, `brands`, `vintage_brands`.

### `sync_keywords_to_json()`
Calls `get_keywords()` and writes the result to `keywords.json`. Also stamps a `synced_at` timestamp. Called automatically when running the script directly.

### `load_keywords_from_json()`
Reads `keywords.json` from disk. Returns `None` if the file doesn't exist. Used by the scraper at runtime to avoid hitting the API on every run.

### `append_dataframe(sheet_name, df)`
Batch-appends a pandas DataFrame to a sheet. Handles datetime serialization and NaN values. Uses `append_rows()` for speed rather than row-by-row writes.

### `clear_and_write(sheet_name, df)`
Clears a sheet completely and writes fresh data. Used when replacing old scrape results.

### `clear_sheet(sheet_name)`
Clears all data from a sheet. Silently succeeds if the sheet doesn't exist.

### `log_error(error_message)`
Appends a timestamped error entry to the `error_log` sheet. Called internally by other functions on failure.

---

## Running Standalone

```bash
python gsheets_sync.py
```

Requires `credentials.json` (service account key) in the project root. Output example:

```
Syncing keywords from Google Sheets...
Keywords synced to /path/to/keywords.json
  - Textures: 9
  - Colors: 14
  - Styles: 13
  - Brands: 20
  - Vintage brands: 20
```
