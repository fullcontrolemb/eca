from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from sheets import get_creds


def upload_file(uploaded_file, token_json):
    creds = get_creds(token_json)
    drive = build("drive", "v3", credentials=creds)

    media = MediaIoBaseUpload(
        io.BytesIO(uploaded_file.read()),
        mimetype=uploaded_file.type
    )

    file = drive.files().create(
        body={"name": uploaded_file.name},
        media_body=media,
        fields="id"
    ).execute()

    return f"https://drive.google.com/file/d/{file['id']}/view"