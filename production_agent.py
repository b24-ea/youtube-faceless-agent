import os
import asyncio
import requests
import random


ELEVENLABS_VOICES = [
    {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh"},
    {"id": "VR6AewLTigWG4xSOukaG", "name": "Arnold"},
    {"id": "pqHfZKP75CvOlQylNhV4", "name": "Bill"},
    {"id": "nPczCjzI2devNBz1zQrb", "name": "Brian"},
]


class ProductionAgent:
    def __init__(self):
        self.output_dir = "output"
        self.elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_audio(self, script_data):
        script = self._build_full_script(script_data)
        print("Generating audio...")
        audio_path = os.path.join(self.output_dir, "audio.mp3")
        voice = random.choice(ELEVENLABS_VOICES)
        print("Using voice: " + voice["name"])
        try:
            url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice["id"]
            headers = {
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            body = {
                "text": script,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {
                    "stability": 0.35,
                    "similarity_boost": 0.85,
                    "style": 0.6,
                    "use_speaker_boost": True
                }
            }
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
        return None

    def add_audio_to_video(self, video_path, audio_path):
        try:
            output_path = os.path.join(self.output_dir, "final_with_audio.mp4")
            cmd = (
                "ffmpeg -y -i " + video_path +
                " -i " + audio_path +
                " -map 0:v -map 1:a -c:v copy -c:a aac -shortest " +
                output_path
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(output_path):
                print("Audio added to video")
                return output_path
        except Exception as e:
            print("Audio merge error: " + str(e))
        return video_path

    def add_subtitles(self, video_path, script_data, audio_duration):
        try:
            script = self._build_full_script(script_data)
            words = script.split()
            if not words:
                return video_path

            srt_path = os.path.join(self.output_dir, "subtitles.srt")
            words_per_second = len(words) / audio_duration
            chunk_size = max(1, int(words_per_second * 1.5))
            chunks = []
            for i in range(0, len(words), chunk_size):
                chunk = words[i:i+chunk_size]
                chunks.append(" ".join(chunk))

            time_per_chunk = audio_duration / len(chunks)

            with open(srt_path, "w", encoding="utf-8") as f:
                for i, chunk in enumerate(chunks):
                    start = i * time_per_chunk
                    end = (i + 1) * time_per_chunk
                    words_in_chunk = chunk.split()
                    if len(words_in_chunk) > 1:
                        mid = len(words_in_chunk) // 2
                        first = " ".join(words_in_chunk[:mid]).upper()
                        last = " ".join(words_in_chunk[mid:]).upper()
                        styled = first + " <font color='#FFFF00'>" + last + "</font>"
                    else:
                        styled = "<font color='#FFFF00'>" + chunk.upper() + "</font>"
                    f.write(str(i+1) + "\n")
                    f.write(self._fmt_time(start) + " --> " + self._fmt_time(end) + "\n")
                    f.write(styled + "\n\n")

            subtitled_path = os.path.join(self.output_dir, "final_subtitled.mp4")
            style = (
                "FontName=Impact,"
                "FontSize=24,"
                "PrimaryColour=&H00FFFFFF,"
                "SecondaryColour=&H0000FFFF,"
                "OutlineColour=&H00000000,"
                "BackColour=&H00000000,"
                "Bold=1,"
                "Outline=4,"
                "Shadow=2,"
                "Alignment=2,"
                "MarginV=200"
            )
            cmd = (
                "ffmpeg -y -i " + video_path +
                " -vf \"subtitles=" + srt_path +
                ":force_style='" + style + "'\" " +
                "-c:a copy " + subtitled_path
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(subtitled_path):
                print("Subtitles added")
                ret

    def get_audio_duration(self, audio_path):
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
            return 50.0

    def _build_full_script(self, script_data):
        if isinstance(script_data, str):
            return script_data
        if isinstance(script_data, dict):
            parts = []
            for key in ["hook", "story", "details", "climax", "cliffhanger"]:
                if key in script_data:
                    parts.append(str(script_data[key]))
            return " ".join(parts)
        return str(script_data)

    def _fmt_time(self, t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int((t - int(t)) * 1000)
        return (str(h).zfill(2) + ":" + str(m).zfill(2) + ":" +
                str(s).zfill(2) + "," + str(ms).zfill(3))
