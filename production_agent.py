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
        print("  Generating voiceover...")
        audio_path = self._generate_audio(video_data["script"])

        print("  Downloading stock video clips...")
        clip_paths = self._download_video_clips(video_data["visual_descriptions"])

        print("  Combining video...")
        video_path = self._combine_to_video(audio_path, clip_paths)

        return video_path

    def _generate_audio(self, script):
        if isinstance(script, dict):
            script = " ".join([str(v) for v in script.values()])
        script = str(script)[:4500]
        audio_path = os.path.join(self.output_dir, "audio.mp3")

        async def _tts():
            communicate = edge_tts.Communicate(script, self.voice)
            await communicate.save(audio_path)

        asyncio.run(_tts())
        return audio_path

    def _download_video_clips(self, visual_descriptions):
        clip_paths = []
        fallback_queries = [
            "dark mystery forest",
            "abandoned building night",
            "foggy road night",
            "dramatic storm sky",
            "empty dark corridor",
            "old newspaper documents"
        ]

        queries = []
        for desc in visual_descriptions[:4]:
            words = [w for w in str(desc).lower().split() if len(w) > 4][:3]
            queries.append(" ".join(words) if words else "dark mystery")
        queries += fallback_queries[:2]

        for i, query in enumerate(queries[:6]):
