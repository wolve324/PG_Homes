from flask import Blueprint, request, jsonify
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import os

upload_bp = Blueprint("upload", __name__)  # Define Blueprint

# Google Drive Setup
SERVICE_ACCOUNT_FILE = "/home/PGHomes/mysite/service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=credentials)

FOLDER_ID = "1znvuousaTApyLFcXz3xlSAguLG9anumk"

@upload_bp.route("/upload", methods=["POST"])  # Use upload_bp instead of app
def upload_to_drive():
    files = request.files
    responses = {}

    for file_key in files:
        file = files[file_key]
        file_path = f"/tmp/{file.filename}"
        file.save(file_path)

        file_metadata = {"name": file.filename, "parents": [FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=True)
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        responses[file.filename] = f"Uploaded to Drive with ID: {uploaded_file.get('id')}"
        os.remove(file_path)  # Delete temp file

    return jsonify(responses)
