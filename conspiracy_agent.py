import os
import anthropic
from datetime import datetime
from conspiracy_content_agent import ConspiracyContentAgent
from audio_agent import AudioAgent
from long_video_generator import LongVideoGenerator
from production_agent import ProductionAgent
from publish_agent import PublishAgent


TARGET_DURATION_SECONDS = 300  # 5 dakika hedef

# Daha kalin, yogun, urkutucu erkek sesi (ElevenLabs premade "Arnold" - dogal olarak
# derin/yogun tonu ile bilinir). Psychology Shorts'un sesini (Adam) etkilemez, ayri parametre.
CREEPY_VOICE_ID = "VR6AewLTigWG4xSOukaG"


def main():
    print("\n" + "="*50)
    print("Creepy Horror Long-Form Agent Started: " + str(datetime.now()))
    print("="*50 + "\n")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    content_agent = ConspiracyContentAgent(client)
    audio_agent = AudioAgent()
    video_gen = LongVideoGenerator()
    production = ProductionAgent()
    publisher = PublishAgent()

    print("Generating horror story and visual sequence...")
    video_data = content_agent.generate_video()
    print("Title: " + str(video_data.get("title", "N/A")))
    print("Premise: " + str(video_data.get("topic", "N/A")))
    print("Entity: " + str(video_data.get("entity_name", "N/A")))

    script = video_data.get("script", "")
    if not script:
        print("ERROR: No script generated")
        return
    print("Script length: " + str(len(script.split())) + " words")

    print("\nGenerating voiceover with ElevenLabs (deep eerie voice)...")
    audio_path, audio_duration, word_timings = audio_agent.generate_voiceover(script, voice_id=CREEPY_VOICE_ID)
    if not audio_path:
        print("ERROR: Voiceover generation failed")
        return

    target_duration = max(TARGET_DURATION_SECONDS - 20, audio_duration + 1)
    print("Target video duration: " + str(round(target_duration, 1)) + "s (audio: " + str(round(audio_duration, 1)) + "s)")

    print("\nBuilding visual plan (VEO3 + FLUX Pro only, story order)...")
    visual_plan = video_gen.build_visual_plan(video_data, target_duration)
    if not visual_plan:
        print("ERROR: No visual plan generated")
        return

    print("\nDownloading background music...")
    music_path = production.get_background_music()

    print("\nGenerating visuals...")
    visuals_path = video_gen.generate(visual_plan, target_duration)
    if not visuals_path or not os.path.exists(visuals_path):
        print("ERROR: Visual generation failed")
        return

    print("\nAdding voiceover, captions, and music...")
    video_path = video_gen.add_voiceover_and_captions(
        visuals_path, audio_path, word_timings, music_path=music_path, total_duration=target_duration
    )

    print("\nUploading to YouTube...")
    video_id = publisher.upload_long_form(video_path, video_data)

    if video_id:
        print("Uploaded! Video ID: " + video_id)

        thumbnail_prompt = video_data.get("thumbnail_prompt")
        if thumbnail_prompt:
            print("\nGenerating custom thumbnail...")
            thumbnail_path = video_gen.generate_thumbnail(thumbnail_prompt)
            if thumbnail_path:
                publisher.set_thumbnail(video_id, thumbnail_path)
    else:
        print("Upload failed")

    print("\n" + "="*50)
    print("Done: " + str(datetime.now()))
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
