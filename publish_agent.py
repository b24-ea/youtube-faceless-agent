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
            "https://www.googleapis.com/auth/youtube"
        ]

    def upload(self, video_path, video_data):
        """Shorts icin - gun kisitlamasi yok, her calismada yukler"""
        youtube = self._get_youtube_client()
        title = video_data.get("title", "Video")
        if "#Shorts" not in title:
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

    def upload_long_form(self, video_path, video_data):
        """
        Uzun format (8dk) komplo teorisi videolari icin.
        #Shorts etiketi YOK, farkli kategori (Entertainment=24 veya People&Blogs=22).
        """
        try:
            youtube = self._get_youtube_client()
            title = video_data.get("title", "Untitled")

            body = {
                "snippet": {
                    "title": title,
                    "description": video_data.get("description", ""),
                    "tags": video_data.get("tags", []),
                    "categoryId": "24"  # Entertainment
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
            print("Uploaded (long-form): https://youtube.com/watch?v=" + video_id)
            return video_id
        except Exception as e:
            print("Long-form upload error: " + str(e))
            return None

    def _get_youtube_client(self):
        token_b64 = os.environ.get("YOUTUBE_TOKEN")
        if not token_b64:
            raise ValueError("YOUTUBE_TOKEN not found!")

        token_data = json.loads(base64.b64decode(token_b64).decode())
        creds = Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes")
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return build("youtube", "v3", credentials=creds)
