import json


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def generate_video(self, niche, analytics_data):
        prompt = (
            "You are an expert at creating viral scary story YouTube videos.\n\n"
            "Create a terrifying TRUE CRIME or PARANORMAL story video script.\n"
            "Style: Dark, suspenseful, like 'Nightmare Files' or 'Chilling Tales'\n"
            "Length: 4-5 minutes when read aloud\n\n"
            "Choose ONE of these story types:\n"
            "- Real unsolved disappearance with creepy details\n"
            "- Paranormal event with witness accounts\n"
            "- Abandoned place with dark history\n"
            "- Urban legend that turned out to be real\n"
            "- Government cover-up with disturbing evidence\n\n"
            "Return ONLY a JSON object with these exact keys:\n"
            "{\n"
            "  \"title\": \"terrifying clickbait title under 60 chars\",\n"
            "  \"hook\": \"first 15 seconds - must be shocking\",\n"
            "  \"script\": \"full scary story script, vivid details, suspenseful pacing\",\n"
            "  \"visual_descriptions\": [\n"
            "    \"scene 1: specific scary visual\",\n"
            "    \"scene 2: specific scary visual\",\n"
            "    \"scene 3: specific scary visual\",\n"
            "    \"scene 4: specific scary visual\",\n"
            "    \"scene 5: specific scary visual\",\n"
            "    \"scene 6: specific scary visual\"\n"
            "  ],\n"
            "  \"dalle_prompts\": [\n"
            "    \"cinematic horror scene 1, dark atmosphere, photorealistic\",\n"
            "    \"cinematic horror scene 2, dark atmosphere, photorealistic\",\n"
            "    \"cinematic horror scene 3, dark atmosphere, photorealistic\"\n"
            "  ],\n"
            "  \"tags\": [\"scary\", \"horror\", \"truecrime\", \"paranormal\", \"mystery\", \"creepy\", \"disturbing\", \"unsolved\", \"dark\", \"viral\"],\n"
            "  \"description\": \"200 word spooky video description\",\n"
            "  \"thumbnail_concept\": \"exact description for a scary thumbnail: background, subject, text overlay\"\n"
            "}\n\n"
            "No markdown, no backticks, raw JSON only."
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
                "title": "The Town That Vanished Without a Trace",
                "hook": "In 1987, an entire town of 300 people disappeared overnight...",
                "script": content,
                "visual_descriptions": [
                    "abandoned town at night with fog",
                    "empty houses with broken windows",
                    "old newspaper headlines about disappearance",
                    "dark forest surrounding the town",
                    "police tape and investigation scene",
                    "mysterious figure in the distance"
                ],
                "dalle_prompts": [
                    "abandoned ghost town at night, thick fog, horror atmosphere, photorealistic",
                    "dark empty house interior with broken windows, moonlight, scary",
                    "mysterious shadowy figure in foggy forest at night, horror, cinematic"
                ],
                "tags": ["scary", "horror", "truecrime", "paranormal", "mystery", "creepy", "disturbing", "unsolved", "dark", "viral"],
                "description": "Exploring one of the most disturbing mysteries never solved.",
                "thumbnail_concept": "Dark foggy abandoned town, red glowing eyes in darkness, white bold text"
            }

        video_data["niche"] = "horror"
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on scary, suspenseful content that keeps viewers watching."