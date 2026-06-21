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

    def generate(self, video_data, target_duration):
        """
        target_duration: sesin toplam süresi (saniye). Görseller bu süreyi
        dolduracak şekilde uzatılır / tekrarlanır.
        """
        visuals = video_data.get("visuals", [])
        if not visuals:
            print("No visuals found")
            return None

        # Her görselin süresini target_duration'a göre yeniden hesapla
        per_visual_duration = max(4, round(target_duration / len(visuals), 1))

        clip_paths = []
        for i, visual in enumerate(visuals):
            visual_type = visual.get("type", "FLUX")
            prompt = visual.get("prompt", "dark cinematic scene")
            clip_path = os.path.join(self.output_dir, "clip_" + str(i) + ".mp4")

            print("Visual " + str(i+1) + "/" + str(len(visuals)) + " [" + visual_type + "]: " + prompt[:50])

            if visual_type == "VEO":
                success = self._generate_veo_clip(prompt, clip_path, per_visual_duration)
            else:
                success = self._generate_flux_image(prompt, clip_path, per_visual_duration)

            if success:
                clip_paths.append(clip_path)
            else:
                print("Visual " + str(i+1) + " failed, skipping")

        if not clip_paths:
            return None

        merged = self._merge_clips(clip_paths, target_duration)
        return merged

    def _generate_veo_clip(self, prompt, save_path, duration):
        try:
            veo_duration = "8s" if duration >= 7 else ("6s" if duration >= 5 else "4s")
            result = fal_client.subscribe(
                "fal-ai/veo3/fast",
                arguments={
                    "prompt": prompt + " Cinematic, dark, moody, atmospheric, 9:16 vertical video, no visible faces.",
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
                print("  VEO clip ready")
                return True
        except Exception as e:
            print("  VEO error: " + str(e))
        return False

    def _generate_flux_image(self, prompt, save_path, duration):
        try:
            result = fal_client.subscribe(
                "fal-ai/flux-pro",
                arguments={
                    "prompt": prompt + " Photorealistic moody atmosphere, cold desaturated tones, cinematic shadows, 9:16 vertical, no visible faces.",
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

    def _image_to_video_kenburns(self, image_path, video_path, duration):
        try:
            fps = 24
            total_frames = int(fps * duration)

            movements = [
                "zoompan=z='min(zoom+0.0008,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={f}:s=1080x1920:fps={fps}",
                "zoompan=z='if(lte(zoom,1.0),1.2,max(1.0,zoom-0.0008))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={f}:s=1080x1920:fps={fps}",
                "zoompan=z='min(zoom+0.0006,1.15)':x='iw/2-(iw/zoom/2)':y='ih*0.2':d={f}:s=1080x1920:fps={fps}",
            ]

            chosen = random.choice(movements)
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

    def _merge_clips(self, clip_paths, target_duration):
        try:
            video_path = os.path.join(self.output_dir, "visuals_merged.mp4")
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

            if not os.path.exists(video_path):
                return None

            # Görsellerin toplam süresi hedef süreden kısa kalırsa, son kareyi
            # dondurup uzat (sesle senkron kalsın diye)
            final_path = self._ensure_min_duration(video_path, target_duration)
            print("Video merged: " + str(len(normalized)) + " clips")
            return final_path
        except Exception as e:
            print("Merge error: " + str(e))
        return None

    def _ensure_min_duration(self, video_path, target_duration):
        try:
            import subprocess
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                capture_output=True, text=True
            )
            current_duration = float(result.stdout.strip())

            if current_duration >= target_duration - 0.3:
                return video_path

            padded_path = video_path.replace(".mp4", "_padded.mp4")
            extra = target_duration - current_duration
            cmd = (
                "ffmpeg -y -i " + video_path +
                " -vf \"tpad=stop_mode=clone:stop_duration=" + str(round(extra, 2)) + "\" " +
                "-c:v libx264 -pix_fmt yuv420p " + padded_path
            )
            os.system(cmd)
            if os.path.exists(padded_path):
                return padded_path
            return video_path
        except Exception as e:
            print("Duration pad error: " + str(e))
        return video_path

    def add_voiceover_and_captions(self, video_path, audio_path, word_timings, output_path=None, total_duration=None):
        """
        Videoya ses ekler, kelime kelime senkronize altyazı ve sabit kanal adı yakar.
        """
        try:
            if output_path is None:
                output_path = os.path.join(self.output_dir, "video_with_voice.mp4")

            if total_duration is None and word_timings:
                total_duration = word_timings[-1]["end"] + 0.5

            ass_path = os.path.join(self.output_dir, "captions.ass")
            self._write_ass_captions(word_timings, ass_path, total_duration)

            ass_escaped = ass_path.replace(":", "\\:").replace("\\", "/")

            cmd = (
                "ffmpeg -y -i " + video_path + " -i " + audio_path + " "
                "-vf \"ass=" + ass_escaped + "\" "
                "-map 0:v -map 1:a "
                "-c:v libx264 -c:a aac -pix_fmt yuv420p -shortest " + output_path
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(output_path):
                print("Voiceover + captions added")
                return output_path

            print("Caption burn failed, adding voice only")
            cmd2 = (
                "ffmpeg -y -i " + video_path + " -i " + audio_path + " "
                "-map 0:v -map 1:a "
                "-c:v copy -c:a aac -shortest " + output_path
            )
            result2 = os.system(cmd2)
            if result2 == 0 and os.path.exists(output_path):
                return output_path

        except Exception as e:
            print("Voiceover/caption error: " + str(e))
        return video_path

    def _write_ass_captions(self, word_timings, ass_path, total_duration=None):
        """Kelime kelime yığılan TikTok tarzı neon sarı glow altyazı (.ass) üretir"""
        header = (
            "[Script Info]\n"
            "ScriptType: v4.00+\n"
            "PlayResX: 1080\n"
            "PlayResY: 1920\n"
            "\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
            "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
            "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            # Kelime kelime altyazi: kuculmus boyut (62px), beyaz govde + neon sari glow + siyah kontur
            "Style: Caption,Arial Black,62,&H00FFFFFF,&H000000FF,&H0000E6FF,&H00000000,1,0,0,0,100,100,0,0,"
            "1,4,0,2,60,60,400,1\n"
            "\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )

        events = []

        # Kelime kelime altyazi - neon sari glow icin {\blur} tag'i kullanilir
        # OutlineColour &H0000E6FF = neon sari (BGR formatinda), blur ile glow efekti verilir
        for w in word_timings:
            start = self._format_ass_time(w["start"])
            end = self._format_ass_time(w["end"])
            word_text = w["word"].upper().replace("\n", " ")
            events.append(
                "Dialogue: 0," + start + "," + end + ",Caption,,0,0,0,,"
                "{\\fad(50,50)\\blur3}" + word_text
            )

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(header)
            f.write("\n".join(events))

    def _format_ass_time(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return "{:01d}:{:02d}:{:05.2f}".format(h, m, s)
