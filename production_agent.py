import os
import asyncio
import requests
import edge_tts


class ProductionAgent:
    def __init__(self):
        self.output_dir = "output"
        self.voice = "en-US-AriaNeural"
        self.pexels_api_key = os.environ.get("PEXELS_API_KEY")
        os.makedirs(self.output_dir, exist_ok=True)

    def create_video(self, video_data):
        audio_path = self._generate_audio(video_data["script"])
        clip_paths = self._download_video_clips(video_data["visual_descriptions"])
        video_path = self._combine_to_video(audio_path, clip_paths)
        return video_path

    def _generate_audio(self, script):
        if isinstance(script, dict):
            script = " ".join([str(v) for v in script.values()])
        script = str(script)[:4500]
        audio_path = os.path.join(self.output_dir, "audio.mp3")

        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.audio.speech.create(
                model="tts-1-hd",
                voice="onyx",
                input=script
            )
            response.stream_to_file(audio_path)
            print("OpenAI TTS audio generated")
        except Exception as e:
            print("OpenAI TTS error: " + str(e) + ", falling back to Edge-TTS")
            async def _tts():
                communicate = edge_tts.Communicate(script, self.voice)
                await communicate.save(audio_path)
            asyncio.run(_tts())

        return audio_path

    def _download_video_clips(self, visual_descriptions):
        clip_paths = []
        fallbacks = [
            "dark mystery forest",
            "abandoned building night",
            "foggy road night",
            "dramatic storm sky"
        ]
        queries = []
        for desc in visual_descriptions[:4]:
            words = [w for w in str(desc).lower().split() if len(w) > 4][:3]
            queries.append(" ".join(words) if words else "dark mystery")
        queries += fallbacks[:2]
        for i, query in enumerate(queries[:6]):
            clip_path = os.path.join(self.output_dir, "clip_" + str(i) + ".mp4")
            if self._fetch_pexels_video(query, clip_path):
                clip_paths.append(clip_path)
            elif self._fetch_pexels_video("dark mystery", clip_path):
                clip_paths.append(clip_path)
        return clip_paths

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
            video_files = videos[0].get("video_files", [])
            hd_files = [f for f in video_files if f.get("width", 0) >= 1280]
            if not hd_files:
                hd_files = video_files
            if not hd_files:
                return False
            r = requests.get(hd_files[0]["link"], timeout=60, stream=True)
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print("Pexels error: " + str(e))
            return False

    def _combine_to_video(self, audio_path, clip_paths):
        if not clip_paths:
            return None
        video_path = os.path.join(self.output_dir, "final_video.mp4")
        normalized = []
        for i, clip in enumerate(clip_paths):
            norm_path = os.path.join(self.output_dir, "norm_" + str(i) + ".mp4")
            vf = "scale=1920:1080:force_original_aspect_ratio=decrease,"
            vf += "pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
            cmd = "ffmpeg -y -i " + clip + " -vf \"" + vf + "\""
            cmd += " -c:v libx264 -an -t 30 " + norm_path
            os.system(cmd)
            if os.path.exists(norm_path):
                normalized.append(norm_path)
        if not normalized:
            return None
        concat_file = os.path.join(self.output_dir, "concat.txt")
        with open(concat_file, "w") as f:
            for clip in normalized:
                f.write("file '" + os.path.abspath(clip) + "'\n")
        merged_path = os.path.join(self.output_dir, "merged.mp4")
        cmd = "ffmpeg -y -f concat -safe 0 -i " + concat_file + " -c copy " + merged_path
        os.system(cmd)
        cmd = "ffmpeg -y -i " + merged_path + " -i " + audio_path
        cmd += " -map 0:v -map 1:a -c:v copy -c:a aac -shortest " + video_path
        os.system(cmd)
        if os.path.exists(video_path):
            return video_path
        return None