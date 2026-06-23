import os
import anthropic
from datetime import datetime
from content_agent import ContentAgent
from audio_agent import AudioAgent
from video_generator import VideoGenerator
from production_agent import ProductionAgent
from publish_agent import PublishAgent
from analytics_agent import AnalyticsAgent


# Video suresi bu aralikta olmasi hedeflenir (saniye).
# NOT: ses suresi MAX_DURATION'i asarsa video KISILMAZ, sesin tam suresine gore uretilir
# (aksi halde konusma/altyazi yarida kesilir). Bu yuzden script uzunlugu content_agent'ta
# bu hedefe gore ayarlanmali.
MIN_DURATION = 25
MAX_DURATION = 30


def main():
    print("\n" + "="*50)
    print("Psychology Agent Started: " + str(datetime.now()))
    print("="*50 + "\n")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    content_agent = ContentAgent(client)
    audio_agent = AudioAgent()
    video_gen = VideoGenerator()
    production = ProductionAgent()
    publisher = PublishAgent()
    analytics = AnalyticsAgent()

    print("Generating script and visual prompts...")
    video_data = content_agent.generate_video()
    print("Title: " + str(video_data.get("title", "N/A")))
    print("Topic: " + str(video_data.get("scenario", "N/A")))

    script = video_data.get("script", "")
    if not script:
        print("ERROR: No script generated")
        return

    print("\nGenerating voiceover with ElevenLabs...")
    audio_path, audio_duration, word_timings = audio_agent.generate_voiceover(script)
    if not audio_path:
        print("ERROR: Voiceover generation failed")
        return

    # Ses suresi asla kirpilmaz - video her zaman sesin TAMAMINI kapsayacak
    # sekilde uretilir, boylece konusma/altyazi yarida kesilmez.
    # MIN_DURATION sadece sesin cok kisa gelmesi durumunda alt sinir olarak kullanilir.
    target_duration = max(MIN_DURATION, audio_duration + 0.5)

    if audio_duration > MAX_DURATION + 3:
        print("WARNING: Audio is " + str(round(audio_duration, 1)) + "s, well over the "
              + str(MAX_DURATION) + "s target. Script may need to be shorter next time.")

    print("Target video duration: " + str(round(target_duration, 1)) + "s (audio: " + str(round(audio_duration, 1)) + "s)")

    print("\nPicking horror visuals (max 4s each)...")
    video_data["visuals"] = content_agent.get_horror_visuals(target_duration, max_visual_duration=4)
    print(str(len(video_data["visuals"])) + " visuals selected")

    print("\nDownloading background music...")
    music_path = production.get_background_music()

    print("\nGenerating visuals (Flux Pro + Veo 3)...")
    visuals_path = video_gen.generate(video_data, target_duration)
    if not visuals_path or not os.path.exists(visuals_path):
        print("ERROR: Visual generation failed")
        return

    print("\nAdding voiceover and word-by-word captions...")
    video_path = video_gen.add_voiceover_and_captions(visuals_path, audio_path, word_timings)

    if music_path:
        print("\nAdding background music...")
        video_path = production.add_music_to_video(video_path, music_path)

    print("\nUploading to YouTube...")
    video_id = publisher.upload(video_path, video_data)

    if video_id and not str(video_id).startswith("SKIPPED"):
        print("Uploaded! Video ID: " + video_id)
        analytics.save_video_performance(video_id, "psychology", video_data)
    else:
        print("Upload skipped — not a publish day")

    print("\n" + "="*50)
    print("Done: " + str(datetime.now()))
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
