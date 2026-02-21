"""
Google Sheets synchronization module for the Vintage Bag Trend Dashboard.
Handles reading and writing data to Google Sheets using service account credentials.
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Sheet names
SHEET_TRENDS = "trends_data"
SHEET_PRICES = "price_data"
SHEET_PINTEREST = "pinterest_data"
SHEET_ERRORS = "error_log"


def get_gspread_client():
    """Get authenticated gspread client using Streamlit secrets."""
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
    return gspread.authorize(credentials)


def get_spreadsheet():
    """Get the main spreadsheet object."""
    client = get_gspread_client()
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
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
    """Append a DataFrame to a sheet."""
    try:
        spreadsheet = get_spreadsheet()
        worksheet = ensure_worksheet_exists(spreadsheet, sheet_name, headers or list(df.columns))

        # Check if sheet is empty (only has headers or is completely empty)
        existing = worksheet.get_all_values()
        if len(existing) <= 1:
            # Sheet is empty or only has headers, add headers if needed
            if len(existing) == 0 and headers:
                worksheet.append_row(headers or list(df.columns))

        # Append data rows
        for _, row in df.iterrows():
            worksheet.append_row(row.tolist())

        return True
    except Exception as e:
        log_error(f"Error appending DataFrame to {sheet_name}: {str(e)}")
        return False


def clear_and_write(sheet_name, df):
    """Clear a sheet and write fresh data."""
    try:
        spreadsheet = get_spreadsheet()
        worksheet = ensure_worksheet_exists(spreadsheet, sheet_name, list(df.columns))
        worksheet.clear()
        worksheet.append_row(list(df.columns))

        for _, row in df.iterrows():
            worksheet.append_row(row.tolist())

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
