import os
import anthropic
from datetime import datetime
from content_agent import ContentAgent
from video_generator import VideoGenerator
from publish_agent import PublishAgent
from analytics_agent import AnalyticsAgent


def main():
    print("\n" + "="*50)
    print("Faceless Agent Started: " + str(datetime.now()))
    print("="*50 + "\n")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    content_agent = ContentAgent(client)
    video_gen = VideoGenerator()
    publisher = PublishAgent()
    analytics = AnalyticsAgent()

    print("Reading analytics...")
    analytics_data = analytics.get_performance_data()
    best_niche = analytics.get_best_performing_niche(analytics_data)
    print("Best niche: " + best_niche)

    print("\nGenerating script...")
    video_data = content_agent.generate_video(best_niche, analytics_data)
    print("Title: " + str(video_data.get("title", "N/A")))

    print("\nGenerating video...")
    video_path = video_gen.generate(video_data["video_prompt"])

    if not video_path or not os.path.exists(video_path):
        print("ERROR: Video generation failed")
        return

    print("\nUploading to YouTube...")
    video_id = publisher.upload(video_path, video_data)
    print("Uploaded! Video ID: " + video_id)

    analytics.save_video_performance(video_id, best_niche, video_data)

    print("\n" + "="*50)
    print("Done: " + str(datetime.now()))
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
