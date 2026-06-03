import os
import anthropic
from datetime import datetime
from content_agent import ContentAgent
from production_agent import ProductionAgent
from publish_agent import PublishAgent
from analytics_agent import AnalyticsAgent


class YouTubeAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.content_agent = ContentAgent(self.client)
        self.production_agent = ProductionAgent()
        self.publish_agent = PublishAgent()
        self.analytics_agent = AnalyticsAgent()

    def run(self):
        print("\n" + "="*50)
        print("YouTube Agent Started: " + str(datetime.now()))
        print("="*50 + "\n")

        print("Reading analytics...")
        analytics_data = self.analytics_agent.get_performance_data()

        best_niche = self.analytics_agent.get_best_performing_niche(analytics_data)
        print("Best niche: " + best_niche)

        print("\nGenerating script...")
        video_data = self.content_agent.generate_video(best_niche, analytics_data)
        print("Title: " + str(video_data.get("title", "N/A")))

        print("\nCreating video...")
        video_path = self.production_agent.create_video(video_data)

        if not video_path or not os.path.exists(video_path):
            print("ERROR: Video could not be created, exiting...")
            return

        print("Video ready: " + video_path)

        print("\nUploading to YouTube...")
        video_id = self.publish_agent.upload(video_path, video_data)
        print("Uploaded! Video ID: " + video_id)

        self.analytics_agent.save_video_performance(video_id, best_niche, video_data)

        print("\n" + "="*50)
        print("Done: " + str(datetime.now()))
        print("="*50 + "\n")


if __name__ == "__main__":
    agent = YouTubeAgent()
    agent.run()
