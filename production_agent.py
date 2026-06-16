import os
import asyncio
import requests
import random
from PIL import Image, ImageDraw


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

    def get_background_music(self):
        try:
            music_path = os.path.join(self.output_dir, "music.mp3")
            urls = [
                "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3",
                "https://audionautix.com/Music/Tense.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dark%20Fog.mp3",
                "https://files.freemusicarchive.org/storage-freemusicarchive-org/music/no_curator/Kevin_MacLeod/Investigations/Kevin_MacLeod_-_Investigations.mp3",
            ]
            for url in urls:
                try:
                    r = requests.get(url, timeout=30, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    })
                    if r.status_code == 200 and len(r.content) > 10000:
                        with open(music_path, "wb") as f:
                            f.write(r.content)
                        print("Background music downloaded: " + str(len(r.content)) + " bytes")
                        return music_path
                    else:
                        print("Music URL failed: " + str(r.status_code))
                except Exception as ex:
                    print("Music URL error: " + str(ex))
                    continue
        except Exception as e:
            print("Music error: " + str(e))
        return None

    def mix_audio_with_music(self, voice_path, music_path, audio_duration):
        try:
            mixed_path = os.path.join(self.output_dir, "mixed_audio.mp3")
            cmd = (
                "ffmpeg -y "
                "-i " + voice_path + " "
                "-stream_loop -1 -i " + music_path + " "
                "-filter_complex \"[1:a]volume=0.08[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=0[out]\" "
                "-map \"[out]\" "
                "-t " + str(int(audio_duration)) + " "
                "-c:a libmp3lame " + mixed_path
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(mixed_path) and os.path.getsize(mixed_path) > 1000:
                print("Music mixed successfully")
                return mixed_path
            print("Music mix failed, using voice only")
        except Exception as e:
            print("Mix error: " + str(e))
        return voice_path

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
            import subprocess
            cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-vf", "subtitles=" + srt_path + ":force_style='" + style + "'",
                "-c:a", "copy", subtitled_path
            ]
            result = subprocess.run(cmd, capture_output=True)
            result = result.returncode
            result = os.system(cmd)
            if result == 0 and os.path.exists(subtitled_path):
                print("Subtitles added")
                return subtitled_path
        except Exception as e:
            print("Subtitle error: " + str(e))
        return video_path

    def add_outro(self, video_path, audio_duration):
        try:
            outro_image_path = os.path.join(self.output_dir, "outro.png")
            outro_video_path = os.path.join(self.output_dir, "outro_clip.mp4")
            final_path = os.path.join(self.output_dir, "final_with_outro.mp4")

            img = Image.new("RGB", (1080, 1920), (0, 0, 0))
            draw = ImageDraw.Draw(img)

            draw.rectangle([0, 0, 1080, 1920], fill=(5, 5, 15))

            for i in range(0, 1920, 4):
                alpha = int(20 * (i / 1920))
                draw.line([(0, i), (1080, i)], fill=(alpha, alpha, alpha+10))

            draw.text((540, 700), "FOLLOW", fill=(255, 50, 50), anchor="mm")
            draw.text((540, 820), "FOR MORE", fill=(255, 255, 255), anchor="mm")
            draw.text((540, 940), "CLASSIFIED", fill=(255, 50, 50), anchor="mm")
            draw.text((540, 1060), "SECRETS", fill=(255, 255, 255), anchor="mm")
            draw.text((540, 1250), "NEW VIDEO", fill=(150, 150, 150), anchor="mm")
            draw.text((540, 1330), "EVERY WEEK", fill=(150, 150, 150), anchor="mm")

            img.save(outro_image_path, "PNG")

            cmd = (
                "ffmpeg -y -loop 1 -i " + outro_image_path +
                " -t 3 -c:v libx264 -vf scale=1080:1920 -pix_fmt yuv420p " +
                outro_video_path
            )
            os.system(cmd)

            if not os.path.exists(outro_video_path):
                return video_path

            concat_file = os.path.join(self.output_dir, "final_concat.txt")
            with open(concat_file, "w") as f:
                f.write("file '" + os.path.abspath(video_path) + "'\n")
                f.write("file '" + os.path.abspath(outro_video_path) + "'\n")

            cmd = (
                "ffmpeg -y -f concat -safe 0 -i " + concat_file +
                " -c copy " + final_path
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(final_path):
                print("Outro added")
                return final_path

        except Exception as e:
            print("Outro error: " + str(e))
        return video_path

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
