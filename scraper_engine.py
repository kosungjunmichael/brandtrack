"""
Scraper engine for the Vintage Bag Trend Dashboard.
Collects data from Google Trends, Pinterest, and eBay.
"""

import time
import random
import pandas as pd
from datetime import datetime
from pytrends.request import TrendReq
from bs4 import BeautifulSoup
import requests

# Import gsheets_sync for data persistence
try:
    import gsheets_sync as gs
except ImportError:
    gs = None


# Default fallback keywords (used if Google Sheets is unavailable)
DEFAULT_BRANDS = ["Hermès bag", "Chanel bag", "Louis Vuitton bag", "Gucci bag", "Prada bag", "Bottega Veneta bag"]
DEFAULT_VINTAGE_BRANDS = ["Vintage Gucci", "Vintage Prada", "Vintage Chanel", "Vintage Louis Vuitton", "Vintage Fendi"]
DEFAULT_STYLES = ["shoulder bag", "tote bag", "crossbody bag", "clutch bag", "bucket bag", "satchel bag"]
DEFAULT_COLORS = ["black bag", "brown bag", "beige bag", "white bag", "green bag", "red bag", "blue bag", "pink bag"]
DEFAULT_TEXTURES = ["leather bag", "quilted bag", "canvas bag", "suede bag", "patent leather bag", "woven bag"]


def load_keywords():
    """
    Load keywords from local JSON file (keywords.json).
    Falls back to defaults if file doesn't exist.

    To update keywords.json, run: python gsheets_sync.py
    """
    if gs:
        try:
            keywords = gs.load_keywords_from_json()
            if keywords:
                synced_at = keywords.get('synced_at', 'unknown')
                print(f"  Loaded keywords from local cache (synced: {synced_at})")
                return {
                    'brands': keywords['brands'] if keywords['brands'] else DEFAULT_BRANDS,
                    'vintage_brands': keywords.get('vintage_brands') or DEFAULT_VINTAGE_BRANDS,
                    'styles': keywords['styles'] if keywords['styles'] else DEFAULT_STYLES,
                    'colors': keywords['colors'] if keywords['colors'] else DEFAULT_COLORS,
                    'textures': keywords['textures'] if keywords['textures'] else DEFAULT_TEXTURES,
                }
            else:
                print("  No local keywords.json found, using defaults")
                print("  Tip: Run 'python gsheets_sync.py' to sync keywords from Google Sheets")
        except Exception as e:
            print(f"Warning: Could not load keywords: {e}")

    return {
        'brands': DEFAULT_BRANDS,
        'vintage_brands': DEFAULT_VINTAGE_BRANDS,
        'styles': DEFAULT_STYLES,
        'colors': DEFAULT_COLORS,
        'textures': DEFAULT_TEXTURES,
    }


def polite_delay():
    """Random delay to avoid rate limiting."""
    time.sleep(random.randint(5, 15))


def batch_keywords(keywords, batch_size=5):
    """Split keywords into batches of specified size."""
    for i in range(0, len(keywords), batch_size):
        yield keywords[i:i + batch_size]


class GoogleTrendsScraper:
    """Scraper for Google Trends data using PyTrends."""

    def __init__(self, keywords=None):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.keywords = keywords or load_keywords()

    def fetch_interest_over_time(self, keywords, timeframe='today 3-m'):
        """Fetch interest over time for a batch of keywords."""
        try:
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo='', gprop='')
            data = self.pytrends.interest_over_time()

            if data.empty:
                return pd.DataFrame()

            # Remove isPartial column if present
            if 'isPartial' in data.columns:
                data = data.drop(columns=['isPartial'])

            # Convert from wide to long format for better storage
            data = data.reset_index()
            data = data.melt(id_vars=['date'], var_name='keyword', value_name='interest')

            return data
        except Exception as e:
            print(f"Error fetching trends for {keywords}: {e}")
            if gs:
                gs.log_error(f"PyTrends error for {keywords}: {str(e)}")
            return pd.DataFrame()

    def fetch_all_brand_trends(self):
        """Fetch trends for all luxury brands."""
        all_data = []
        brands = self.keywords['brands']

        if not brands:
            print("  No brand keywords found, skipping...")
            return pd.DataFrame()

        for batch in batch_keywords(brands, 5):
            print(f"Fetching trends for: {batch}")
            data = self.fetch_interest_over_time(batch)
            if not data.empty:
                all_data.append(data)
            polite_delay()

        if all_data:
            return pd.concat(all_data, axis=0).drop_duplicates()
        return pd.DataFrame()

    def fetch_color_trends(self):
        """Fetch trends for bag colors."""
        all_data = []
        colors = self.keywords['colors']

        if not colors:
            print("  No color keywords found, skipping...")
            return pd.DataFrame()

        for batch in batch_keywords(colors, 5):
            print(f"Fetching color trends for: {batch}")
            data = self.fetch_interest_over_time(batch)
            if not data.empty:
                all_data.append(data)
            polite_delay()

        if all_data:
            return pd.concat(all_data, axis=0).drop_duplicates()
        return pd.DataFrame()

    def fetch_style_trends(self):
        """Fetch trends for bag styles."""
        all_data = []
        styles = self.keywords['styles']

        if not styles:
            print("  No style keywords found, skipping...")
            return pd.DataFrame()

        for batch in batch_keywords(styles, 5):
            print(f"Fetching style trends for: {batch}")
            data = self.fetch_interest_over_time(batch)
            if not data.empty:
                all_data.append(data)
            polite_delay()

        if all_data:
            return pd.concat(all_data, axis=0).drop_duplicates()
        return pd.DataFrame()

    def fetch_vintage_brand_trends(self):
        """Fetch trends for vintage brands."""
        all_data = []
        vintage_brands = self.keywords['vintage_brands']

        if not vintage_brands:
            print("  No vintage brand keywords found, skipping...")
            return pd.DataFrame()

        for batch in batch_keywords(vintage_brands, 5):
            print(f"Fetching vintage brand trends for: {batch}")
            data = self.fetch_interest_over_time(batch)
            if not data.empty:
                all_data.append(data)
            polite_delay()

        if all_data:
            return pd.concat(all_data, axis=0).drop_duplicates()
        return pd.DataFrame()

    def fetch_texture_trends(self):
        """Fetch trends for bag textures/materials."""
        all_data = []
        textures = self.keywords['textures']

        if not textures:
            print("  No texture keywords found, skipping...")
            return pd.DataFrame()

        for batch in batch_keywords(textures, 5):
            print(f"Fetching texture trends for: {batch}")
            data = self.fetch_interest_over_time(batch)
            if not data.empty:
                all_data.append(data)
            polite_delay()

        if all_data:
            return pd.concat(all_data, axis=0).drop_duplicates()
        return pd.DataFrame()


class EbayScraper:
    """Scraper for eBay sold listings."""

    BASE_URL = "https://www.ebay.com/sch/i.html"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(self, keywords=None):
        self.keywords = keywords or load_keywords()

    def search_sold_listings(self, query, min_price=None, max_price=None):
        """Search for sold listings on eBay."""
        params = {
            "_nkw": query,
            "LH_Sold": "1",  # Only sold items
            "LH_Complete": "1",  # Completed listings
            "_sop": "13",  # Sort by end date (recent)
        }

        if min_price:
            params["_udlo"] = min_price
        if max_price:
            params["_udhi"] = max_price

        try:
            response = requests.get(self.BASE_URL, params=params, headers=self.HEADERS)
            response.raise_for_status()
            return self._parse_listings(response.text, query)
        except Exception as e:
            print(f"Error fetching eBay data for {query}: {e}")
            if gs:
                gs.log_error(f"eBay scraper error for {query}: {str(e)}")
            return []

    def _parse_listings(self, html, query):
        """Parse eBay listing HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        listings = []

        items = soup.select('.s-item')

        for item in items[:20]:  # Limit to first 20 results
            try:
                title_elem = item.select_one('.s-item__title')
                price_elem = item.select_one('.s-item__price')
                date_elem = item.select_one('.s-item__ended-date, .s-item__endedDate')

                if title_elem and price_elem:
                    title = title_elem.get_text(strip=True)
                    price_text = price_elem.get_text(strip=True)

                    # Skip "Shop on eBay" placeholder items
                    if "Shop on eBay" in title:
                        continue

                    # Parse price
                    price = self._parse_price(price_text)

                    listings.append({
                        "query": query,
                        "title": title,
                        "price": price,
                        "date_scraped": datetime.now().isoformat(),
                    })
            except Exception:
                continue

        return listings

    def _parse_price(self, price_text):
        """Extract numeric price from price text."""
        import re
        # Handle price ranges (take the average)
        if "to" in price_text.lower():
            prices = re.findall(r'[\d,]+\.?\d*', price_text)
            if len(prices) >= 2:
                p1 = float(prices[0].replace(',', ''))
                p2 = float(prices[1].replace(',', ''))
                return (p1 + p2) / 2

        # Single price
        match = re.search(r'[\d,]+\.?\d*', price_text)
        if match:
            return float(match.group().replace(',', ''))
        return None

    def fetch_brand_prices(self):
        """Fetch sold prices for all luxury brands."""
        all_listings = []
        brands = self.keywords['brands']

        if not brands:
            print("  No brand keywords found, skipping...")
            return pd.DataFrame()

        # Convert brand keywords to vintage search queries
        for brand in brands:
            # Add "vintage" prefix if not already present
            if brand.lower().startswith("vintage"):
                query = brand
            else:
                query = f"vintage {brand}"

            print(f"Fetching eBay prices for: {query}")
            listings = self.search_sold_listings(query, min_price=100)
            all_listings.extend(listings)
            polite_delay()

        return pd.DataFrame(all_listings)


class PinterestScraper:
    """Scraper for Pinterest trends (requires Playwright)."""

    def __init__(self):
        self.browser = None

    async def init_browser(self):
        """Initialize Playwright browser."""
        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
        except Exception as e:
            print(f"Error initializing Playwright: {e}")
            if gs:
                gs.log_error(f"Playwright init error: {str(e)}")

    async def close_browser(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()

    async def fetch_pinterest_trends(self, search_term):
        """Fetch trend data from Pinterest for a search term."""
        if not self.browser:
            await self.init_browser()

        if not self.browser:
            return None

        try:
            page = await self.browser.new_page()
            url = f"https://www.pinterest.com/search/pins/?q={search_term.replace(' ', '%20')}"
            await page.goto(url, wait_until='networkidle')

            # Add random delay
            await page.wait_for_timeout(random.randint(3000, 8000))

            # Get page content for analysis
            content = await page.content()
            await page.close()

            # Parse pin count or engagement metrics
            soup = BeautifulSoup(content, 'html.parser')

            return {
                "search_term": search_term,
                "date_scraped": datetime.now().isoformat(),
                "has_results": len(soup.select('[data-test-id="pin"]')) > 0
            }
        except Exception as e:
            print(f"Error fetching Pinterest data for {search_term}: {e}")
            if gs:
                gs.log_error(f"Pinterest scraper error for {search_term}: {str(e)}")
            return None


def run_all_scrapers():
    """Run all scrapers and save data to Google Sheets."""
    print("=" * 50)
    print("Starting scraper engine...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 50)

    # Load keywords from local JSON cache
    print("\n[0/1] Loading keywords...")
    keywords = load_keywords()
    print(f"  - Brands: {len(keywords['brands'])} keywords")
    print(f"  - Vintage brands: {len(keywords['vintage_brands'])} keywords")
    print(f"  - Colors: {len(keywords['colors'])} keywords")
    print(f"  - Styles: {len(keywords['styles'])} keywords")
    print(f"  - Textures: {len(keywords['textures'])} keywords")

    # Google Trends
    print("\n[1/1] Fetching Google Trends data...")
    trends_scraper = GoogleTrendsScraper(keywords)

    # Clear existing trends data before fresh scrape
    if gs:
        print("  Clearing old trends data...")
        gs.clear_sheet(gs.SHEET_BRAND_TRENDS)
        gs.clear_sheet(gs.SHEET_VINTAGE_BRAND_TRENDS)
        gs.clear_sheet(gs.SHEET_COLOR_TRENDS)
        gs.clear_sheet(gs.SHEET_STYLE_TRENDS)
        gs.clear_sheet(gs.SHEET_TEXTURE_TRENDS)

    brand_trends = trends_scraper.fetch_all_brand_trends()
    if not brand_trends.empty and gs:
        brand_trends['scraped_at'] = datetime.now().isoformat()
        gs.append_dataframe(gs.SHEET_BRAND_TRENDS, brand_trends)
        print(f"  - Saved {len(brand_trends)} brand trend records")

    vintage_brand_trends = trends_scraper.fetch_vintage_brand_trends()
    if not vintage_brand_trends.empty and gs:
        vintage_brand_trends['scraped_at'] = datetime.now().isoformat()
        gs.append_dataframe(gs.SHEET_VINTAGE_BRAND_TRENDS, vintage_brand_trends)
        print(f"  - Saved {len(vintage_brand_trends)} vintage brand trend records")

    color_trends = trends_scraper.fetch_color_trends()
    if not color_trends.empty and gs:
        color_trends['scraped_at'] = datetime.now().isoformat()
        gs.append_dataframe(gs.SHEET_COLOR_TRENDS, color_trends)
        print(f"  - Saved {len(color_trends)} color trend records")

    style_trends = trends_scraper.fetch_style_trends()
    if not style_trends.empty and gs:
        style_trends['scraped_at'] = datetime.now().isoformat()
        gs.append_dataframe(gs.SHEET_STYLE_TRENDS, style_trends)
        print(f"  - Saved {len(style_trends)} style trend records")

    texture_trends = trends_scraper.fetch_texture_trends()
    if not texture_trends.empty and gs:
        texture_trends['scraped_at'] = datetime.now().isoformat()
        gs.append_dataframe(gs.SHEET_TEXTURE_TRENDS, texture_trends)
        print(f"  - Saved {len(texture_trends)} texture trend records")

    # eBay Prices - TEMPORARILY DISABLED
    # print("\n[2/3] Fetching eBay price data...")
    # ebay_scraper = EbayScraper(keywords)
    # price_data = ebay_scraper.fetch_brand_prices()
    # if not price_data.empty and gs:
    #     gs.append_dataframe(gs.SHEET_PRICES, price_data)
    #     print(f"  - Saved {len(price_data)} price records")

    # Pinterest - TEMPORARILY DISABLED
    # print("\n[3/3] Pinterest scraping...")

    print("\n" + "=" * 50)
    print("Scraper engine complete!")
    print("=" * 50)


if __name__ == "__main__":
    run_all_scrapers()
