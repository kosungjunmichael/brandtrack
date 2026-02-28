"""
Google Sheets synchronization module for the Vintage Bag Trend Dashboard.
Handles reading and writing data to Google Sheets using service account credentials.
"""

import streamlit as st
import pandas as pd
import gspread
import os
from google.oauth2.service_account import Credentials
from datetime import datetime


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Sheet names
SHEET_TRENDS = "trends_data"  # Legacy, kept for compatibility
SHEET_BRAND_TRENDS = "brand_trends"
SHEET_VINTAGE_BRAND_TRENDS = "vintage_brand_trends"
SHEET_COLOR_TRENDS = "color_trends"
SHEET_STYLE_TRENDS = "style_trends"
SHEET_TEXTURE_TRENDS = "texture_trends"
SHEET_PRICES = "price_data"
SHEET_PINTEREST = "pinterest_data"
SHEET_ERRORS = "error_log"
SHEET_KEYWORDS = "keywords"


CREDENTIALS_JSON_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1o75hpU7tcnAFqj1X7uAFOM5U2_mOxA55SN1tWhXD29s"


def _is_streamlit():
    """Return True when running inside a Streamlit session."""
    try:
        # st.secrets raises an error outside of Streamlit context
        _ = st.secrets["connections"]
        return True
    except Exception:
        return False


def get_gspread_client():
    """Get authenticated gspread client.

    Uses Streamlit secrets when running inside the app, otherwise falls back
    to the local credentials.json service account file.
    """
    if _is_streamlit():
        creds_dict = {
            "type": "service_account",
            "project_id": st.secrets["connections"]["gsheets"]["project_id"],
            "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
            "private_key": st.secrets["connections"]["gsheets"]["private_key"],
            "client_email": st.secrets["connections"]["gsheets"]["client_email"],
            "client_id": st.secrets["connections"]["gsheets"]["client_id"],
            "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
            "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"],
        }
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        credentials = Credentials.from_service_account_file(CREDENTIALS_JSON_PATH, scopes=SCOPES)

    return gspread.authorize(credentials)


def get_spreadsheet():
    """Get the main spreadsheet object."""
    client = get_gspread_client()
    if _is_streamlit():
        spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    else:
        spreadsheet_url = SPREADSHEET_URL
    return client.open_by_url(spreadsheet_url)


def ensure_worksheet_exists(spreadsheet, sheet_name, headers=None):
    """Ensure a worksheet exists, create it if it doesn't."""
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
        if headers:
            worksheet.append_row(headers)
    return worksheet


def read_sheet_data(sheet_name):
    """Read all data from a specific sheet as a DataFrame."""
    try:
        spreadsheet = get_spreadsheet()
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except gspread.WorksheetNotFound:
        return pd.DataFrame()
    except Exception as e:
        log_error(f"Error reading {sheet_name}: {str(e)}")
        return pd.DataFrame()


def append_data(sheet_name, data_row, headers=None):
    """Append a single row of data to a sheet."""
    try:
        spreadsheet = get_spreadsheet()
        worksheet = ensure_worksheet_exists(spreadsheet, sheet_name, headers)
        worksheet.append_row(data_row)
        return True
    except Exception as e:
        log_error(f"Error appending to {sheet_name}: {str(e)}")
        return False


def append_dataframe(sheet_name, df, headers=None):
    """Append a DataFrame to a sheet using batch update for speed."""
    try:
        spreadsheet = get_spreadsheet()
        worksheet = ensure_worksheet_exists(spreadsheet, sheet_name, headers or list(df.columns))

        # Check if sheet is empty (only has headers or is completely empty)
        existing = worksheet.get_all_values()
        if len(existing) <= 1:
            # Sheet is empty or only has headers, add headers if needed
            if len(existing) == 0:
                worksheet.append_row(headers or list(df.columns))
                existing = [[]]  # Update to reflect header was added

        # Convert DataFrame to list of lists, handling Timestamps and NaN
        rows = []
        for _, row in df.iterrows():
            row_values = []
            for val in row.tolist():
                if hasattr(val, 'isoformat'):  # Handle Timestamp/datetime objects
                    row_values.append(val.isoformat())
                elif pd.isna(val):  # Handle NaN/NaT
                    row_values.append('')
                else:
                    row_values.append(val)
            rows.append(row_values)

        # Batch append all rows at once (much faster than row-by-row)
        if rows:
            worksheet.append_rows(rows, value_input_option='RAW')

        return True
    except Exception as e:
        log_error(f"Error appending DataFrame to {sheet_name}: {str(e)}")
        return False


def clear_sheet(sheet_name):
    """Clear all data from a sheet."""
    try:
        spreadsheet = get_spreadsheet()
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.clear()
        return True
    except gspread.WorksheetNotFound:
        return True  # Sheet doesn't exist, nothing to clear
    except Exception as e:
        log_error(f"Error clearing {sheet_name}: {str(e)}")
        return False


def clear_and_write(sheet_name, df):
    """Clear a sheet and write fresh data."""
    try:
        spreadsheet = get_spreadsheet()
        worksheet = ensure_worksheet_exists(spreadsheet, sheet_name, list(df.columns))
        worksheet.clear()
        worksheet.append_row(list(df.columns))

        for _, row in df.iterrows():
            row_values = []
            for val in row.tolist():
                if hasattr(val, 'isoformat'):  # Handle Timestamp/datetime objects
                    row_values.append(val.isoformat())
                elif pd.isna(val):  # Handle NaN/NaT
                    row_values.append('')
                else:
                    row_values.append(val)
            worksheet.append_row(row_values)

        return True
    except Exception as e:
        log_error(f"Error writing to {sheet_name}: {str(e)}")
        return False


def log_error(error_message):
    """Log an error to the error_log sheet."""
    try:
        spreadsheet = get_spreadsheet()
        headers = ["timestamp", "error_message"]
        worksheet = ensure_worksheet_exists(spreadsheet, SHEET_ERRORS, headers)
        worksheet.append_row([datetime.now().isoformat(), error_message])
    except Exception:
        # If we can't even log the error, just pass
        pass


def get_trends_data(days=30):
    """Get Google Trends data, optionally filtered by days."""
    df = read_sheet_data(SHEET_TRENDS)
    if df.empty:
        return df

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        cutoff = datetime.now() - pd.Timedelta(days=days)
        df = df[df["date"] >= cutoff]

    return df


def get_price_data():
    """Get eBay price data."""
    return read_sheet_data(SHEET_PRICES)


def get_pinterest_data():
    """Get Pinterest trends data."""
    return read_sheet_data(SHEET_PINTEREST)


def get_keywords():
    """
    Get keywords from the keywords sheet.

    Returns a dict with keys: 'textures', 'colors', 'styles', 'brands'
    Column A = Textures, B = Colors, C = Styles & Trends, D = Brands
    """
    try:
        spreadsheet = get_spreadsheet()
        worksheet = spreadsheet.worksheet(SHEET_KEYWORDS)

        # Get all values from each column (skip header row)
        all_values = worksheet.get_all_values()

        if len(all_values) <= 1:
            return {'textures': [], 'colors': [], 'styles': [], 'brands': []}

        # Skip header row, extract each column
        data_rows = all_values[1:]

        textures = [row[0].strip() for row in data_rows if len(row) > 0 and row[0].strip()]
        colors = [row[1].strip() for row in data_rows if len(row) > 1 and row[1].strip()]
        styles = [row[2].strip() for row in data_rows if len(row) > 2 and row[2].strip()]
        brands = [row[3].strip() for row in data_rows if len(row) > 3 and row[3].strip()]
        vintage_brands = [row[4].strip() for row in data_rows if len(row) > 4 and row[4].strip()]

        return {
            'textures': textures,
            'colors': colors,
            'styles': styles,
            'brands': brands,
            'vintage_brands': vintage_brands,
        }
    except gspread.WorksheetNotFound:
        log_error(f"Keywords sheet '{SHEET_KEYWORDS}' not found")
        return {'textures': [], 'colors': [], 'styles': [], 'brands': []}
    except Exception as e:
        log_error(f"Error reading keywords: {str(e)}")
        return {'textures': [], 'colors': [], 'styles': [], 'brands': []}


if __name__ == "__main__":
    print("Fetching keywords from Google Sheets...")
    keywords = get_keywords()
    if any(keywords.values()):
        print(f"  - Textures: {len(keywords['textures'])}")
        print(f"  - Colors: {len(keywords['colors'])}")
        print(f"  - Styles: {len(keywords['styles'])}")
        print(f"  - Brands: {len(keywords['brands'])}")
        print(f"  - Vintage brands: {len(keywords['vintage_brands'])}")
    else:
        print("Warning: No keywords found in Google Sheets")
