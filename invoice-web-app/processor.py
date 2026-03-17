import streamlit as st
import gspread
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import pandas as pd
import io


SPREADSHEET_NAME = "Finance_Manager_2026"


def get_creds(token_json):
    return Credentials(
        token=token_json["access_token"],
        refresh_token=token_json.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=st.secrets["GOOGLE_CLIENT_ID"],
        client_secret=st.secrets["GOOGLE_CLIENT_SECRET"],
    )


def get_month_sheet_name():
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"


def save_to_user_sheets(data, token_json):

    creds = get_creds(token_json)
    client = gspread.authorize(creds)

    try:
        sh = client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        sh = client.create(SPREADSHEET_NAME)

    sheet_name = get_month_sheet_name()

    try:
        worksheet = sh.worksheet(sheet_name)
    except:
        worksheet = sh.add_worksheet(title=sheet_name, rows="1000", cols="10")
        worksheet.append_row(["Date", "Vendor", "Amount", "Currency", "File", "Created At"])

    worksheet.append_row([
        data["date"],
        data["vendor_name"],
        data["total_amount"],
        data["currency"],
        data.get("file_link", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])


def get_monthly_summary(token_json):

    creds = get_creds(token_json)
    client = gspread.authorize(creds)

    try:
        sh = client.open(SPREADSHEET_NAME)
        sheet = sh.worksheet(get_month_sheet_name())
    except:
        return None

    records = sheet.get_all_records()
    if not records:
        return None

    df = pd.DataFrame(records)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    total = df["Amount"].sum()
    daily = df.groupby("Date")["Amount"].sum()

    return {
        "total": total,
        "daily_data": daily
    }


def upload_file_to_drive(uploaded_file, token_json):

    creds = get_creds(token_json)
    drive_service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": uploaded_file.name}

    media = MediaIoBaseUpload(
        io.BytesIO(uploaded_file.read()),
        mimetype=uploaded_file.type
    )

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return f"https://drive.google.com/file/d/{file.get('id')}/view"