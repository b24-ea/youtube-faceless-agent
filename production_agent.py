import os
import json
import requests
import random
from PIL import Image, ImageDraw


class ProductionAgent:
    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    def get_background_music(self):
        try:
            music_path = os.path.join(self.output_dir, "music.mp3")
            
            creepy_music_urls = [
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dark%20Fog.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Lightless%20Dawn.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Invariance.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Ossuary%206%20-%20Air.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/The%20House%20of%20Leaves.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Phantasm.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Cipher.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Eternal%20Procession.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Grieving%20Angel.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Malicious.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Sinister.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Failing%20Defense.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Volatile%20Reaction.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Unholy%20Knight.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Horror%20Show.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Tenebrous%20Brothers%20Carnival.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Midnight%20Tale.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Arcadia.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Ossuary%201%20-%20A%20Beginning.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Ossuary%202%20-%20Turn.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Ossuary%203%20-%20Convergence.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Ossuary%204%20-%20Release.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Ossuary%205%20-%20Dissolution.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/At%20Rest.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Backed%20Vibes%20Clean.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Black%20Vortex.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Cold%20Funk.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Darkness%20Is%20Coming.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Evening%20of%20Chaos.mp3",
                "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Nowhere%20Land.mp3",
            ]
            
            try:
                with open("used_music.json", "r") as f:
                    used_music = json.load(f)
            except Exception:
                used_music = []
            
            available_music = [u for u in creepy_music_urls if u not in used_music]
            if not available_music:
                used_music = []
                available_music = creepy_music_urls
            
            random.shuffle(available_music)
            
            for url in available_music:
                try:
                    r = requests.get(url, timeout=30, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    })
                    if r.status_code == 200 and len(r.content) > 10000:
                        with open(music_path, "wb") as f:
                            f.write(r.content)
                        used_music.append(url)
                        with open("used_music.json", "w") as f:
                            json.dump(used_music, f)
                        print("Music: " + url.split("/")[-1].replace("%20", " "))
                        return music_path
                    else:
                        print("Music failed: " + str(r.status_code))
                except Exception as ex:
                    print("Music error: " + str(ex))
                    continue
        except Exception as e:
            print("Music error: " + str(e))
        return None

    def add_music_to_video(self, video_path, music_path):
        try:
            output_path = os.path.join(self.output_dir, "final_with_music.mp4")
            cmd = (
                "ffmpeg -y -i " + video_path + " "
                "-stream_loop -1 -i " + music_path + " "
                "-filter_complex \"[1:a]volume=0.3[bg];[0:a]volume=1.0[orig];[orig][bg]amix=inputs=2:duration=first:dropout_transition=0[out]\" "
                "-map 0:v -map \"[out]\" "
                "-c:v copy -c:a aac -shortest " + output_path
            )
            result = os.system(cmd)
            if result == 0 and os.path.exists(output_path):
                print("Music added to video")
                return output_path
            print("Music add failed, trying simple merge...")
            cmd2 = (
                "ffmpeg -y -i " + video_path + " "
                "-stream_loop -1 -i " + music_path + " "
                "-map 0:v -map 1:a "
                "-c:v copy -c:a aac -shortest " + output_path
            )
            result2 = os.system(cmd2)
            if result2 == 0 and os.path.exists(output_path):
                print("Music added (simple merge)")
                return output_path
        except Exception as e:
            print("Music merge error: " + str(e))
        return video_path

    def add_outro(self, video_path):
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
            draw.text((540, 800), "FOLLOW", fill=(255, 50, 50), anchor="mm")
            draw.text((540, 920), "FOR MORE", fill=(255, 255, 255), anchor="mm")
            draw.text((540, 1040), "HORROR", fill=(255, 50, 50), anchor="mm")
            draw.text((540, 1160), "CONTENT", fill=(255, 255, 255), anchor="mm")
            img.save(outro_image_path, "PNG")

            cmd = (
                "ffmpeg -y -loop 1 -i " + outro_image_path +
                " -t 3 -c:v libx264 -vf scale=1080:1920 -pix_fmt yuv420p -an " +
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
