# Project: Vintage Bag Trend & Price Dashboard

## 📌 Context
A lightweight, automated monitoring system for vintage luxury bags. It tracks search interest (Hype), planning trends (Aspiration), and actual market sales (Reality).

## 🛠 Tech Stack
- **Frontend:** Streamlit (Deployed on Streamlit Cloud)
- **Automation:** GitHub Actions (Daily Cron Job)
- **Database:** Google Sheets API (via `gspread` or `st.connection("gsheets")`)
- **Languages:** Python 3.11+
- **Key Libraries:** `pytrends`, `playwright` (Pinterest), `beautifulsoup4` (eBay)

## 📊 Data Pipeline
1. **Google Trends (via PyTrends):** - Tracks keyword interest for specific models.
   - *Constraint:* Batch keywords in groups of 5 to avoid 429 rate limits.
2. **Pinterest Trends:** - Scrapes visual trend data using Playwright.
   - *Constraint:* Use randomized delays to avoid bot detection.
3. **eBay Market Data:** - Scrapes "Sold" listings for historical price averages.
   - *Logic:* Filter for `LH_Sold=1` in URL.

## 📁 Project Structure
- `app.py`: Streamlit frontend and visualization logic.
- `scraper_engine.py`: Main script for PyTrends, eBay, and Pinterest data collection.
- `gsheets_sync.py`: Logic to append/read data from Google Sheets.
- `.github/workflows/daily_scrape.yml`: Cron job configuration (runs 03:00 UTC).
- `requirements.txt`: Project dependencies.

## 📜 Coding Rules & Patterns
- **Polite Scraping:** Always implement `time.sleep(random.randint(5, 15))` between requests.
- **Statelessness:** The dashboard must read from Google Sheets, NOT local CSVs (Streamlit Cloud resets local files).
- **Error Handling:** If a scraper fails (e.g., PyTrends empty dataframe), log the error to the Sheet and continue.
- **Security:** API keys and Service Account JSONs MUST be read from `st.secrets` or GitHub Secrets.

## 🚀 Commands
- Run Dashboard: `streamlit run app.py`
- Test Scrapers: `python scraper_engine.py`
- Install Deps: `pip install -r requirements.txt`