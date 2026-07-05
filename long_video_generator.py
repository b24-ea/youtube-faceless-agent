import os
import requests
import fal_client
import random
from PIL import Image
from io import BytesIO


class LongVideoGenerator:
    def __init__(self):
        self.output_dir = "output"
        fal_key = os.environ.get("FAL_API_KEY", "")
        os.environ["FAL_KEY"] = fal_key
        os.makedirs(self.output_dir, exist_ok=True)

    def build_visual_plan(self, video_data, target_duration):
        """
        Claude'un urettigi 'visuals' listesini (kronolojik sirada, hikayeyle eslesen)
        alir ve her ogeye sure atar. VEO sabit 8sn, FLUX kalan sureyi paylasir.
        Sira DEGISTIRILMEZ - hikayeyle senkron kalmasi gerekiyor.
        """
        visuals = video_data.get("visuals", [])
        if not visuals:
            return []

        veo_items = [v for v in visuals if v.get("type") == "VEO"]
        flux_items = [v for v in visuals if v.get("type") == "FLUX"]

        veo_duration = 8
        veo_total = len(veo_items) * veo_duration
        remaining = max(0, target_duration - veo_total)
        flux_duration = round(remaining / len(flux_items), 1) if flux_items else 0
        flux_duration = max(6, flux_duration)  # cok kisa olmasin

        plan = []
        for v in visuals:
            duration = veo_duration if v.get("type") == "VEO" else flux_duration
            plan.append({"type": v.get("type", "FLUX"), "prompt": v.get("prompt", "dark horror scene"), "duration": duration})

        total_planned = sum(p["duration"] for p in plan)
        print("Visual plan: " + str(len(veo_items)) + " VEO + " + str(len(flux_items)) +
              " FLUX, in story order (~" + str(round(total_planned, 1)) + "s planned, target=" +
              str(round(target_duration, 1)) + "s)")
        return plan

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
            else:
                success = self._generate_flux_image(prompt, clip_path, duration)
                if not success:
                    success = self._generate_flux_image(prompt, clip_path, duration)

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
                    "prompt": prompt + " Cinematic horror, dark and dreadful, 16:9 landscape, no readable text, no visible clear faces.",
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
                    "prompt": prompt + " Photorealistic horror cinematography, cold desaturated tones, cinematic shadows, 16:9 landscape, no readable text, no visible clear faces.",
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
        try:
            thumb_path = os.path.join(self.output_dir, "thumbnail.jpg")
            result = fal_client.subscribe(
                "fal-ai/flux-pro",
                arguments={
                    "prompt": thumbnail_prompt + " High detail, dramatic composition, horror thumbnail style, 16:9 landscape.",
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

            print("Visual gap of " + str(round(gap, 1)) + "s, extending last clip to fill")
            padded_path = video_path.replace(".mp4", "_padded.mp4")
            cmd = (
                "ffmpeg -y -i " + video_path +
                " -vf \"tpad=stop_mode=clone:stop_duration=" + str(round(gap, 2)) + "\" " +
                "-c:v libx264 -pix_fmt yuv420p " + padded_path
            )
            os.system(cmd)
            if os.path.exists(padded_path):
                return padded_path
            return video_path
        except Exception as e:
            print("Duration fill error: " + str(e))
        return video_path

    def add_voiceover_and_captions(self, video_path, audio_path, word_timings, music_path=None, total_duration=None):
        """Ses + kelime kelime altyazi (16:9, 1920x1080) + istege bagli muzik ekler"""
        try:
            output_path = os.path.join(self.output_dir, "video_with_voice.mp4")

            if total_duration is None and word_timings:
                total_duration = word_timings[-1]["end"] + 0.5

            ass_path = os.path.join(self.output_dir, "captions.ass")
            self._write_ass_captions(word_timings, ass_path)
            ass_escaped = ass_path.replace(":", "\\:").replace("\\", "/")

            cmd = (
                "ffmpeg -y -i " + video_path + " -i " + audio_path + " "
                "-vf \"ass=" + ass_escaped + "\" "
                "-map 0:v -map 1:a -c:v libx264 -c:a aac -pix_fmt yuv420p -shortest " + output_path
            )
            result = os.system(cmd)
            if not (result == 0 and os.path.exists(output_path)):
                print("Caption burn failed, adding voice only")
                cmd2 = (
                    "ffmpeg -y -i " + video_path + " -i " + audio_path + " "
                    "-map 0:v -map 1:a -c:v copy -c:a aac -shortest " + output_path
                )
                os.system(cmd2)

            if not os.path.exists(output_path):
                return video_path

            if not music_path:
                return output_path

            final_path = os.path.join(self.output_dir, "final_with_music.mp4")
            cmd3 = (
                "ffmpeg -y -i " + output_path + " -stream_loop -1 -i " + music_path + " "
                "-filter_complex \"[1:a]volume=0.15[bg];[0:a]volume=1.0[orig];"
                "[orig][bg]amix=inputs=2:duration=first:dropout_transition=0[out]\" "
                "-map 0:v -map \"[out]\" -c:v copy -c:a aac -shortest " + final_path
            )
            result2 = os.system(cmd3)
            if result2 == 0 and os.path.exists(final_path):
                return final_path
            return output_path
        except Exception as e:
            print("Voiceover/caption error: " + str(e))
        return video_path

    def _write_ass_captions(self, word_timings, ass_path):
        """Kelime kelime yigilan altyazi - 1920x1080 (16:9) icin olceklendi"""
        header = (
            "[Script Info]\n"
            "ScriptType: v4.00+\n"
            "PlayResX: 1920\n"
            "PlayResY: 1080\n"
            "\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
            "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
            "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Caption,Arial Black,54,&H00FFFFFF,&H000000FF,&H0000E6FF,&H00000000,1,0,0,0,100,100,0,0,"
            "1,3,0,2,100,100,90,1\n"
            "\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )

        events = []
        for w in word_timings:
            start = self._format_ass_time(w["start"])
            end = self._format_ass_time(w["end"])
            word_text = w["word"].upper().replace("\n", " ")
            events.append(
                "Dialogue: 0," + start + "," + end + ",Caption,,0,0,0,,"
                "{\\fad(50,50)\\blur2}" + word_text
            )

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(header)
            f.write("\n".join(events))

    def _format_ass_time(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return "{:01d}:{:02d}:{:05.2f}".format(h, m, s)
