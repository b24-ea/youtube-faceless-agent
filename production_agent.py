import os
import asyncio
import requests
import edge_tts
import re
import time
import jwt


class ProductionAgent:
    def __init__(self):
        self.output_dir = "output"
        self.voice = "en-US-AriaNeural"
        self.pexels_api_key = os.environ.get("PEXELS_API_KEY")
        self.elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.kling_access_key = os.environ.get("KLING_ACCESS_KEY")
        self.kling_secret_key = os.environ.get("KLING_SECRET_KEY")
        os.makedirs(self.output_dir, exist_ok=True)

    def create_video(self, video_data):
        audio_path = self._generate_audio(video_data["script"])
        audio_duration = self._get_audio_duration(audio_path)
        segments = self._split_script_to_segments(video_data["script"], audio_duration)
        clip_paths = self._download_clips_for_segments(segments)
        video_path = self._combine_to_video(audio_path, clip_paths, audio_duration)
        return video_path

    def _generate_audio(self, script):
        if isinstance(script, dict):
            script = " ".join([str(v) for v in script.values()])
        script = str(script)[:4500]
        audio_path = os.path.join(self.output_dir, "audio.mp3")

        try:
            url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"
            headers = {
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            body = {
                "text": script,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.8,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            response = requests.post(url, json=body, headers=headers, timeout=60)
            if response.status_code == 200:
                with open(audio_path, "wb") as f:
                    f.write(response.content)
                print("ElevenLabs audio generated")
                return audio_path
            else:
                print("ElevenLabs error: " + str(response.status_code) + " " + response.text[:200])
        except Exception as e:
            print("ElevenLabs error: " + str(e))

        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.audio.speech.create(
                model="tts-1-hd",
                voice="onyx",
                input=script
            )
            response.stream_to_file(audio_path)
            print("OpenAI TTS fallback used")
            return audio_path
        except Exception as e:
            print("OpenAI TTS error: " + str(e))

        async def _tts():
            communicate = edge_tts.Communicate(script, self.voice)
            await communicate.save(audio_path)
        asyncio.run(_tts())
        print("Edge-TTS fallback used")
        return audio_path

    def _get_audio_duration(self, audio_path):
        try:
            import subprocess
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                capture_output=True, text=True
            )
            duration = float(result.stdout.strip())
            print("Audio duration: " + str(round(duration, 1)) + "s")
            return duration
        except Exception as e:
            print("Duration error: " + str(e))
            return 180.0

    def _split_script_to_segments(self, script, audio_duration):
        if isinstance(script, dict):
            script = " ".join([str(v) for v in script.values()])
        script = str(script)
        sentences = re.split(r'(?<=[.!?])\s+', script)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        segment_duration = 10.0
        num_segments = max(1, int(audio_duration / segment_duration))
        if len(sentences) == 0:
            return [{"text": script, "duration": segment_duration}] * num_segments
        chunk_size = max(1, len(sentences) // num_segments)
        segments = []
        for i in range(num_segments):
            start = i * chunk_size
            end = start + chunk_size if i < num_segments - 1 else len(sentences)
            chunk_text = " ".join(sentences[start:end])
            segments.append({"text": chunk_text, "duration": segment_duration})
        print("Created " + str(len(segments)) + " segments")
        return segments

    def _extract_keywords(self, text):
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "this", "that", "was", "were",
            "been", "have", "has", "had", "will", "would", "could", "should",
            "they", "them", "their", "there", "when", "where", "what", "which",
            "who", "how", "all", "its", "it", "is", "are", "be", "as", "into"
        }
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]
        return " ".join(keywords[:3]) if keywords else "dark mystery"

    def _get_kling_token(self):
        try:
            now = int(time.time())
            payload = {
                "iss": self.kling_access_key,
                "exp": now + 1800,
                "nbf": now - 5
            }
            token = jwt.encode(payload, self.kling_secret_key, algorithm="HS256")
            return token
        except Exception as e:
            print("Kling token error: " + str(e))
            return None

    def _generate_kling_video(self, prompt, save_path):
        try:
            token = self._get_kling_token()
            if not token:
                return False

            headers = {
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json"
            }

            body = {
                "model_name": "kling-v1",
                "prompt": prompt,
                "negative_prompt": "text, watermark, blurry, low quality",
                "cfg_scale": 0.5,
                "mode": "std",
                "duration": "5"
            }

            response = requests.post(
                "https://api.klingai.com/v1/videos/text2video",
                json=body,
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                print("Kling API error: " + str(response.status_code))
                return False

            data = response.json()
            task_id = data.get("data", {}).get("task_id")
            if not task_id:
                return False

            print("Kling task created: " + task_id)

            for attempt in range(30):
                time.sleep(10)
                token = self._get_kling_token()
                headers["Authorization"] = "Bearer " + token
                status_response = requests.get(
                    "https://api.klingai.com/v1/videos/text2video/" + task_id,
                    headers=headers,
                    timeout=15
                )
                status_data = status_response.json()
                task_status = status_data.get("data", {}).get("task_status")

                if task_status == "succeed":
                    videos = status_data.get("data", {}).get("task_result", {}).get("videos", [])
                    if videos:
                        video_url = videos[0].get("url")
                        r = requests.get(video_url, timeout=60, stream=True)
                        with open(save_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                        print("Kling video downloaded")
                        return True
                elif task_status == "failed":
                    print("Kling task failed")
                    return False
                else:
                    print("Kling status: " + str(task_status) + " (attempt " + str(attempt+1) + "/30)")

            return False
        except Exception as e:
            print("Kling error: " + str(e))
            return False

    def _download_clips_for_segments(self, segments):
        clip_paths = []
        used_queries = set()

        for i, segment in enumerate(segments):
            clip_path = os.path.join(self.output_dir, "clip_" + str(i) + ".mp4")
            query = self._extract_keywords(segment["text"])

            if query in used_queries:
                query = query + " cinematic"
            used_queries.add(query)

            kling_prompt = (
                "Cinematic dark mysterious atmosphere, " + segment["text"][:200] +
                ". Dramatic lighting, photorealistic, no text, no watermark."
            )

            print("Segment " + str(i+1) + ": trying Kling AI...")
            if self._generate_kling_video(kling_prompt, clip_path):
                clip_paths.append((clip_path, segment["duration"]))
                continue

            print("Segment " + str(i+1) + ": falling back to Pexels '" + query + "'")
            if self._fetch_pexels_video(query, clip_path):
                clip_paths.append((clip_path, segment["duration"]))
            elif self._fetch_pexels_video("dark mystery night", clip_path):
                clip_paths.append((clip_path, segment["duration"]))

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
        for i, (clip, duration) in enumerate(clip_paths):
            norm_path = os.path.join(self.output_dir, "norm_" + str(i) + ".mp4")
            vf = "scale=1920:1080:force_original_aspect_ratio=decrease,"
            vf += "pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
            cmd = "ffmpeg -y -i " + clip + " -vf \"" + vf + "\""
            cmd += " -c:v libx264 -an -t " + str(int(duration)) + " " + norm_path
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