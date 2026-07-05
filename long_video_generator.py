import os
import requests
import fal_client
import random
from PIL import Image
from io import BytesIO


class LongVideoGenerator:
    def __init__(self, stock_agent):
        self.output_dir = "output"
        fal_key = os.environ.get("FAL_API_KEY", "")
        os.environ["FAL_KEY"] = fal_key
        os.makedirs(self.output_dir, exist_ok=True)
        self.stock_agent = stock_agent

    def build_visual_plan(self, video_data, target_duration):
        """
        3-4 VEO + 10 FLUX + geri kalani stock ile 16:9 gorsel plani olusturur.
        Ilk gorsel her zaman VEO (guclu acilis hook'u icin).
        """
        veo_prompts = video_data.get("veo_prompts", [])[:4]
        flux_prompts = video_data.get("flux_prompts", [])[:5]
        stock_queries = video_data.get("stock_queries", [])

        veo_duration = 8
        flux_duration = 15

        veo_total = len(veo_prompts) * veo_duration
        flux_total = len(flux_prompts) * flux_duration
        remaining = max(0, target_duration - veo_total - flux_total)

        stock_clip_duration = 12
        stock_count = max(4, round(remaining / stock_clip_duration)) if stock_queries else 0

        plan = []
        for p in veo_prompts:
            plan.append({"type": "VEO", "prompt": p, "duration": veo_duration})
        for p in flux_prompts:
            plan.append({"type": "FLUX", "prompt": p, "duration": flux_duration})
        for i in range(stock_count):
            query = stock_queries[i % len(stock_queries)] if stock_queries else "dark mystery atmosphere"
            plan.append({"type": "STOCK", "prompt": query, "duration": stock_clip_duration})

        # Ilk oge VEO olsun (hook), geri kalanini karistir ama ayni tip 3 kere ust uste gelmesin
        first = None
        for i, item in enumerate(plan):
            if item["type"] == "VEO":
                first = plan.pop(i)
                break
        rest = plan
        random.shuffle(rest)

        ordered = [first] if first else []
        last_types = []
        pool = rest[:]
        while pool:
            placed = False
            for i, item in enumerate(pool):
                if len(last_types) < 2 or not (last_types[-1] == last_types[-2] == item["type"]):
                    ordered.append(item)
                    last_types.append(item["type"])
                    pool.pop(i)
                    placed = True
                    break
            if not placed:
                # kural saglanamiyorsa ilkini ekle
                ordered.append(pool.pop(0))

        print("Visual plan: " + str(len(veo_prompts)) + " VEO + " + str(len(flux_prompts)) +
              " FLUX + " + str(stock_count) + " STOCK (~" + str(round(target_duration, 1)) + "s target)")
        return ordered

    def generate(self, visual_plan, target_duration):
        clip_paths = []
        for i, visual in enumerate(visual_plan):
            visual_type = visual["type"]
            prompt = visual["prompt"]
            duration = visual["duration"]
            clip_path = os.path.join(self.output_dir, "clip_" + str(i) + ".mp4")

            print("Visual " + str(i+1) + "/" + str(len(visual_plan)) + " [" + visual_type + "][" + str(duration) + "s]: " + prompt[:50])

            success = False
            if visual_type == "VEO":
                success = self._generate_veo_clip(prompt, clip_path, duration)
                if not success:
                    success = self._generate_veo_clip(prompt, clip_path, duration)
                if not success:
                    success = self._generate_flux_image(prompt, clip_path, duration)
            elif visual_type == "FLUX":
                success = self._generate_flux_image(prompt, clip_path, duration)
                if not success:
                    success = self._generate_flux_image(prompt, clip_path, duration)
            else:  # STOCK
                result_path = self.stock_agent.fetch_stock_clip(prompt, duration, i)
                if result_path:
                    clip_path = result_path
                    success = True
                else:
                    # stock hem video hem resim basarisiz olursa FLUX'a dus
                    success = self._generate_flux_image(
                        "dark documentary atmosphere, government archive mood, cinematic shadows",
                        clip_path, duration
                    )

            if success:
                clip_paths.append(clip_path)
            else:
                print("Visual " + str(i+1) + " failed entirely, skipping (rare)")

        if not clip_paths:
            return None

        return self._merge_clips(clip_paths, target_duration)

    def _generate_veo_clip(self, prompt, save_path, duration):
        try:
            allowed = [4, 6, 8]
            veo_pick = min(allowed, key=lambda x: abs(x - duration))
            result = fal_client.subscribe(
                "fal-ai/veo3/fast",
                arguments={
                    "prompt": prompt + " Cinematic documentary style, dark and mysterious, 16:9 landscape, no readable text, no visible faces.",
                    "aspect_ratio": "16:9",
                    "duration": str(veo_pick) + "s",
                    "generate_audio": False
                }
            )
            if result and result.get("video", {}).get("url"):
                video_url = result["video"]["url"]
                r = requests.get(video_url, timeout=120, stream=True)
                with open(save_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                if duration < veo_pick:
                    self._trim_clip(save_path, duration)
                return os.path.exists(save_path) and os.path.getsize(save_path) > 1000
        except Exception as e:
            print("  VEO error: " + str(e))
        return False

    def _generate_flux_image(self, prompt, save_path, duration):
        try:
            result = fal_client.subscribe(
                "fal-ai/flux-pro",
                arguments={
                    "prompt": prompt + " Photorealistic documentary photography, cold desaturated tones, cinematic shadows, 16:9 landscape, no readable text, no visible faces.",
                    "image_size": "landscape_16_9",
                    "num_images": 1,
                    "safety_tolerance": "5"
                }
            )
            if result and result.get("images") and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                r = requests.get(image_url, timeout=30)
                img = Image.open(BytesIO(r.content))
                img = img.resize((1920, 1080), Image.LANCZOS)
                img_path = save_path.replace(".mp4", ".jpg")
                img.save(img_path, "JPEG", quality=95)
                return self._image_to_video_kenburns(img_path, save_path, duration)
        except Exception as e:
            print("  FLUX error: " + str(e))
        return False

    def generate_thumbnail(self, thumbnail_prompt):
        """Video konusuna ozel, YouTube standardi 1280x720 (16:9) kapak resmi uretir"""
        try:
            thumb_path = os.path.join(self.output_dir, "thumbnail.jpg")
            result = fal_client.subscribe(
                "fal-ai/flux-pro",
                arguments={
                    "prompt": thumbnail_prompt + " High detail, dramatic composition, documentary thumbnail style, 16:9 landscape.",
                    "image_size": "landscape_16_9",
                    "num_images": 1,
                    "safety_tolerance": "5"
                }
            )
            if result and result.get("images") and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                r = requests.get(image_url, timeout=30)
                img = Image.open(BytesIO(r.content))
                img = img.resize((1280, 720), Image.LANCZOS)
                img.save(thumb_path, "JPEG", quality=95)
                print("Thumbnail generated")
                return thumb_path
        except Exception as e:
            print("Thumbnail generation error: " + str(e))
        return None

    def _image_to_video_kenburns(self, image_path, video_path, duration):
        try:
            fps = 24
            total_frames = max(1, int(fps * duration))
            movements = [
                "zoompan=z='min(zoom+0.0005,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={f}:s=1920x1080:fps={fps}",
                "zoompan=z='if(lte(zoom,1.0),1.15,max(1.0,zoom-0.0005))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={f}:s=1920x1080:fps={fps}",
            ]
            chosen = random.choice(movements)
            vf = chosen.format(f=total_frames, fps=fps)
            cmd = (
                "ffmpeg -y -loop 1 -i " + image_path +
                " -vf \"" + vf + "\" -c:v libx264 -t " + str(duration) +
                " -pix_fmt yuv420p -an " + video_path
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(video_path) and os.path.getsize(video_path) > 1000:
                return True

            cmd2 = (
                "ffmpeg -y -loop 1 -i " + image_path +
                " -c:v libx264 -t " + str(duration) +
                " -vf scale=1920:1080 -pix_fmt yuv420p -an " + video_path
            )
            result2 = os.system(cmd2)
            return result2 == 0 and os.path.exists(video_path) and os.path.getsize(video_path) > 1000
        except Exception as e:
            print("  Ken Burns error: " + str(e))
        return False

    def _trim_clip(self, video_path, duration):
        try:
            trimmed_path = video_path.replace(".mp4", "_trimmed.mp4")
            cmd = "ffmpeg -y -i " + video_path + " -t " + str(duration) + " -c:v libx264 -an " + trimmed_path
            result = os.system(cmd)
            if result == 0 and os.path.exists(trimmed_path) and os.path.getsize(trimmed_path) > 1000:
                os.replace(trimmed_path, video_path)
        except Exception as e:
            print("  Trim error: " + str(e))

    def _merge_clips(self, clip_paths, target_duration):
        try:
            video_path = os.path.join(self.output_dir, "visuals_merged.mp4")
            concat_file = os.path.join(self.output_dir, "concat.txt")
            normalized = []

            for i, clip in enumerate(clip_paths):
                norm_path = os.path.join(self.output_dir, "norm_" + str(i) + ".mp4")
                cmd = (
                    "ffmpeg -y -i " + clip +
                    " -vf \"scale=1920:1080:force_original_aspect_ratio=decrease,"
                    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2\" "
                    "-c:v libx264 -r 24 -pix_fmt yuv420p -an " + norm_path
                )
                os.system(cmd)
                if os.path.exists(norm_path) and os.path.getsize(norm_path) > 1000:
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

            if not os.path.exists(video_path):
                return None

            final_path = self._ensure_min_duration(video_path, target_duration, normalized)
            print("Long video merged: " + str(len(normalized)) + " clips")
            return final_path
        except Exception as e:
            print("Merge error: " + str(e))
        return None

    def _ensure_min_duration(self, video_path, target_duration, source_clips):
        try:
            import subprocess
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                capture_output=True, text=True
            )
            current_duration = float(result.stdout.strip())
            gap = target_duration - current_duration
            if gap <= 1.5:
                return video_path

            print("Visual gap of " + str(round(gap, 1)) + "s, looping clips to fill")
            concat_file = os.path.join(self.output_dir, "concat_loop.txt")
            looped_path = os.path.join(self.output_dir, "visuals_looped.mp4")

            with open(concat_file, "w") as f:
                f.write("file '" + os.path.abspath(video_path) + "'\n")
                remaining = gap
                idx = 0
                while remaining > 0 and source_clips:
                    clip = source_clips[idx % len(source_clips)]
                    f.write("file '" + os.path.abspath(clip) + "'\n")
                    remaining -= 12
                    idx += 1
                    if idx > 30:
                        break

            os.system(
                "ffmpeg -y -f concat -safe 0 -i " + concat_file +
                " -c:v libx264 -r 24 -pix_fmt yuv420p " + looped_path
            )

            if os.path.exists(looped_path):
                trimmed_path = looped_path.replace(".mp4", "_final.mp4")
                cmd = (
                    "ffmpeg -y -i " + looped_path +
                    " -t " + str(round(target_duration, 2)) +
                    " -c:v libx264 -pix_fmt yuv420p " + trimmed_path
                )
                os.system(cmd)
                return trimmed_path if os.path.exists(trimmed_path) else looped_path
            return video_path
        except Exception as e:
            print("Duration fill error: " + str(e))
        return video_path

    def add_voiceover_and_music(self, video_path, audio_path, music_path=None):
        """Ses ekler, altyazi YOK (kullanici istegi). Muzik varsa kisik seviyede karistirir."""
        try:
            output_path = os.path.join(self.output_dir, "video_with_voice.mp4")
            cmd = (
                "ffmpeg -y -i " + video_path + " -i " + audio_path + " "
                "-map 0:v -map 1:a -c:v copy -c:a aac -shortest " + output_path
            )
            result = os.system(cmd)
            if not (result == 0 and os.path.exists(output_path)):
                print("Voiceover add failed")
                return video_path

            if not music_path:
                return output_path

            final_path = os.path.join(self.output_dir, "final_with_music.mp4")
            cmd2 = (
                "ffmpeg -y -i " + output_path + " -stream_loop -1 -i " + music_path + " "
                "-filter_complex \"[1:a]volume=0.15[bg];[0:a]volume=1.0[orig];"
                "[orig][bg]amix=inputs=2:duration=first:dropout_transition=0[out]\" "
                "-map 0:v -map \"[out]\" -c:v copy -c:a aac -shortest " + final_path
            )
            result2 = os.system(cmd2)
            if result2 == 0 and os.path.exists(final_path):
                return final_path
            return output_path
        except Exception as e:
            print("Voiceover/music error: " + str(e))
        return video_path
