import os
import asyncio
import requests
import edge_tts
import subprocess


class ProductionAgent:
    def __init__(self):
        self.output_dir = "output"
        self.voice = "en-US-AriaNeural"
        self.pexels_api_key = os.environ.get("PEXELS_API_KEY")
        os.makedirs(self.output_dir, exist_ok=True)

    def create_video(self, video_data):
        print("  🎙️  Generating voiceover...")
        audio_path = self._generate_audio(video_data["script"])

        print("  🎬 Downloading stock video clips...")
        clip_paths = self._download_video_clips(video_data["visual_descriptions"], video_data["title"])

        print("  🎞️  Combining video...")
        video_path = self._combine_to_video(audio_path, clip_paths)

        return video_path

    def _generate_audio(self, script):
        if isinstance(script, dict):
            script = " ".join([str(v) for v in script.values()])
        script = str(script)[:4500]
        audio_path = f"{self.output_dir}/audio.mp3"

        async def _tts():
            communicate = edge_tts.Communicate(script, self.voice)
            await communicate.save(audio_path)

        asyncio.run(_tts())
        return audio_path

    def _download_video_clips(self, visual_descriptions, title):
        clip_paths = []
        queries = self._build_search_queries(visual_descriptions, title)

        for i, query in enumerate(queries[:6]):
            clip_path = f"{self.output_dir}/clip_{i}.mp4"
            success = self._fetch_pexels_video(query, clip_path)
            if success:
                print(f"    ✅ Clip {i+1} downloaded: {query}")
                clip_paths.append(clip_path)
            else:
                print(f"    ⚠️  No clip found for: {query}, trying fallback...")
                fallback_success = self._fetch_pexels_video("dark mystery forest night", clip_path)
                if fallback_success:
                    clip_paths.append(clip_path)

        return clip_paths

    def _build_search_queries(self, visual_descriptions, title):
        queries = []
        keywords = [
            "dark mystery", "abandoned building", "foggy forest night",
            "dramatic sky storm", "empty road night", "old documents"
        ]
        for i, desc in enumerate(visual_descriptions[:4]):
            words = desc.lower().split()
            useful = [w for w in words if len(w) > 4][:3]
            if useful:
                queries.append(" ".join(useful))
            else:
                queries.append(keywords[i % len(keywords)])
        queries += keywords[:2]
        return queries

    def _fetch_pexels_video(self, query, save_path):
        try:
            headers = {"Authorization": self.pexels_api_key}
            params = {"query": query, "per_page": 5, "orientation": "landscape"}
            response = requests.get(
                "https://api.pexels.com/videos/search",
                headers=headers,
                params=params,
                timeout=15
            )
            data = response.json()
            videos = data.get("videos", [])

            if not videos:
                return False

            video = videos[0]
            video_files = video.get("video_files", [])
            hd_files = [f for f in video_files if f.get("quality") in ["hd", "sd"] and f.get("width", 0) >= 1280]
            if not hd_files:
                hd_files = video_files

            if not hd_files:
                return False

            video_url = hd_files[0]["link"]
            video_response = requests.get(video_url, timeout=60, stream=True)

            with open(save_path, "wb") as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True

        except Exception as e:
            print(f"    Pexels error: {e}")
            return False

    def _combine_to_video(self, audio_path, clip_paths):
        video_path = f"{self.output_dir}/final_video.mp4"

        if not clip_paths:
            print("  ⚠️  No clips available!")
            return None

        # Her klibi 1920x1080'e normalize et
        normalized = []
        for i, clip in enumerate(clip_paths):
            norm_path = f"{self.output_dir}/norm_{i}.mp4"
            cmd = (
                f"ffmpeg -y -i {clip} "
                f"-vf \"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2\"
                f"-c:v libx264 -an -t 30 {norm_path}"
            )
            os.system(cmd)
            if os.path.exists(norm_path):
                normalized.append(norm_path)

        if not normalized:
            return None

        # Klipleri birleştir
        concat_file = f"{self.output_dir}/concat.txt"
        with open(concat_file, "w") as f:
            for clip in normalized:
                f.write(f"file '{os.path.abspath(clip)}'\n")

        merged_path = f"{self.output_dir}/merged.mp4"
        os.system(f"ffmpeg -y -f concat -safe 0 -i {concat_file} -c copy {merged_path}")

        # Ses ekle
        os.system(
            f"ffmpeg -y -i {merged_path} -i {audio_path} "
            f"-map 0:v -map 1:a -c:v copy -c:a aac -shortest {video_path}"
        )

        return video_path
