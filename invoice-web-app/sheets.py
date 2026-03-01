import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.credentials import Credentials
import streamlit as st

SPREADSHEET_NAME = "Finance_Control_2026"

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

def create_monthly_sheet_if_not_exists(token_json):
    creds = get_creds(token_json)
    client = gspread.authorize(creds)

    try:
        sh = client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        sh = client.create(SPREADSHEET_NAME)

    sheet_name = get_month_sheet()

    try:
        worksheet = sh.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=sheet_name, rows="1000", cols="10")
        worksheet.append_row(
            ["Data", "Tipo", "Valor", "Descrição", "Observação", "Criado Em"]
        )

    return sh.worksheet(sheet_name)

def save_entry(data, token_json):
    ws = create_monthly_sheet_if_not_exists(token_json)

    ws.append_row([
        data["date"],
        data["type"],
        data["value"],
        data["description"],
        data["obs"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

def get_month_data(token_json):
    try:
        creds = get_creds(token_json)
        client = gspread.authorize(creds)
        sh = client.open(SPREADSHEET_NAME)

        ws = sh.worksheet(get_month_sheet())
        records = ws.get_all_records()
        df = pd.DataFrame(records)
    except Exception as e:
        return None

    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

    entradas = df[df["Tipo"] == "Entrada"]["Valor"].sum()
    saidas = df[df["Tipo"] == "Saída"]["Valor"].sum()
    saldo = entradas - saidas

    return df, entradas, saidas, saldo