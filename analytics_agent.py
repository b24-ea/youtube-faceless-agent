import os
import json


class AnalyticsAgent:
    def __init__(self):
        self.data_file = "analytics_history.json"

    def get_performance_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                return json.load(f)
        return {"status": "no_data", "videos": []}

    def get_best_performing_niche(self, analytics_data):
        return "horror"

    def save_video_performance(self, video_id, niche, metadata):
        data = self.get_performance_data()
        if data.get("status") == "no_data":
            data = {"videos": []}
        data["videos"].append({
            "video_id": video_id,
            "niche": niche,
            "title": metadata.get("title", ""),
            "style": metadata.get("style", ""),
            "views": 0,
            "likes": 0
        })
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)
