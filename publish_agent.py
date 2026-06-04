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
        title = video_data.get("title", "Mystery Video")
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
        media = MediaFileUpload(video_path, mime
