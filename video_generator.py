import os
import requests
import fal_client


class VideoGenerator:
    def __init__(self):
        self.output_dir = "output"
        fal_key = os.environ.get("FAL_API_KEY", "")
        os.environ["FAL_KEY"] = fal_key
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, video_prompt):
        clips = []
        prompts = [
            video_prompt + " Opening scene, dark and mysterious atmosphere, immediate dread.",
            video_prompt + " Situation escalates, terrifying revelations unfold.",
            video_prompt + " Maximum horror and intensity, peak darkness.",
            video_prompt + " Shocking unexpected dark twist ending."
        ]
        for i, prompt in enumerate(prompts):
            clip_path = self._generate_clip(prompt, i)
            if clip_path:
                clips.append(clip_path)
        if not clips:
            return None
        return self._merge_clips(clips)

    def _generate_clip(self, prompt, index):
        try:
            print("Generating clip " + str(index+1) + "/4...")
            result = fal_client.subscribe(
                "fal-ai/veo3/fast",
                arguments={
                    "prompt": prompt,
                    "aspect_ratio": "9:16",
                    "duration": "8s",
                    "generate_audio": True
                }
            )
            if result and result.get("video", {}).get("url"):
                video_url = result["video"]["url"]
                clip_path = os.path.join(self.output_dir, "clip_" + str(index) + ".mp4")
                r = requests.get(video_url, timeout=120, stream=True)
                with open(clip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("Clip " + str(index+1) + " ready")
                return clip_path
        except Exception as e:
            print("Clip " + str(index+1) + " error: " + str(e))
        return None

    def _merge_clips(self, clips):
        try:
            video_path = os.path.join(self.output_dir, "final_video.mp4")
            concat_file = os.path.join(self.output_dir, "concat.txt")
            with open(concat_file, "w") as f:
                for clip in clips:
                    f.write("file '" + os.path.abspath(clip) + "'\n")
            os.system("ffmpeg -y -f concat -safe 0 -i " + concat_file + " -c copy " + video_path)
            if os.path.exists(video_path):
                print("Clips merged: " + str(len(clips)) + " clips = ~" + str(len(clips)*8) + "s")
                return video_path
        except Exception as e:
            print("Merge error: " + str(e))
        return clips[0] if clips else None
