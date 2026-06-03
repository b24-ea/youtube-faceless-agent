import os
import asyncio
import requests
import edge_tts
import re


class ProductionAgent:
    def __init__(self):
        self.output_dir = "output"
        self.voice = "en-US-AriaNeural"
        self.pexels_api_key = os.environ.get("PEXELS_API_KEY")
        self.elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        os.makedirs(self.output_dir, exist_ok=True)

    def create_video(self, video_data):
        audio_path = self._generate_audio(video_data["script"])
        audio_duration = self._get_audio_duration(audio_path)
        segments = self._split_script_to_segments(video_data["script"], audio_duration)
        dalle_prompts = video_data.get("dalle_prompts", [])
        clip_paths = self._download_clips_for_segments(segments, dalle_prompts)
        video_path = self._combine_to_video(audio_path, clip_paths, audio_duration)
        return video_path

    def _generate_audio(self, script):
        if isinstance(script, dict):
            script = " ".join([str(v) for v in script.values()])
        script = str(script)[:4500]
        audio_path = os.path.join(self.output_dir, "audio.mp3")
        try:
            url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"
            headers = {"xi-api-key": self.elevenlabs_api_key, "Content-Type": "application/json"}
            body = {
                "text": script,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.5, "use_speaker_boost": True}
            }
            response = requests.post(url, json=body, headers=headers, timeout=60)
            if response.status_code == 200:
                with open(audio_path, "wb") as f:
                    f.write(response.content)
                print("ElevenLabs audio generated")
                return audio_path
            else:
                print("ElevenLabs error: " + str(response.status_code))
        except Exception as e:
            print("ElevenLabs error: " + str(e))
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            response = client.audio.speech.create(model="tts-1-hd", voice="onyx", input=script)
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
        if not sentences:
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
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "this", "that", "was", "were", "been", "have", "has", "had", "will", "would", "could", "should", "they", "them", "their", "there", "when", "where", "what", "which", "who", "how", "all", "its", "it", "is", "are", "be", "as", "into"}
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]
        return " ".join(keywords[:3]) if keywords else "dark mystery"

    def _generate_dalle_image(self, prompt, save_path):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            full_prompt = "Cinematic horror atmosphere, dark and scary, " + prompt + ". No text, no watermarks, photorealistic, dramatic lighting."
            response = client.images.generate(model="dall-e-3", prompt=full_prompt, size="1792x1024", quality="standard", n=1)
            image_url = response.data[0].url
            r = requests.get(image_url, timeout=30)
            with open(save_path, "wb") as f:
                f.write(r.content)
            video_path = save_path.replace(".jpg", ".mp4")
            cmd = "ffmpeg -y -loop 1 -i " + save_path + " -t 10 -c:v libx264 -vf scale=1920:1080 " + video_path
            os.system(cmd)
            if os.path.exists(video_path):
                print("DALL-E image created")
                return video_path
        except Exception as e:
            print("DALL-E error: " + str(e))
        return None

    def _download_clips_for_segments(self, segments, dalle_prompts):
        clip_paths = []
        used_queries = set()
        dalle_index = 0
        for i, segment in enumerate(segments):
            clip_path_base = os.path.join(self.output_dir, "clip_" + str(i))
            clip_path_mp4 = clip_path_base + ".mp4"
            if i % 2 == 1 and dalle_index < len(dalle_prompts):
                dalle_clip = self._generate_dalle_image(dalle_prompts[dalle_index], clip_path_base + ".jpg")
                dalle_index += 1
                if dalle_clip:
                    clip_paths.append((dalle_clip, segment["duration"]))
                    continue
            query = self._extract_keywords(segment["text"])
            if query in used_queries:
                query = query + " horror"
            used_queries.add(query)
            print("Segment " + str(i+1) + ": Pexels '" + query + "'")
            if self._fetch_pexels_video(query, clip_path_mp4):
                clip_paths.append((clip_path_mp4, segment["duration"]))
            elif self._fetch_pexels_video("dark scary night", clip_path_mp4):
                clip_paths.append((clip_path_mp4, segment["duration"]))
        return clip_paths

    def _fetch_pexels_video(self, query, save_path):
        try:
            headers = {"Authorization": self.pexels_api_key}
            params = {"query": query, "per_page": 5, "orientation": "landscape"}
            response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=15)
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

    def _combine_to_video(self, audio_path, clip_paths, audio_duration=180):
        if not clip_paths:
            return None
        video_path = os.path.join(self.output_dir, "final_video.mp4")
        normalized = []
        num_clips = len(clip_paths)
        duration_per_clip = max(5, int(audio_duration / num_clips))
        print("Clips: " + str(num_clips) + ", duration each: " + str(duration_per_clip) + "s")
        for i, (clip, duration) in enumerate(clip_paths):
            norm_path = os.path.join(self.output_dir, "norm_" + str(i) + ".mp4")
            vf = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
            cmd = "ffmpeg -y -i " + clip + " -vf \"" + vf + "\" -c:v libx264 -an -t " + str(duration_per_clip) + " " + norm_path
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
        os.system("ffmpeg -y -f concat -safe 0 -i " + concat_file + " -c copy " + merged_path)
        cmd = "ffmpeg -y -i " + merged_path + " -i " + audio_path + " -map 0:v -map 1:a -c:v copy -c:a aac -t " + str(int(audio_duration)) + " " + video_path
        os.system(cmd)
        if os.path.exists(video_path):
            return video_path
        return None