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
            tension = visual.get("tension", "HOOK")
            clip_path = os.path.join(self.output_dir, "clip_" + str(i) + ".mp4")

            print("Visual " + str(i+1) + "/" + str(len(visuals)) + " [" + visual_type + "][" + tension + "]: " + prompt[:50])

            if visual_type == "VEO":
                success = self._generate_veo_clip(prompt, clip_path, duration, tension)
            else:
                success = self._generate_flux_image(prompt, clip_path, duration, tension)

            if success:
                clip_paths.append(clip_path)
            else:
                print("Visual " + str(i+1) + " failed, skipping")

        if not clip_paths:
            return None

        return self._merge_clips(clip_paths)

    def _generate_veo_clip(self, prompt, save_path, duration=4, tension="HOOK"):
        try:
            # Gerilim seviyesine göre kamera yönlendirmesi ekle
            tension_camera = {
                "HOOK":         "ultra slow creeping push forward, barely moving, ominous stillness",
                "MYSTERY":      "extremely slow dolly in, something wrong at edge of frame",
                "FIRST_SIGN":   "slow push toward the darkness, camera hesitates",
                "DREAD":        "slow tilt down then up, dread building, subtle shake",
                "ESCALATION":   "moderate push forward with slight hand-held shake, urgency rising",
                "CONFRONTATION":"slow pull back as creature advances, medium camera shake",
                "PEAK_TERROR":  "fast push into creature, heavy shake, chaotic movement",
                "AFTERMATH":    "very slow pull back to wide, stillness after chaos",
            }
            camera_note = tension_camera.get(tension, "slow cinematic movement")
            enhanced_prompt = prompt + " Camera: " + camera_note + ". Cinematic horror, 9:16 vertical, no audio."

            veo_duration = "6s" if duration >= 5 else "4s"
            result = fal_client.subscribe(
                "fal-ai/veo3/fast",
                arguments={
                    "prompt": enhanced_prompt,
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
                self._trim_clip(save_path, duration)
                print("  VEO clip ready [" + tension + "]")
                return True
        except Exception as e:
            print("  VEO error: " + str(e))
        return False

    def _generate_flux_image(self, prompt, save_path, duration=3, tension="HOOK"):
        try:
            result = fal_client.subscribe(
                "fal-ai/flux-pro",
                arguments={
                    "prompt": prompt + " Photorealistic horror film still, cold desaturated blue-black, 9:16 vertical, cinematic shadows.",
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
                success = self._image_to_video_kenburns(img_path, save_path, duration, tension)
                print("  FLUX image ready [" + tension + "]")
                return success
        except Exception as e:
            print("  FLUX error: " + str(e))
        return False

    def _image_to_video_kenburns(self, image_path, video_path, duration=3, tension="HOOK"):
        """Gerilim seviyesine göre Ken Burns hareketi — başta sakin, sonda kaotik"""
        try:
            fps = 24
            total_frames = fps * duration

            # Her gerilim seviyesi için farklı hareket hızı ve tipi
            movements = {
                "HOOK": [
                    # Çok yavaş zoom in — merak uyandırır
                    "zoompan=z='min(zoom+0.0008,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={f}:s=1080x1920:fps={fps}",
                    # Çok yavaş pan sola — bir şey görünecek gibi
                    "zoompan=z='1.1':x='iw*0.05+on/({f})*iw*0.05':y='ih/2-(ih/zoom/2)':d={f}:s=1080x1920:fps={fps}",
                ],
                "MYSTERY": [
                    # Yavaş zoom in üst kısma — karanlıkta bir şey var
                    "zoompan=z='min(zoom+0.001,1.2)':x='iw/2-(iw/zoom/2)':y='ih*0.1':d={f}:s=1080x1920:fps={fps}",
                    # Yavaş pan yukarı — zeminden yukarıya
                    "zoompan=z='1.15':x='iw/2-(iw/zoom/2)':y='ih*0.3-on/({f})*ih*0.15':d={f}:s=1080x1920:fps={fps}",
                ],
                "FIRST_SIGN": [
                    # Orta hızlı zoom in — bir şey fark edildi
                    "zoompan=z='min(zoom+0.0015,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={f}:s=1080x1920:fps={fps}",
                    # Sağ köşeye yavaş pan — oraya doğru bakış
                    "zoompan=z='1.2':x='iw*0.1+on/({f})*iw*0.15':y='ih/2-(ih/zoom/2)':d={f}:s=1080x1920:fps={fps}",
                ],
                "DREAD": [
                    # Orta zoom, hafif titreme simülasyonu
                    "zoompan=z='min(zoom+0.002,1.3)':x='iw/2-(iw/zoom/2)+sin(on*0.3)*3':y='ih/2-(ih/zoom/2)+cos(on*0.3)*2':d={f}:s=1080x1920:fps={fps}",
                ],
                "ESCALATION": [
                    # Daha hızlı zoom + hafif shake
                    "zoompan=z='min(zoom+0.003,1.4)':x='iw/2-(iw/zoom/2)+sin(on*0.5)*5':y='ih/2-(ih/zoom/2)+cos(on*0.4)*4':d={f}:s=1080x1920:fps={fps}",
                ],
                "CONFRONTATION": [
                    # Zoom out + güçlü shake — panik
                    "zoompan=z='max(zoom-0.002,1.0)':x='iw/2-(iw/zoom/2)+sin(on*0.8)*8':y='ih/2-(ih/zoom/2)+cos(on*0.7)*6':d={f}:s=1080x1920:fps={fps}",
                ],
                "PEAK_TERROR": [
                    # Hızlı zoom in + kaotik shake — maksimum korku
                    "zoompan=z='min(zoom+0.004,1.5)':x='iw/2-(iw/zoom/2)+sin(on*1.2)*12':y='ih/2-(ih/zoom/2)+cos(on*1.0)*10':d={f}:s=1080x1920:fps={fps}",
                ],
                "AFTERMATH": [
                    # Çok yavaş zoom out — sessizlik, her şey bitti
                    "zoompan=z='max(zoom-0.001,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={f}:s=1080x1920:fps={fps}",
                ],
            }

            options = movements.get(tension, movements["HOOK"])
            chosen = random.choice(options)
            vf = chosen.format(f=total_frames, fps=fps)

            cmd = (
                "ffmpeg -y -loop 1 -i " + image_path +
                " -vf \"" + vf + "\" " +
                " -c:v libx264 -t " + str(duration) +
                " -pix_fmt yuv420p -an " + video_path
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(video_path):
                return True

            # Fallback
            print("  Ken Burns failed, static fallback")
            cmd2 = (
                "ffmpeg -y -loop 1 -i " + image_path +
                " -c:v libx264 -t " + str(duration) +
                " -vf scale=1080:1920 -pix_fmt yuv420p -an " + video_path
            )
            result2 = os.system(cmd2)
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
        except Exception as e:
            print("  Trim error: " + str(e))

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
                    "-c:v libx264 -r 24 -pix_fmt yuv420p -an " + norm_path
                )
                os.system(cmd)
                if os.path.exists(norm_path):
                    normalized.append(norm_path)

            if not normalized:
                return None

            with open(concat_file, "w") as f:
                for clip in normalized:
                    f.write("file '" + os.path.abspath(clip) + "'\n")

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
