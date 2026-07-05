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
        try:
            youtube = self._get_youtube_client()
            title = video_data.get("title", "Untitled")

            body = {
                "snippet": {
                    "title": title,
                    "description": video_data.get("description", ""),
                    "tags": video_data.get("tags", []),
                    "categoryId": "24"
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

    def set_thumbnail(self, video_id, thumbnail_path):
        if not video_id or not thumbnail_path or not os.path.exists(thumbnail_path):
            print("Thumbnail skipped: missing video_id or thumbnail file")
            return False

        try:
            youtube = self._get_youtube_client()
            media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
            print("Thumbnail set for video: " + video_id)
            return True
        except Exception as e:
            print("Thumbnail set error (channel may need phone verification): " + str(e))
            return False

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
