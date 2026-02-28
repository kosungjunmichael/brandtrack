# app.py

The main Streamlit dashboard for the Luxury Fashion Bag Trends project. Displays market intelligence for luxury handbag search trends including brand performance, colors, textures, and styles.

---

## Running the App

```bash
streamlit run app.py
```

The app will open in the browser at `http://localhost:8501`.

---

## Data

The app pulls data from two sources via `gsheets_sync`:

| Function | Sheet | Cache TTL |
| --- | --- | --- |
| `gs.get_trends_data(days=90)` | `trends_data` | 5 minutes |
| `gs.get_price_data()` | `price_data` | 5 minutes |

Both are wrapped in `@st.cache_data(ttl=300)` so the Google Sheets API is only called once every 5 minutes. Clicking the **Refresh** button in the UI clears the cache and forces an immediate reload.

### Sample data fallback

If no real data is available from Google Sheets, `generate_sample_data()` produces synthetic data for demonstration purposes. This covers brand trends (180 days of simulated interest scores), colors, textures, and style distributions. The sample data is currently used by most charts — real data integration is in progress.

---

## Layout

### Header
- Dashboard title and subtitle
- **Time Period** selector — Last 30 / 60 / 90 Days (filters the brand trends chart)
- Last updated timestamp and **Refresh** button

### KPI Metrics Row
Four stat cards showing (currently hardcoded placeholder values):
- Total Searches
- Avg. Daily Searches
- Top Brand
- Fastest Growing

### Brand Power Shift _(line chart)_
Search interest over time for 6 luxury brands, filtered by the selected time period. Uses sample data. Each brand has a fixed colour:

| Brand | Colour |
| --- | --- |
| Hermès | Orange |
| Chanel | Black |
| Louis Vuitton | Brown |
| Gucci | Green |
| Prada | Blue |
| Bottega Veneta | Light green |

### Trending Search Combinations _(list)_
Top 5 keyword combinations ranked by search volume. Shows the combination name, search count, category type (e.g. Brand × Texture), and week-over-week change. Currently hardcoded.

### Color Trends _(horizontal bar chart)_
Top searched bag colors ranked by search volume. Each bar is coloured to match the actual colour it represents. Uses sample data.

### Texture & Material Trends _(horizontal bar chart)_
Top searched textures and materials ranked by search volume. Uses sample data.

### Style & Shape Distribution _(pie chart)_
Market share breakdown by bag style (Shoulder, Tote, Crossbody, etc.). Uses sample data.

### Quick Insights _(cards)_
Five manually written insight cards highlighting notable trends, each with a colour-coded left border. Currently hardcoded.

---

## Styling

Custom CSS is loaded from `styles.css` at startup via `load_css()`. CSS classes used throughout the app:

| Class | Used for |
| --- | --- |
| `.main-header` | Page title |
| `.sub-header` | Page subtitle |
| `.section-title` | Section headings |
| `.section-subtitle` | Section subheadings |
| `.insight-card` | Quick Insights cards |
| `.insight-title` | Card heading |
| `.insight-text` | Card body text |
