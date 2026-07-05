import os
import requests
import random


class StockAgent:
    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        self.pexels_key = os.environ.get("PEXELS_API_KEY", "")
        self.pixabay_key = os.environ.get("PIXABAY_API_KEY", "")

    def fetch_stock_clip(self, query, duration, index):
        """
        Once video, olmazsa resim (Ken Burns ile) dener. Ikisi de basarisiz olursa None doner
        (cagiran taraf FLUX ile doldurmali).
        """
        video_path = os.path.join(self.output_dir, "stock_" + str(index) + ".mp4")

        video_source = self._fetch_pexels_video(query)
        if not video_source:
            video_source = self._fetch_pixabay_video(query)

        if video_source:
            if self._fit_video_to_duration(video_source, video_path, duration):
                return video_path

        image_source = self._fetch_pexels_image(query)
        if not image_source:
            image_source = self._fetch_pixabay_image(query)

        if image_source:
            if self._image_to_video_kenburns(image_source, video_path, duration):
                return video_path

        print("  Stock fetch failed for query: " + query)
        return None

    def _fetch_pexels_video(self, query):
        try:
            url = "https://api.pexels.com/videos/search"
            headers = {"Authorization": self.pexels_key}
            params = {"query": query, "per_page": 5, "orientation": "landscape"}
            r = requests.get(url, headers=headers, params=params, timeout=20)
            if r.status_code != 200:
                return None
            data = r.json()
            videos = data.get("videos", [])
            if not videos:
                return None

            video = random.choice(videos)
            files = video.get("video_files", [])
            # HD kalite ve landscape olani tercih et
            hd_files = [f for f in files if f.get("width", 0) >= 1280 and f.get("width", 0) <= 1920]
            chosen = hd_files[0] if hd_files else (files[0] if files else None)
            if not chosen:
                return None

            download_path = os.path.join(self.output_dir, "pexels_src.mp4")
            r2 = requests.get(chosen["link"], timeout=60, stream=True)
            with open(download_path, "wb") as f:
                for chunk in r2.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("  Pexels video: " + query)
            return download_path
        except Exception as e:
            print("  Pexels video error: " + str(e))
            return None

    def _fetch_pixabay_video(self, query):
        try:
            url = "https://pixabay.com/api/videos/"
            params = {"key": self.pixabay_key, "q": query, "per_page": 5, "orientation": "horizontal"}
            r = requests.get(url, params=params, timeout=20)
            if r.status_code != 200:
                return None
            data = r.json()
            hits = data.get("hits", [])
            if not hits:
                return None

            hit = random.choice(hits)
            videos = hit.get("videos", {})
            chosen_url = videos.get("large", {}).get("url") or videos.get("medium", {}).get("url")
            if not chosen_url:
                return None

            download_path = os.path.join(self.output_dir, "pixabay_src.mp4")
            r2 = requests.get(chosen_url, timeout=60, stream=True)
            with open(download_path, "wb") as f:
                for chunk in r2.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("  Pixabay video: " + query)
            return download_path
        except Exception as e:
            print("  Pixabay video error: " + str(e))
            return None

    def _fetch_pexels_image(self, query):
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_key}
            params = {"query": query, "per_page": 5, "orientation": "landscape"}
            r = requests.get(url, headers=headers, params=params, timeout=20)
            if r.status_code != 200:
                return None
            data = r.json()
            photos = data.get("photos", [])
            if not photos:
                return None

            photo = random.choice(photos)
            image_url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if not image_url:
                return None

            download_path = os.path.join(self.output_dir, "pexels_img.jpg")
            r2 = requests.get(image_url, timeout=30)
            with open(download_path, "wb") as f:
                f.write(r2.content)
            print("  Pexels image: " + query)
            return download_path
        except Exception as e:
            print("  Pexels image error: " + str(e))
            return None

    def _fetch_pixabay_image(self, query):
        try:
            url = "https://pixabay.com/api/"
            params = {"key": self.pixabay_key, "q": query, "per_page": 5, "orientation": "horizontal", "image_type": "photo"}
            r = requests.get(url, params=params, timeout=20)
            if r.status_code != 200:
                return None
            data = r.json()
            hits = data.get("hits", [])
            if not hits:
                return None

            hit = random.choice(hits)
            image_url = hit.get("largeImageURL")
            if not image_url:
                return None

            download_path = os.path.join(self.output_dir, "pixabay_img.jpg")
            r2 = requests.get(image_url, timeout=30)
            with open(download_path, "wb") as f:
                f.write(r2.content)
            print("  Pixabay image: " + query)
            return download_path
        except Exception as e:
            print("  Pixabay image error: " + str(e))
            return None

    def _fit_video_to_duration(self, source_path, output_path, duration):
        """Stok videoyu tam istenen sureye getirir - kisaysa loop, uzunsa kirp"""
        try:
            cmd = (
                "ffmpeg -y -stream_loop -1 -i " + source_path +
                " -t " + str(duration) +
                " -vf \"scale=1920:1080:force_original_aspect_ratio=decrease,"
                "pad=1920:1080:(ow-iw)/2:(oh-ih)/2\" "
                "-c:v libx264 -r 24 -pix_fmt yuv420p -an " + output_path
            )
            result = os.system(cmd)
            return result == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000
        except Exception as e:
            print("  Video fit error: " + str(e))
            return False

    def _image_to_video_kenburns(self, image_path, video_path, duration):
        try:
            fps = 24
            total_frames = max(1, int(fps * duration))
            vf = (
                "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
                "zoompan=z='min(zoom+0.0006,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                "d=" + str(total_frames) + ":s=1920x1080:fps=" + str(fps)
            )
            cmd = (
                "ffmpeg -y -loop 1 -i " + image_path +
                " -vf \"" + vf + "\" -c:v libx264 -t " + str(duration) +
                " -pix_fmt yuv420p -an " + video_path
            )
            result = os.system(cmd)
            return result == 0 and os.path.exists(video_path) and os.path.getsize(video_path) > 1000
        except Exception as e:
            print("  Kenburns error: " + str(e))
            return False
