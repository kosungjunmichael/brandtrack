# Luxury Fashion Bag Trends Dashboard

Real-time market intelligence for luxury handbag searches. Track search interest, market prices, and visual trends for vintage luxury bags.

## Features

- **KPI Metrics**: Total searches, daily averages, top brands, fastest growing
- **Brand Power Shift**: Search volume trends by luxury brand over time
- **Trending Combinations**: Top keyword combinations (brand × texture, color × style)
- **Color & Texture Trends**: Popular colors and materials
- **Style Distribution**: Market share by bag style (shoulder, tote, crossbody, etc.)
- **Quick Insights**: AI-generated trend analysis

## Tech Stack

- **Frontend**: Streamlit
- **Data Storage**: Google Sheets API
- **Data Sources**: Google Trends (PyTrends), eBay sold listings, Pinterest
- **Automation**: GitHub Actions (daily cron at 03:00 UTC)

## Project Structure

```
brandtrack/
├── app.py                 # Main Streamlit dashboard
├── scripts/
│   ├── scraper_engine.py  # Data collection (PyTrends, eBay, Pinterest)
│   └── gsheets_sync.py    # Google Sheets read/write module
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── secrets.toml       # Google Sheets credentials (not in repo)
└── .github/
    └── workflows/
        └── daily_scrape.yml  # Daily automation
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Google Sheets

Create `.streamlit/secrets.toml` with your service account credentials:

```toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID"
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

### 3. Run the Dashboard

```bash
streamlit run app.py
```

### 4. Run Scrapers Manually

```bash
python scripts/scraper_engine.py
```

## Deployment

### Streamlit Cloud

1. Connect your GitHub repository to [Streamlit Cloud](https://streamlit.io/cloud)
2. Set main file path to `app.py`
3. Add secrets in Streamlit Cloud settings (copy from `secrets.toml`)

### GitHub Actions

Add these secrets to your repository for automated daily scraping:

- `GSHEETS_SPREADSHEET`
- `GSHEETS_TYPE`
- `GSHEETS_PROJECT_ID`
- `GSHEETS_PRIVATE_KEY_ID`
- `GSHEETS_PRIVATE_KEY`
- `GSHEETS_CLIENT_EMAIL`
- `GSHEETS_CLIENT_ID`
- `GSHEETS_AUTH_URI`
- `GSHEETS_TOKEN_URI`
- `GSHEETS_AUTH_PROVIDER_CERT_URL`
- `GSHEETS_CLIENT_CERT_URL`

## Brands Tracked

- Hermès
- Chanel
- Louis Vuitton
- Gucci
- Prada
- Bottega Veneta

## License

Private project.
