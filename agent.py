import os
import json
import asyncio
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
        
        # Kanal nişleri
        self.niches = [
            "mysterious_events",      # Gizemli olaylar
            "conspiracy_theories",    # Komplo teorileri  
            "disaster_scenarios",     # Felaket senaryoları
            "leaked_footage"          # Sızdırılmış görüntüler
        ]

    def run(self):
        print(f"\n{'='*50}")
        print(f"🎬 YouTube Agent Başladı: {datetime.now()}")
        print(f"{'='*50}\n")

        # 1. Analytics oku (önceki videoların performansı)
        print("📊 Analytics okunuyor...")
        analytics_data = self.analytics_agent.get_performance_data()
        
        # 2. En iyi performans gösteren nişi belirle
        best_niche = self.analytics_agent.get_best_performing_niche(analytics_data)
        print(f"✅ En iyi niş: {best_niche}")

        # 3. Script üret
        print("\n✍️  Script üretiliyor...")
        video_data = self.content_agent.generate_video(best_niche, analytics_data)
        print(f"✅ Başlık: {video_data.get('title', video_data.get('BAŞLIK', 'Video üretildi'))}")

        # 4. Video üret
        print("\n🎬 Video üretiliyor...")
        video_path = self.production_agent.create_video(video_data)
        print(f"✅ Video hazır: {video_path}")

        # 5. YouTube'a yükle
        print("\n📤 YouTube'a yükleniyor...")
        video_id = self.publish_agent.upload(video_path, video_data)
        print(f"✅ Yüklendi! Video ID: {video_id}")

        print(f"\n{'='*50}")
        print(f"🎉 Tamamlandı: {datetime.now()}")
        print(f"{'='*50}\n")

if __name__ == "__main__":
    agent = YouTubeAgent()
    agent.run()
