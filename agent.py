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
    print("Horror Agent Started: " + str(datetime.now()))
    print("="*50 + "\n")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    content_agent = ContentAgent(client)
    video_gen = VideoGenerator()
    production = ProductionAgent()
    publisher = PublishAgent()
    analytics = AnalyticsAgent()

    print("Generating horror visuals...")
    video_data = content_agent.generate_video()
    print("Title: " + str(video_data.get("title", "N/A")))
    print("Style: " + str(video_data.get("style", "N/A")))

    print("\nDownloading background music...")
    music_path = production.get_background_music()

    print("\nGenerating visuals (Flux Pro + Veo 3)...")
    video_path = video_gen.generate(video_data)
    if not video_path or not os.path.exists(video_path):
        print("ERROR: Video generation failed")
        return

    if music_path:
        print("\nAdding music to video...")
        video_path = production.add_music_to_video(video_path, music_path)

    print("\nUploading to YouTube...")
    video_id = publisher.upload(video_path, video_data)
    print("Uploaded! Video ID: " + video_id)

    analytics.save_video_performance(video_id, "horror", video_data)

    print("\n" + "="*50)
    print("Done: " + str(datetime.now()))
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
