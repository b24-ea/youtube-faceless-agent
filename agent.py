import os
import json
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
        self.niches = [
            "mysterious_events",
            "conspiracy_theories",
            "disaster_scenarios",
            "leaked_footage"
        ]

    def run(self):
        print("\n" + "="*50)
        print(f"🎬 YouTube Agent Başladı: {datetime.now()}")
        print("="*50 + "\n")

        print("📊 Analytics okunuyor...")
        analytics_data = self.analytics_agent.get_performance_data()

        best_niche = self.analytics_agent.get_best_performing_niche(analytics_data)
        print(f"✅ En iyi niş: {best_niche}")

        print("\n✍️  Script üretiliyor...")
        video_data = self.content_agent.generate_video(best_niche, analytics_data)
        print(f"✅ Başlık: {video_data.get('title', 'N/A')}")

        print("
