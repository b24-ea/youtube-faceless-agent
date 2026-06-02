import os
import asyncio
import requests
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
from openai import OpenAI


class ProductionAgent:
    def __init__(self):
        self.output_dir = "output"
        self.voice = "en-US-AriaNeural"
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        os.makedirs(self.output_dir, exist_ok=True)

    def create_video(self, video_data: dict) -> str:
        print("  🎙️  Generating voiceover...")
        audio_path = self._generate_audio(video_data["script"])

        print("  🖼️  Generating AI images with DALL-E 3...")
        image_paths = self._generate_images(video_data["visual_descriptions"], video_data["title"])

        print("  🎬 Combining video...")
        video_path = self._combine_to_video(audio_path, image_paths, video_data)

        return video_path

    def _generate_audio(self, script: str) -> str:
        if isinstance(script, dict):
            script = " ".join([str(v) for v in script.values()])

        script = str(script)[:4000]
        audio_path = f"{self.output_dir}/audio.mp3"

        async def _tts():
            communicate = edge_tts.Communicate(script, self.voice)
            await communicate.save(audio_path)

        asyncio.run(_tts())
        return audio_path

    def _generate_images(self, visual_descriptions: list, title: str) -> list:
        image_paths = []

        for i, description in enumerate(visual_descriptions[:4]):
            img_path = f"{self.output_dir}/frame_{i}.png"
            try:
                print(f"    🎨 Generating image {i+1}/4...")
                
                dalle_prompt = (
                    f"Cinematic, dark and mysterious atmosphere. "
                    f"{description}. "
                    f"High quality, dramatic lighting, photorealistic, "
                    f"documentary style, no text, no watermarks."
                )

                response = self.openai_client.images.generate(
                    model="gpt-image-1",
                    prompt=dalle_prompt,
                    size="1792x1024",
                    quality="standard",
                    n=1
                )

                image_url = response.data[0].url
                img_response = requests.get(image_url)
                img = Image.open(BytesIO(img_response.content))
                img = img.resize((1920, 1080), Image.LANCZOS)
                img.save(img_path)
                print(f"    ✅ Image {i+1} generated")

            except Exception as e:
                print(f"    ⚠️  DALL-E failed for image {i+1}: {e}, using fallback")
                self._create_fallback_image(description, img_path, i)

            image_paths.append(img_path)

        return image_paths

    def _create_fallback_image(self, description: str, path: str, index: int):
        colors = [(10, 10, 30), (20, 5, 5), (5, 20, 5), (15, 15, 15)]
        bg_color = colors[index % len(colors)]
        img = Image.new("RGB", (1920, 1080), bg_color)
        draw = ImageDraw.Draw(img)
        wrapped = textwrap.fill(description, width=50)
        draw.text((960, 540), wrapped, fill=(200, 200, 200), anchor="mm")
        img.save(path)

    def _combine_to_video(self, audio_path: str, image_paths: list, video_data: dict) -> str:
        video_path = f"{self.output_dir}/final_video.mp4"
        duration_per_image = 30
        n = len(image_paths)

        inputs = " ".join([f"-loop 1 -t {duration_per_image} -i {p}" for p in image_paths])
        filter_parts = "".join([f"[{i}:v]scale=1920:1080,setsar=1[v{i}];" for i in range(n)])
        concat_inputs = "".join([f"[v{i}]" for i in range(n)])
        filter_complex = f"{filter_parts}{concat_inputs}concat=n={n}:v=1:a=0[outv]"

        cmd = (
            f"ffmpeg -y {inputs} "
            f"-i {audio_path} "
            f'-filter_complex "{filter_complex}" '
            f"-map [outv] -map {n}:a "
            f"-c:v libx264 -c:a aac -shortest {video_path}"
        )

        os.system(cmd)
        return video_path
