import os
import requests
import fal_client
from PIL import Image
from io import BytesIO
import random


class VideoGenerator:
    def __init__(self):
        self.output_dir = "output"
        fal_key = os.environ.get("FAL_API_KEY", "")
        os.environ["FAL_KEY"] = fal_key
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, video_data):
        visuals = video_data.get("visuals", [])
        if not visuals:
            print("No visuals found")
            return None

        clip_paths = []
        for i, visual in enumerate(visuals):
            visual_type = visual.get("type", "FLUX")
            prompt = visual.get("prompt", "dark cinematic scene")
            duration = visual.get("duration", 3)
            clip_path = os.path.join(self.output_dir, "clip_" + str(i) + ".mp4")

            print("Visual " + str(i+1) + "/" + str(len(visuals)) + " [" + visual_type + "]: " + prompt[:60])

            if visual_type == "VEO":
                success = self._generate_veo_clip(prompt, clip_path, duration)
            else:
                success = self._generate_flux_image(prompt, clip_path, duration)

            if success:
                clip_paths.append(clip_path)
            else:
                print("Visual " + str(i+1) + " failed, skipping")

        if not clip_paths:
            return None

        return self._merge_clips(clip_paths)

    def _generate_veo_clip(self, prompt, save_path, duration=4):
        try:
            veo_duration = "6s" if duration >= 5 else "4s"
            result = fal_client.subscribe(
                "fal-ai/veo3/fast",
                arguments={
                    "prompt": prompt + " Cinematic, dark, dramatic, 9:16 vertical video.",
                    "aspect_ratio": "9:16",
                    "duration": veo_duration,
                    "generate_audio": False
                }
            )
            if result and result.get("video", {}).get("url"):
                video_url = result["video"]["url"]
                r = requests.get(video_url, timeout=120, stream=True)
                with open(save_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                trimmed = self._trim_clip(save_path, duration)
                print("  VEO clip ready")
                return trimmed
        except Exception as e:
            print("  VEO error: " + str(e))
        return False

    def _generate_flux_image(self, prompt, save_path, duration=3):
        try:
            result = fal_client.subscribe(
                "fal-ai/flux-pro",
                arguments={
                    "prompt": prompt + " Dark cinematic atmosphere, dramatic lighting, photorealistic, 9:16 vertical.",
                    "image_size": "portrait_4_3",
                    "num_images": 1,
                    "safety_tolerance": "5"
                }
            )
            if result and result.get("images") and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                r = requests.get(image_url, timeout=30)
                img = Image.open(BytesIO(r.content))
                img = img.resize((1080, 1920), Image.LANCZOS)
                img_path = save_path.replace(".mp4", ".jpg")
                img.save(img_path, "JPEG", quality=95)
                success = self._image_to_video_kenburns(img_path, save_path, duration)
                print("  FLUX image ready")
                return success
        except Exception as e:
            print("  FLUX error: " + str(e))
        return False

    def _image_to_video_kenburns(self, image_path, video_path, duration=3):
        """FLUX resimlerine Ken Burns efekti ekler - yavaş zoom ve pan hareketi"""
        try:
            # Farklı Ken Burns hareketleri - her seferinde random seç
            movements = [
                # Yavaş zoom in - ortadan
                "zoompan=z='min(zoom+0.0015,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fps}*{dur}:s=1080x1920:fps={fps}",
                # Yavaş zoom out
                "zoompan=z='if(lte(zoom,1.0),1.3,max(1.0,zoom-0.0015))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fps}*{dur}:s=1080x1920:fps={fps}",
                # Yavaş pan soldan sağa + hafif zoom
                "zoompan=z='min(zoom+0.001,1.2)':x='if(lte(zoom,1.0),0,iw/2-(iw/zoom/2))+on/({fps}*{dur})*100':y='ih/2-(ih/zoom/2)':d={fps}*{dur}:s=1080x1920:fps={fps}",
                # Yavaş pan yukarıdan aşağı + zoom
                "zoompan=z='min(zoom+0.001,1.2)':x='iw/2-(iw/zoom/2)':y='if(lte(zoom,1.0),0,ih/2-(ih/zoom/2))+on/({fps}*{dur})*80':d={fps}*{dur}:s=1080x1920:fps={fps}",
                # Sağ alt köşeden zoom in
                "zoompan=z='min(zoom+0.0015,1.25)':x='iw-(iw/zoom)':y='ih-(ih/zoom)':d={fps}*{dur}:s=1080x1920:fps={fps}",
                # Sol üst köşeden zoom in
                "zoompan=z='min(zoom+0.0015,1.25)':x='0':y='0':d={fps}*{dur}:s=1080x1920:fps={fps}",
            ]

            fps = 24
            movement = random.choice(movements)
            vf = movement.format(fps=fps, dur=duration)

            cmd = (
                "ffmpeg -y -loop 1 -i " + image_path +
                " -vf \"" + vf + "\" " +
                " -c:v libx264 -t " + str(duration) +
                " -pix_fmt yuv420p -an " + video_path
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(video_path):
                return True

            # Fallback: basit statik video
            print("  Ken Burns failed, using static fallback")
            cmd_fallback = (
                "ffmpeg -y -loop 1 -i " + image_path +
                " -c:v libx264 -t " + str(duration) +
                " -vf scale=1080:1920 -pix_fmt yuv420p -an " + video_path
            )
            result2 = os.system(cmd_fallback)
            return result2 == 0 and os.path.exists(video_path)

        except Exception as e:
            print("  Ken Burns error: " + str(e))
        return False

    def _trim_clip(self, video_path, duration):
        try:
            trimmed_path = video_path.replace(".mp4", "_trimmed.mp4")
            cmd = (
                "ffmpeg -y -i " + video_path +
                " -t " + str(duration) +
                " -c:v libx264 -an " + trimmed_path
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(trimmed_path):
                os.replace(trimmed_path, video_path)
                return True
            return True
        except Exception as e:
            print("  Trim error: " + str(e))
        return True

    def _merge_clips(self, clip_paths):
        try:
            video_path = os.path.join(self.output_dir, "final_video.mp4")
            concat_file = os.path.join(self.output_dir, "concat.txt")
            normalized = []
            for i, clip in enumerate(clip_paths):
                norm_path = os.path.join(self.output_dir, "norm_" + str(i) + ".mp4")
                cmd = (
                    "ffmpeg -y -i " + clip +
                    " -vf \"scale=1080:1920:force_original_aspect_ratio=decrease,"
                    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2\" "
                    "-c:v libx264 -r 24 -an " + norm_path
                )
                os.system(cmd)
                if os.path.exists(norm_path):
                    normalized.append(norm_path)

            if not normalized:
                return None

            with open(concat_file, "w") as f:
                for clip in normalized:
                    f.write("file '" + os.path.abspath(clip) + "'\n")

            # Tüm klipleri aynı frame rate ile birleştir
            os.system(
                "ffmpeg -y -f concat -safe 0 -i " + concat_file +
                " -c:v libx264 -r 24 -pix_fmt yuv420p " + video_path
            )

            if os.path.exists(video_path):
                print("Video merged: " + str(len(normalized)) + " clips")
                return video_path
        except Exception as e:
            print("Merge error: " + str(e))
        return None
