import json


class ContentAgent:
    def __init__(self, client):
        self.client = client
        self.niche_prompts = {
            "mysterious_events": "mysterious disappearances, unexplained phenomena, abandoned places",
            "conspiracy_theories": "government secrets, dark history, hidden truths",
            "disaster_scenarios": "simulation theory, parallel universe, AI takeover",
            "leaked_footage": "leaked documents, secret recordings, whistleblower stories"
        }

    def generate_video(self, niche, analytics_data):
        niche_description = self.niche_prompts.get(niche, self.niche_prompts["mysterious_events"])

        prompt = (
            "You are an expert at creating viral YouTube faceless video content.\n\n"
            "Niche: " + niche_description + "\n"
            "Language: English\n\n"
            "Return ONLY a JSON object with these exact keys:\n"
            "title, hook, script, visual_descriptions, tags, description, thumbnail_concept\n\n"
            "visual_descriptions must be a list of 4 strings.\n"
            "tags must be a list of 10 strings.\n"
            "No markdown, no backticks, just raw JSON."
        )

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text.strip()

        if "```" in content:
            parts = content.split("```")
            for part in parts:
                if part.startswith("json"):
                    content = part[4:].strip()
                    break
                elif "{" in part:
                    content = part.strip()
                    break

        try:
            video_data = json.loads(content)
        except Exception:
            video_data = {
                "title": "The Mystery Nobody Talks About",
                "hook": "What you are about to see will change everything...",
                "script": content,
                "visual_descriptions": [
                    "Dark mysterious atmosphere",
                    "Old documents on a table",
                    "Strange symbols on a wall",
                    "Aerial view of abandoned place"
                ],
                "tags": [
                    "mystery", "conspiracy", "unexplained", "secrets", "viral",
                    "shocking", "hidden", "truth", "exposed", "real"
                ],
                "description": "Exploring mysteries that mainstream media will not cover.",
                "thumbnail_concept": "Dark background with glowing eye and red text"
            }

        video_data["niche"] = niche
        return video_data

    def _get_performance_insight(self, analytics_data):
        if not analytics_data or analytics_data.get("status") == "no_data":
            return "No data yet. Use general viral trends."
        return "First videos - use general viral format."
