import os
import json
import base64
import requests
from io import BytesIO
from PIL import Image, ImageDraw
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
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        fal_key = os.environ.get("FAL_API_KEY", "")
        os.environ["FAL_KEY"] = fal_key

    def upload(self, video_path, video_data, is_shorts=False):
        youtube = self._get_youtube_client()
        title = video_data.get("title", "Fun Video")
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
        thumbnail_path = self._create_thumbnail(video_data)
        if thumbnail_path:
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path)
                ).execute()
                print("Thumbnail uploaded")
            except Exception as e:
                print("Thumbnail upload error: " + str(e))
        return video_id

    def _create_thumbnail(self, video_data):
        try:
            import fal_client
            thumbnail_path = os.path.join("output", "thumbnail.jpg")
            concept = video_data.get("thumbnail_concept", "dark mysterious scene")
            title = video_data.get("title", "Mystery Video")
            prompt = (
                "YouTube thumbnail, dark mysterious atmosphere, " +
                concept +
                ". Cinematic, dramatic lighting, high quality, professional, no text overlay."
            )
            result = fal_client.subscribe(
                "fal-ai/flux/schnell",
                arguments={"prompt": prompt, "image_size": "landscape_16_9", "num_images": 1}
            )
            if result and result.get("images") and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                r = requests.get(image_url, timeout=30)
                img = Image.open(BytesIO(r.content))
                img = img.resize((1280, 720), Image.LANCZOS)
                draw = ImageDraw.Draw(img)
                words = title.upper().replace("#SHORTS", "").strip().split()
                mid = max(1, len(words) // 2)
                line1 = " ".join(words[:mid])
                line2 = " ".join(words[mid:])
                for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                    draw.text((642 + offset[0], 602 + offset[1]), line1, fill=(0, 0, 0), anchor="mm")
                    if line2:
                        draw.text((642 + offset[0], 662 + offset[1]), line2, fill=(0, 0, 0), anchor="mm")
                draw.text((640, 600), line1, fill=(255, 50, 50), anchor="mm")
                if line2:
                    draw.text((640, 660), line2, fill=(255, 255, 255), anchor="mm")
                img.save(thumbnail_path, "JPEG", quality=95)
                print("Thumbnail created with fal.ai Flux")
                return thumbnail_path
        except Exception as e:
            print("Thumbnail error: " + str(e))
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
