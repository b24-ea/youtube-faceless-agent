import os
import json
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class PublishAgent:
    def __init__(self):
        self.scopes = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/yt-analytics.readonly"
        ]

 def upload(self, video_path, video_data, is_shorts=False):
        youtube = self._get_youtube_client()
        title = video_data.get("title", "Mysterious Video")
        if is_shorts and "#Shorts" not in title:
            title = title + " #Shorts"
        body = {
            "snippet": {
                "title": title,
                "description": video_data.get("description", ""),
                "tags": video_data.get("tags", []),
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()
        video_id = response["id"]
        print("Uploaded: https://youtube.com/watch?v=" + video_id)
        return video_id

    def _get_youtube_client(self):
        token_b64 = os.environ.get("YOUTUBE_TOKEN")
        
        if not token_b64:
            raise ValueError("YOUTUBE_TOKEN secret bulunamadı!")
        
        try:
            token_data = json.loads(base64.b64decode(token_b64).decode())
        except Exception as e:
            raise ValueError(f"Token parse hatası: {e}")
        
        creds = Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes")
        )
        
        # Token süresi dolmuşsa yenile
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        return build("youtube", "v3", credentials=creds)
