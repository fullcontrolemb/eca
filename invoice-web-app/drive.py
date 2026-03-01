from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from sheets import get_creds
from datetime import datetime
import io


MAIN_FOLDER_NAME = "Finance_Manager"


def get_or_create_folder(drive, name, parent_id=None):
    """
    Busca uma pasta pelo nome.
    Se não existir, cria.
    """

    query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"

    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = drive.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])

    if folders:
        return folders[0]["id"]

    file_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder"
    }

    if parent_id:
        file_metadata["parents"] = [parent_id]

    folder = drive.files().create(body=file_metadata, fields="id").execute()
    return folder["id"]


def upload_file(uploaded_file, token_json):
    """
    Salva arquivo na estrutura:
    Finance_Manager/AAAA-MM/
    """

    creds = get_creds(token_json)
    drive = build("drive", "v3", credentials=creds)

    # 1️⃣ Garante pasta principal
    main_folder_id = get_or_create_folder(drive, MAIN_FOLDER_NAME)

    # 2️⃣ Define pasta do mês atual
    now = datetime.now()
    month_folder_name = f"{now.year}-{now.month:02d}"

    month_folder_id = get_or_create_folder(
        drive,
        month_folder_name,
        parent_id=main_folder_id
    )

    # 3️⃣ Upload do arquivo dentro da pasta do mês
    media = MediaIoBaseUpload(
        io.BytesIO(uploaded_file.read()),
        mimetype=uploaded_file.type
    )

    file_metadata = {
        "name": uploaded_file.name,
        "parents": [month_folder_id]
    }

    file = drive.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return f"https://drive.google.com/file/d/{file['id']}/view"