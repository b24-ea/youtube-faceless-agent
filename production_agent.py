import os
import asyncio
import subprocess
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import textwrap

class ProductionAgent:
    def __init__(self):
        self.output_dir = "output"
        self.voice = "en-US-AriaNeural"  # Microsoft ücretsiz ses
        os.makedirs(self.output_dir, exist_ok=True)

    def create_video(self, video_data: dict) -> str:
        print("  🎙️  Seslendirme üretiliyor...")
        audio_path = self._generate_audio(video_data["script"])
        
        print("  🖼️  Görseller üretiliyor...")
        image_paths = self._generate_images(video_data["visual_descriptions"])
        
        print("  🎬 Video birleştiriliyor...")
        video_path = self._combine_to_video(audio_path, image_paths, video_data)
        
        return video_path

    def _generate_audio(self, script: str) -> str:
        # Script'i temizle
        if isinstance(script, dict):
            script = " ".join([str(v) for v in script.values()])
        
        audio_path = f"{self.output_dir}/audio.mp3"
        
        async def _tts():
            communicate = edge_tts.Communicate(script, self.voice)
            await communicate.save(audio_path)
        
        asyncio.run(_tts())
        return audio_path

    def _generate_images(self, visual_descriptions: list) -> list:
        image_paths = []
        
        for i, description in enumerate(visual_descriptions[:8]):  # Max 8 görsel
            img_path = f"{self.output_dir}/frame_{i}.png"
            self._create_placeholder_image(description, img_path, i)
            image_paths.append(img_path)
        
        return image_paths

    def _create_placeholder_image(self, description: str, path: str, index: int):
        # Karanlık, dramatik arka plan
        colors = [
            (10, 10, 30),    # Koyu mavi-siyah
            (20, 5, 5),      # Koyu kırmızı-siyah
            (5, 20, 5),      # Koyu yeşil-siyah
            (15, 15, 15),    # Koyu gri
        ]
        bg_color = colors[index % len(colors)]
        
        img = Image.new('RGB', (1920, 1080), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Metin ekle
        wrapped = textwrap.fill(description, width=40)
        draw.text((960, 540), wrapped, fill=(200, 200, 200), anchor="mm")
        
        img.save(path)

    def _combine_to_video(self, audio_path: str, image_paths: list, video_data: dict) -> str:
        video_path = f"{self.output_dir}/final_video.mp4"
        
        # Her görsel için süre hesapla (ses süresine böl)
        duration_per_image = 30  # saniye (sonra dinamik yapacağız)
        
        # FFmpeg ile video oluştur
        inputs = ""
        for img in image_paths:
            inputs += f"-loop 1 -t {duration_per_image} -i {img} "
        
        filter_complex = ""
        for i in range(len(image_paths)):
            filter_complex += f"[{i}:v]scale=1920:1080,setsar=1[v{i}];"
        
        concat_inputs = "".join([f"[v{i}]" for i in range(len(image_paths))])
        filter_complex += f"{concat_inputs}concat=n={len(image_paths)}:v=1:a=0[outv]"
        
        cmd = (
            f"ffmpeg -y {inputs} "
            f"-i {audio_path} "
            f'-filter_complex "{filter_complex}" '
            f"-map [outv] -map {len(image_paths)}:a "
            f"-c:v libx264 -c:a aac -shortest {video_path}"
        )
        
        os.system(cmd)
        return video_path
