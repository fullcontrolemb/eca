from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from googleapiclient.discovery import build
import os

def authenticate_drive():
    gauth = GoogleAuth()
    # Em ambiente local ele usa o arquivo, na nuvem precisaremos de outra config
    gauth.LocalWebserverAuth() 
    return GoogleDrive(gauth)

def upload_invoice(drive, file_path, folder_id, new_name):
    file_drive = drive.CreateFile({'title': new_name, 'parents': [{'id': folder_id}]})
    file_drive.SetContentFile(file_path)
    file_drive.Upload()
    return file_drive['alternateLink']

def append_to_sheet(data, spreadsheet_id):
    # Lógica simplificada para fins de teste
    print(f"Logging to sheet: {data}")
    # Aqui entraria a lógica da Google Sheets API que vimos antes