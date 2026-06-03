import os
import asyncio
import requests
import edge_tts
import re
import random


ELEVENLABS_VOICES = [
    {"id": "N2lVS1w4EtoT3dr4eOWO", "name": "Callum"},
    {"id": "IKne3meq5aSn9XLyUdCD", "name": "Charlie"},
    {"id": "2EiwWnXFnvU5JabPnv8n", "name": "Clyde"},
    {"id": "jsCqWAovK2LkecY7zXl4", "name": "Freya"},
]


class ProductionAgent:
    def __init__(self):
        self.output_dir = "output"
        self.voice = "en-US-AriaNeural"
        self.pixabay_api_key = os.environ.get("PIXABAY_API_KEY")
        self.elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        os.makedirs(self.output_dir, exist_ok=True)

    def create_video(self, video_data, is_shorts=False):
        max_duration = 48 if is_shorts else 240
        audio_path = self._generate_audio(video_data["script"], max_duration)
        audio_duration = self._get_audio_duration(audio_path)
        audio_duration = min(audio_duration, max_duration)
        print("Final duration: " + str(round(audio_duration, 1)) + "s")
        music_path = self._get_background_music()
        segments = self._split_script_to_segments(video_data["script"], audio_duration)
        clip_paths = self._download_clips_for_segments(segments)
        video_path = self._combine_to_video(audio_path, clip_paths, audio_duration, is_shorts, music_path)
        return video_path

    def _generate_audio(self, script, max_duration=240):
        if isinstance(script, dict):
            script = " ".join([str(v) for v in script.values()])
        script = str(script)
        max_words = int(max_duration * 2.5)
        words = script.split()
        if len(words) > max_words:
            script = " ".join(words[:max_words])
        audio_path = os.path.join(self.output_dir, "audio.mp3")
        voice = random.choice(ELEVENLABS_VOICES)
        print("Using voice: " + voice["name"])
        try:
            url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice["id"]
            headers = {"xi-api-key": self.elevenlabs_api_key, "Content-Type": "application/json"}
            body = {
                "text": script,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.7, "use_speaker_boost": True}
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
            response = client.audio.speech.create(model="tts-1-hd", voice="nova", input=script)
            response.stream_to_file(audio_path)
            print("OpenAI TTS fallback used")
            return audio_path
        except Exception as e:
            print("OpenAI TTS error: " + str(e))
        async def _tts():
            communicate = edge_tts.Communicate(script, "en-US-JennyNeural")
            await communicate.save(audio_path)
        asyncio.run(_tts())
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

    def _get_background_music(self):
        try:
            music_path = os.path.join(self.output_dir, "music.mp3")
            urls = [
                "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0c6ff3a5b.mp3",
                "https://cdn.pixabay.com/download/audio/2021/11/25/audio_5bdf8a4a6f.mp3",
                "https://cdn.pixabay.com/download/audio/2022/03/15/audio_1e6ede8a71.mp3",
            ]
            for url in urls:
                try:
                    r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
                    if r.status_code == 200 and len(r.content) > 10000:
                        with open(music_path, "wb") as f:
                            f.write(r.content)
                        print("Background music downloaded")
                        return music_path
                except Exception:
                    continue
        except Exception as e:
            print("Music error: " + str(e))
        return None

    def _split_script_to_segments(self, script, audio_duration):
        if isinstance(script, dict):
            script = " ".join([str(v) for v in script.values()])
        script = str(script)
        sentences = re.split(r'(?<=[.!?])\s+', script)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        segment_duration = 4.0
        num_segments = max(3, int(audio_duration / segment_duration))
        print("Target segments: " + str(num_segments) + " (every 4s)")
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
        return " ".join(keywords[:3]) if keywords else "funny animals"

    def _fetch_pixabay_video(self, query, save_path, used_ids=None):
        try:
            params = {
                "key": self.pixabay_api_key,
                "q": query,
                "video_type": "film",
                "per_page": 10,
                "safesearch": "true",
                "order": "popular"
            }
            response = requests.get("https://pixabay.com/api/videos/", params=params, timeout=15)
            data = response.json()
            videos = data.get("hits", [])
            if not videos:
                return False
            selected = None
            for video in videos:
                vid_id = video.get("id")
                if used_ids is not None and vid_id in used_ids:
                    continue
                selected = video
                if used_ids is not None:
                    used_ids.add(vid_id)
                break
            if not selected:
                selected = videos[0]
            video_files = selected.get("videos", {})
            url = None
            for quality in ["large", "medium", "small", "tiny"]:
                if quality in video_files and video_files[quality].get("url"):
                    url = video_files[quality]["url"]
                    break
            if not url:
                return False
            r = requests.get(url, timeout=60, stream=True)
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print("Pixabay error: " + str(e))
            return False

    def _download_clips_for_segments(self, segments):
        clip_paths = []
        used_video_ids = set()
        fallbacks = ["funny animals", "cute animals playing", "kids laughing", "colorful nature", "funny cats", "baby animals"]
        fallback_index = 0
        for i, segment in enumerate(segments):
            clip_path = os.path.join(self.output_dir, "clip_" + str(i) + ".mp4")
            query = self._extract_keywords(segment["text"])
            print("Segment " + str(i+1) + ": searching '" + query + "'")
            success = self._fetch_pixabay_video(query, clip_path, used_video_ids)
            if not success:
                fallback = fallbacks[fallback_index % len(fallbacks)]
                fallback_index += 1
                success = self._fetch_pixabay_video(fallback, clip_path, used_video_ids)
            if success:
                clip_paths.append((clip_path, segment["duration"]))
        return clip_paths

    def _combine_to_video(self, audio_path, clip_paths, audio_duration=180, is_shorts=False, music_path=None):
        if not clip_paths:
            return None
        video_path = os.path.join(self.output_dir, "final_video.mp4")
        normalized = []
        num_clips = len(clip_paths)
        duration_per_clip = max(4, int(audio_duration / num_clips))
        print("Clips: " + str(num_clips) + ", duration each: " + str(duration_per_clip) + "s")
        width = "1080" if is_shorts else "1920"
        height = "1920" if is_shorts else "1080"
        for i, (clip, duration) in enumerate(clip_paths):
            norm_path = os.path.join(self.output_dir, "norm_" + str(i) + ".mp4")
            vf = "scale=" + width + ":" + height + ":force_original_aspect_ratio=decrease,"
            vf += "pad=" + width + ":" + height + ":(ow-iw)/2:(oh-ih)/2"
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
        if music_path and os.path.exists(music_path):
            mixed_audio = os.path.join(self.output_dir, "mixed.mp3")
            cmd = (
                "ffmpeg -y -i " + audio_path + " -i " + music_path +
                " -filter_complex \"[1:a]volume=0.12,aloop=loop=-1:size=2e+09[bg];"
                "[0:a][bg]amix=inputs=2:duration=first[out]\" "
                "-map \"[out]\" -t " + str(int(audio_duration)) + " " + mixed_audio
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(mixed_audio):
                audio_path = mixed_audio
                print("Music mixed successfully")
            else:
                print("Music mix failed, using voice only")
        cmd = "ffmpeg -y -i " + merged_path + " -i " + audio_path + " -map 0:v -map 1:a -c:v copy -c:a aac -t " + str(int(audio_duration)) + " " + video_path
        os.system(cmd)
        if os.path.exists(video_path):
            return video_path
        return None
