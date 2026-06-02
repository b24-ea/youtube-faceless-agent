import os
import json
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class PublishAgent:
    def __init__(self):
        self.scopes = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube"
        ]

    def upload(self, video_path: str, video_data: dict) -> str:
        youtube = self._get_youtube_client()
        
        body = {
            "snippet": {
                "title": video_data.get("title", "Mysterious Video"),
                "description": video_data.get("description", ""),
                "tags": video_data.get("tags", []),
                "categoryId": "22"  # People & Blogs
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True
        )
        
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = request.execute()
        return response["id"]

    def _get_youtube_client(self):
        creds = None
        client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
        
        # JSON string'i dosyaya yaz
        with open("client_secret.json", "w") as f:
            f.write(client_secret)
        
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json", self.scopes
        )
        creds = flow.run_local_server(port=0)
        
        return build("youtube", "v3", credentials=creds)
