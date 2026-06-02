import os
import json
import random

class AnalyticsAgent:
    def __init__(self):
        self.data_file = "analytics_history.json"

    def get_performance_data(self) -> dict:
        # Kaydedilmiş analytics verisi var mı?
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                return json.load(f)
        
        # İlk çalışmada veri yok
        return {"status": "no_data", "videos": []}

    def get_best_performing_niche(self, analytics_data: dict) -> str:
        niches = [
            "mysterious_events",
            "conspiracy_theories",
            "disaster_scenarios",
            "leaked_footage"
        ]
        
        if analytics_data.get("status") == "no_data":
            # İlk videoda mysterious_events ile başla
            return "mysterious_events"
        
        # Videolar arasında en iyi performans göstereni bul
        videos = analytics_data.get("videos", [])
        if not videos:
            return niches[0]
        
        # Niş bazında ortalama view hesapla
        niche_performance = {}
        for video in videos:
            niche = video.get("niche", "mysterious_events")
            views = video.get("views", 0)
            if niche not in niche_performance:
                niche_performance[niche] = []
            niche_performance[niche].append(views)
        
        # En yüksek ortalamaya sahip nişi seç
        best_niche = max(
            niche_performance,
            key=lambda n: sum(niche_performance[n]) / len(niche_performance[n])
        )
        
        return best_niche

    def save_video_performance(self, video_id: str, niche: str, metadata: dict):
        data = self.get_performance_data()
        if data.get("status") == "no_data":
            data = {"videos": []}
        
        data["videos"].append({
            "video_id": video_id,
            "niche": niche,
            "title": metadata.get("title", ""),
            "upload_date": metadata.get("upload_date", ""),
            "views": 0,  # Sonra güncellenecek
            "watch_time": 0,
            "likes": 0
        })
        
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)
