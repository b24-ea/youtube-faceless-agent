import os
import anthropic
from datetime import datetime
from conspiracy_content_agent import ConspiracyContentAgent
from audio_agent import AudioAgent
from stock_agent import StockAgent
from long_video_generator import LongVideoGenerator
from production_agent import ProductionAgent
from publish_agent import PublishAgent


TARGET_DURATION_SECONDS = 480  # 8 dakika hedef


def main():
    print("\n" + "="*50)
    print("Conspiracy Long-Form Agent Started: " + str(datetime.now()))
    print("="*50 + "\n")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    content_agent = ConspiracyContentAgent(client)
    audio_agent = AudioAgent()
    stock_agent = StockAgent()
    video_gen = LongVideoGenerator(stock_agent)
    production = ProductionAgent()
    publisher = PublishAgent()

    print("Generating script and visual plan...")
    video_data = content_agent.generate_video()
    print("Title: " + str(video_data.get("title", "N/A")))
    print("Topic: " + str(video_data.get("topic", "N/A")))

    script = video_data.get("script", "")
    if not script:
        print("ERROR: No script generated")
        return
    print("Script length: " + str(len(script.split())) + " words")

    print("\nGenerating voiceover with ElevenLabs...")
    audio_path, audio_duration, word_timings = audio_agent.generate_voiceover(script)
    if not audio_path:
        print("ERROR: Voiceover generation failed")
        return

    target_duration = max(TARGET_DURATION_SECONDS - 30, audio_duration + 1)
    print("Target video duration: " + str(round(target_duration, 1)) + "s (audio: " + str(round(audio_duration, 1)) + "s)")

    print("\nBuilding visual plan (3-4 VEO + 10 FLUX + stock)...")
    visual_plan = video_gen.build_visual_plan(video_data, target_duration)

    print("\nDownloading background music...")
    music_path = production.get_background_music()

    print("\nGenerating visuals...")
    visuals_path = video_gen.generate(visual_plan, target_duration)
    if not visuals_path or not os.path.exists(visuals_path):
        print("ERROR: Visual generation failed")
        return

    print("\nAdding voiceover and music (no captions)...")
    video_path = video_gen.add_voiceover_and_music(visuals_path, audio_path, music_path)

    print("\nUploading to YouTube...")
    video_id = publisher.upload_long_form(video_path, video_data)

    if video_id:
        print("Uploaded! Video ID: " + video_id)
    else:
        print("Upload failed")

    print("\n" + "="*50)
    print("Done: " + str(datetime.now()))
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
