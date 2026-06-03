import os
import asyncio
import requests
import edge_tts
import re
import random
import fal_client


ELEVENLABS_VOICES = [
    {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel"},
    {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi"},
    {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella"},
    {"id": "ErXwobaYiN019PkySvjV", "name": "Antoni"},
]


class ProductionAgent:
    def __init__(self):
        self.output_dir = "output"
        self.pixabay_api_key = os.environ.get("PIXABAY_API_KEY")
        self.elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        fal_key = os.environ.get("FAL_API_KEY", "")
        os.environ["FAL_KEY"] = fal_key
        os.makedirs(self.output_dir, exist_ok=True)

    def create_video(self, video_data, is_shorts=False):
        max_duration = 48 if is_shorts else 240
        audio_path = self._generate_audio(video_data["script"], max_duration)
        audio_duration = self._get_audio_duration(audio_path)
        audio_duration = min(audio_duration, max_duration)
        print("Final duration: " + str(round(audio_duration, 1)) + "s")
        music_path = self._get_background_music()
        clip_duration = 3
        num_clips = max(3, int(audio_duration / clip_duration))
        max_hailuo = 8 if is_shorts else 30
        print("Need " + str(num_clips) + " clips, Hailuo max: " + str(max_hailuo))
        segments = self._split_script_to_segments(video_data["script"], num_clips, clip_duration)
        clip_paths = self._download_clips_for_segments(segments, max_hailuo, is_shorts)
        video_path = self._combine_to_video(audio_path, clip_paths, audio_duration, is_shorts, music_path, clip_duration)
        if video_path and os.path.exists(video_path):
            video_path = self._add_subtitles(video_path, video_data["script"], audio_duration, is_shorts)
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
            body = {"text": script, "model_id": "eleven_turbo_v2_5", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.7, "use_speaker_boost": True}}
            response = requests.post(url, json=body, headers=headers, timeout=60)
            if response.status_code == 200:
                with open(audio_path, "wb") as f:
                    f.write(response.content)
                print("ElevenLabs audio generated")
                return audio_path
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
            result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path], capture_output=True, text=True)
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
                        print("Background music downloaded: " + str(len(r.content)) + " bytes")
                        return music_path
                except Exception as ex:
                    print("Music URL failed: " + str(ex))
                    continue
        except Exception as e:
            print("Music error: " + str(e))
        return None

    def _split_script_to_segments(self, script, num_clips, clip_duration):
        if isinstance(script, dict):
            script = " ".join([str(v) for v in script.values()])
        script = str(script)
        sentences = re.split(r'(?<=[.!?])\s+', script)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        if not sentences:
            return [{"text": script, "duration": clip_duration}] * num_clips
        chunk_size = max(1, len(sentences) // num_clips)
        segments = []
        for i in range(num_clips):
            start = i * chunk_size
            end = start + chunk_size if i < num_clips - 1 else len(sentences)
            segments.append({"text": " ".join(sentences[start:end]), "duration": clip_duration})
        print("Created " + str(len(segments)) + " segments of " + str(clip_duration) + "s each")
        return segments

    def _extract_keywords(self, text):
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "this", "that", "was", "were", "been", "have", "has", "had", "will", "would", "could", "should", "they", "them", "their", "there", "when", "where", "what", "which", "who", "how", "all", "its", "it", "is", "are", "be", "as", "into"}
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]
        return " ".join(keywords[:4]) if keywords else "dark mystery"

    def _generate_hailuo_anime_clip(self, prompt, save_path, is_shorts=False):
        try:
            print("  Hailuo generating: " + prompt[:50])
            style = "dark mysterious cinematic style, paranormal atmosphere, dramatic lighting, "
            anime_prompt = style + prompt + ". High quality, smooth motion, no text, no watermark."
            result = fal_client.subscribe(
                "fal-ai/minimax/hailuo-02/standard/text-to-video",
                arguments={"prompt": anime_prompt, "duration": 6, "resolution": "768p"}
            )
            if result and result.get("video", {}).get("url"):
                video_url = result["video"]["url"]
                r = requests.get(video_url, timeout=120, stream=True)
                with open(save_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("  Hailuo clip ready")
                return True
        except Exception as e:
            print("  Hailuo error: " + str(e))
        return False

    def _fetch_pixabay_video(self, query, save_path, used_ids=None):
        try:
            for video_type in ["animation", "film"]:
                params = {"key": self.pixabay_api_key, "q": query, "video_type": video_type, "per_page": 10, "safesearch": "true", "order": "popular"}
                response = requests.get("https://pixabay.com/api/videos/", params=params, timeout=15)
                data = response.json()
                videos = data.get("hits", [])
                if videos:
                    break
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

    def _download_clips_for_segments(self, segments, max_hailuo=30, is_shorts=False):
        clip_paths = []
        used_video_ids = set()
        fallbacks = ["dark mystery forest", "abandoned building", "foggy road night", "dramatic storm", "dark corridor"]
        fallback_index = 0
        hailuo_count = 0
        for i, segment in enumerate(segments):
            clip_path = os.path.join(self.output_dir, "clip_" + str(i) + ".mp4")
            query = self._extract_keywords(segment["text"])
            success = False
            if hailuo_count < max_hailuo:
                success = self._generate_hailuo_anime_clip(query, clip_path, is_shorts)
                if success:
                    hailuo_count += 1
            if not success:
                print("Segment " + str(i+1) + ": Pixabay '" + query + "'")
                success = self._fetch_pixabay_video(query, clip_path, used_video_ids)
            if not success:
                fallback = fallbacks[fallback_index % len(fallbacks)]
                fallback_index += 1
                success = self._fetch_pixabay_video(fallback, clip_path, used_video_ids)
            if success:
                clip_paths.append((clip_path, segment["duration"]))
        print("Total clips: " + str(len(clip_paths)) + " (Hailuo: " + str(hailuo_count) + ")")
        return clip_paths

    def _add_subtitles(self, video_path, script, audio_duration, is_shorts=False):
        try:
            if isinstance(script, dict):
                script = " ".join([str(v) for v in script.values()])
            script = str(script)
            words = script.split()
            if not words:
                return video_path
            srt_path = os.path.join(self.output_dir, "subtitles.srt")
            words_per_second = len(words) / audio_duration
            chunk_size = max(1, int(words_per_second * 3))
            chunks = []
            for i in range(0, len(words), chunk_size):
                chunks.append(" ".join(words[i:i+chunk_size]))
            time_per_chunk = audio_duration / len(chunks)
            with open(srt_path, "w") as f:
                for i, chunk in enumerate(chunks):
                    start = i * time_per_chunk
                    end = (i + 1) * time_per_chunk
                    def fmt(t):
                        h = int(t // 3600)
                        m = int((t % 3600) // 60)
                        s = int(t % 60)
                        ms = int((t - int(t)) * 1000)
                        return str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2) + "," + str(ms).zfill(3)
                    f.write(str(i+1) + "\n")
                    f.write(fmt(start) + " --> " + fmt(end) + "\n")
                    f.write(chunk + "\n\n")
            subtitled_path = os.path.join(self.output_dir, "final_subtitled.mp4")
            font_size = "18" if is_shorts else "24"
            margin = "60" if is_shorts else "40"
            cmd = (
                "ffmpeg -y -i " + video_path + " "
                "-vf \"subtitles=" + srt_path + ":force_style='FontSize=" + font_size + ",PrimaryColour=&Hffffff,OutlineColour=&H000000,Outline=2,Bold=1,MarginV=" + margin + "'\" "
                "-c:a copy " + subtitled_path
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(subtitled_path):
                print("Subtitles added")
                return subtitled_path
            print("Subtitle failed, using video without subtitles")
            return video_path
        except Exception as e:
            print("Subtitle error: " + str(e))
            return video_path

    def _combine_to_video(self, audio_path, clip_paths, audio_duration=180, is_shorts=False, music_path=None, clip_duration=3):
        if not clip_paths:
            return None
        video_path = os.path.join(self.output_dir, "final_video.mp4")
        normalized = []
        num_clips = len(clip_paths)
        duration_per_clip = max(3, int(audio_duration / num_clips))
        print("Clips: " + str(num_clips) + ", duration each: " + str(duration_per_clip) + "s")
        if is_shorts:
            width = "1080"
            height = "1920"
        else:
            width = "1920"
            height = "1080"
        for i, (clip, duration) in enumerate(clip_paths):
            norm_path = os.path.join(self.output_dir, "norm_" + str(i) + ".mp4")
            if is_shorts:
                vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
            else:
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
        if music_path and os.path.exists(music_path):
            mixed_audio = os.path.join(self.output_dir, "mixed.mp3")
            cmd = (
                "ffmpeg -y "
                "-i " + audio_path + " "
                "-stream_loop -1 -i " + music_path + " "
                "-filter_complex \"[1:a]volume=0.10[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=0[out]\" "
                "-map \"[out]\" "
                "-t " + str(int(audio_duration)) + " "
                "-c:a libmp3lame " + mixed_audio
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(mixed_audio) and os.path.getsize(mixed_audio) > 1000:
                audio_path = mixed_audio
                print("Music mixed successfully")
            else:
                print("Music mix failed, using voice only")
        cmd = "ffmpeg -y -i " + merged_path + " -i " + audio_path + " -map 0:v -map 1:a -c:v copy -c:a aac -t " + str(int(audio_duration)) + " " + video_path
        os.system(cmd)
        if os.path.exists(video_path):
            return video_path
        return None
