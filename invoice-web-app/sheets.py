import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.credentials import Credentials
from config import SPREADSHEET_NAME
import streamlit as st


def get_creds(token_json):
    return Credentials(
        token=token_json["access_token"],
        refresh_token=token_json.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=st.secrets["GOOGLE_CLIENT_ID"],
        client_secret=st.secrets["GOOGLE_CLIENT_SECRET"],
    )


def get_month_sheet():
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"


def save_invoice(data, token_json):
    creds = get_creds(token_json)
    client = gspread.authorize(creds)

    try:
        sh = client.open(SPREADSHEET_NAME)
    except:
        sh = client.create(SPREADSHEET_NAME)

    sheet_name = get_month_sheet()

    try:
        ws = sh.worksheet(sheet_name)
    except:
        ws = sh.add_worksheet(title=sheet_name, rows="1000", cols="10")
        ws.append_row(["Date", "Vendor", "Amount", "Currency", "Category", "File", "Created"])

    ws.append_row([
        data["date"],
        data["vendor"],
        data["amount"],
        data["currency"],
        data["category"],
        data.get("file", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])


def get_summary(token_json):
    creds = get_creds(token_json)
    client = gspread.authorize(creds)

    try:
        sh = client.open(SPREADSHEET_NAME)
        ws = sh.worksheet(get_month_sheet())
    except:
        return None

    records = ws.get_all_records()
    if not records:
        return None

    df = pd.DataFrame(records)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    return {
        "total": df["Amount"].sum(),
        "by_category": df.groupby("Category")["Amount"].sum()
    }