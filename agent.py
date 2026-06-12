import os
import anthropic
from datetime import datetime
from content_agent import ContentAgent
from video_generator import VideoGenerator
from production_agent import ProductionAgent
from publish_agent import PublishAgent
from analytics_agent import AnalyticsAgent


def main():
    print("\n" + "="*50)
    print("Faceless Agent Started: " + str(datetime.now()))
    print("="*50 + "\n")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    content_agent = ContentAgent(client)
    video_gen = VideoGenerator()
    production = ProductionAgent()
    publisher = PublishAgent()
    analytics = AnalyticsAgent()

    print("Reading analytics...")
    analytics_data = analytics.get_performance_data()
    best_niche = analytics.get_best_performing_niche(analytics_data)
    print("Best niche: " + best_niche)

    print("\nGenerating script and visuals...")
    video_data = content_agent.generate_video(best_niche, analytics_data)
    print("Title: " + str(video_data.get("title", "N/A")))
    print("Country: " + str(video_data.get("country", "N/A")))
    print("Concept: " + str(video_data.get("concept", "N/A")))

    print("\nGenerating audio...")
    audio_path = production.generate_audio(video_data.get("script", {}))
    if not audio_path:
        print("ERROR: Audio generation failed")
        return
    audio_duration = production.get_audio_duration(audio_path)

    print("\nDownloading background music...")
    music_path = production.get_background_music()
    if music_path:
        audio_path = production.mix_audio_with_music(audio_path, music_path, audio_duration)

    print("\nGenerating visuals (Flux Pro + Veo 3)...")
    video_path = video_gen.generate(video_data)
    if not video_path or not os.path.exists(video_path):
        print("ERROR: Video generation failed")
        return

    print("\nAdding audio to video...")
    video_path = production.add_audio_to_video(video_path, audio_path)

    print("\nAdding subtitles...")
    video_path = production.add_subtitles(video_path, video_data.get("script", {}), audio_duration)

    print("\nUploading to YouTube...")
    video_id = publisher.upload(video_path, video_data)
    print("Uploaded! Video ID: " + video_id)

    analytics.save_video_performance(video_id, best_niche, video_data)

    print("\n" + "="*50)
    print("Done: " + str(datetime.now()))
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
