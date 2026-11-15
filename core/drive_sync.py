import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'

def get_drive_service():
    """Authenticates the user and returns the Google Drive service object."""
    if not os.path.exists(CREDS_FILE):
        return None, "Missing credentials.json"
        
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
            
    try:
        service = build('drive', 'v3', credentials=creds)
        return service, None
    except Exception as e:
        return None, str(e)

def upload_to_drive(filepath, filename):
    service, error = get_drive_service()
    if error:
        return False, error
        
    try:
        file_metadata = {'name': filename}
        media = MediaFileUpload(filepath, mimetype='application/json')
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return True, f"File uploaded successfully! ID: {file.get('id')}"
    except Exception as e:
        return False, str(e)

def list_drive_files():
    service, error = get_drive_service()
    if error:
        return None, error
        
    try:
        # Search for .mukta files in the user's Drive
        results = service.files().list(
            q="name contains '.mukta'",
            pageSize=20, 
            fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        return items, None
    except Exception as e:
        return None, str(e)

def download_from_drive(file_id, filepath):
    import io
    service, error = get_drive_service()
    if error:
        return False, error
        
    try:
        request = service.files().get_media(fileId=file_id)
        with open(filepath, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
        return True, "File downloaded successfully!"
    except Exception as e:
        return False, str(e)
