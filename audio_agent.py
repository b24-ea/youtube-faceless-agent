import os
import json
import requests


class AudioAgent:
    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        self.api_key = os.environ.get("ELEVENLABS_API_KEY", "")
        # Adam - stabil, derin, otoriter erkek sesi (her hesapta varsayılan olarak bulunur)
        self.voice_id = "pNInz6obpgDQGcFmaJgB"

    def generate_voiceover(self, script_text):
        """
        ElevenLabs ile ses üretir ve kelime kelime zamanlama bilgisi döner.
        Returns: (audio_path, duration_seconds, word_timings) ya da (None, 0, [])
        """
        try:
            audio_path = os.path.join(self.output_dir, "voiceover.mp3")
            url = "https://api.elevenlabs.io/v1/text-to-speech/" + self.voice_id + "/with-timestamps"

            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            body = {
                "text": script_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.65,
                    "similarity_boost": 0.75,
                    "style": 0.4,
                    "use_speaker_boost": True
                }
            }

            r = requests.post(url, headers=headers, json=body, timeout=60)
            if r.status_code != 200:
                print("ElevenLabs error: " + str(r.status_code) + " " + r.text[:200])
                return None, 0, []

            data = r.json()
            import base64
            audio_bytes = base64.b64decode(data["audio_base64"])
            with open(audio_path, "wb") as f:
                f.write(audio_bytes)

            alignment = data.get("alignment", {})
            word_timings = self._build_word_timings(alignment)

            duration = 0
            if word_timings:
                duration = word_timings[-1]["end"]
            else:
                duration = self._get_audio_duration(audio_path)

            print("Voiceover generated: " + str(round(duration, 1)) + "s, " + str(len(word_timings)) + " words")
            return audio_path, duration, word_timings

        except Exception as e:
            print("Audio generation error: " + str(e))
            return None, 0, []

    def _build_word_timings(self, alignment):
        """ElevenLabs karakter bazlı zamanlamasını kelime bazlı zamanlamaya çevirir"""
        try:
            chars = alignment.get("characters", [])
            starts = alignment.get("character_start_times_seconds", [])
            ends = alignment.get("character_end_times_seconds", [])

            if not chars or not starts or not ends:
                return []

            words = []
            current_word = ""
            word_start = None

            for i, ch in enumerate(chars):
                if ch.strip() == "":
                    if current_word:
                        words.append({
                            "word": current_word,
                            "start": word_start,
                            "end": ends[i - 1] if i > 0 else starts[i]
                        })
                        current_word = ""
                        word_start = None
                else:
                    if word_start is None:
                        word_start = starts[i]
                    current_word += ch

            if current_word:
                words.append({
                    "word": current_word,
                    "start": word_start,
                    "end": ends[-1]
                })

            return words
        except Exception as e:
            print("Word timing build error: " + str(e))
            return []

    def _get_audio_duration(self, audio_path):
        try:
            import subprocess
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                capture_output=True, text=True
            )
            return float(result.stdout.strip())
        except Exception as e:
            print("Duration probe error: " + str(e))
            return 30.0
