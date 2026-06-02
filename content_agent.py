import json
import random

class ContentAgent:
    def __init__(self, client):
        self.client = client
        
        self.niche_prompts = {
            "mysterious_events": "mysterious disappearances, unexplained phenomena, abandoned places",
            "conspiracy_theories": "government secrets, dark history, hidden truths",
            "disaster_scenarios": "simulation theory, parallel universe, AI takeover, disaster scenarios",
            "leaked_footage": "leaked documents, secret recordings, whistleblower stories"
        }

    def generate_video(self, niche: str, analytics_data: dict) -> dict:
        performance_insight = self._get_performance_insight(analytics_data)
        niche_description = self.niche_prompts.get(niche, self.niche_prompts["mysterious_events"])
        
        prompt = f"""You are an expert at creating viral YouTube faceless video content.

Niche: {niche_description}
Language: English (global audience)
Format: Faceless video (visuals + voiceover only)

Performance insights:
{performance_insight}

Generate video content in this EXACT JSON format, use only these exact keys:

{{
  "title": "compelling title under 60 chars",
  "hook": "opening line that grabs attention in first 15 seconds",
  "script": "full 3-4 minute video script divided into sections",
  "visual_descriptions": ["visual 1 description", "visual 2 description", "visual 3 description", "visual 4 description"],
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"],
  "description": "200 word YouTube video description with keywords",
  "thumbnail_concept": "what should appear on the thumbnail"
}}

IMPORTANT: Return ONLY the JSON object, no other text, no markdown backticks."""

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text.strip()
        
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.split("```")[0].strip()
        
        try:
            video_data = json.loads(content)
        except:
            video_data = {
                "title": "The Mystery Nobody Talks About",
                "hook": "What you are about to see will change everything you think you know...",
                "script": content,
                "visual_descriptions": ["Dark mysterious atmosphere", "Old documents", "Strange symbols", "Aerial view"],
                "tags": ["mystery", "conspiracy", "unexplained", "secrets", "viral", "shocking", "hidden", "truth", "exposed", "real"],
                "description": "Exploring the mysteries that mainstream media will not cover. Subscribe for weekly mystery content.",
                "thumbnail_concept": "Dark background with glowing eye symbol and red text"
            }
        
        video_data["niche"] = niche
        return video_data

    def _get_performance_insight(self, analytics_data: dict) -> str:
        if not analytics_data or analytics_data.get("status") == "no_data":
            return "No data yet. Use general viral trends."
        
        insights = []
        
        if analytics_data.get("best_performing_type"):
            insights.append(f"Best content type: {analytics_data['best_performing_type']}")
        
        if analytics_data.get("avg_watch_time"):
            insights.append(f"Average watch time: {analytics_data['avg_watch_time']} seconds")
        
        if analytics_data.get("top_tags"):
            insights.append(f"Best performing tags: {', '.join(
