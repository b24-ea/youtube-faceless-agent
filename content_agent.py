import json


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def generate_video(self, niche, analytics_data, is_shorts=False):
        if is_shorts:
            prompt = (
                "You are an expert at creating viral YouTube SHORTS scary content.\n\n"
                "Create a terrifying SHORT story for YouTube Shorts.\n"
                "Max length: 45 seconds when read aloud (about 100-120 words)\n"
                "Style: Extremely shocking opening, fast-paced, ends with cliffhanger\n\n"
                "Return ONLY a JSON object:\n"
                "{\n"
                "  \"title\": \"scary shorts title with #Shorts\",\n"
                "  \"hook\": \"shocking first line\",\n"
                "  \"script\": \"45 second scary story, max 120 words\",\n"
                "  \"visual_descriptions\": [\"scene 1\", \"scene 2\", \"scene 3\"],\n"
                "  \"dalle_prompts\": [\"horror scene 1 photorealistic\", \"horror scene 2 photorealistic\"],\n"
                "  \"tags\": [\"#Shorts\", \"scary\", \"horror\", \"creepy\", \"paranormal\", \"mystery\", \"dark\", \"viral\", \"truecrime\", \"unsolved\"],\n"
                "  \"description\": \"short spooky description\",\n"
                "  \"thumbnail_concept\": \"scary thumbnail description\"\n"
                "}\n\n"
                "No markdown, raw JSON only."
            )
        else:
            prompt = (
                "You are an expert at creating viral scary story YouTube videos.\n\n"
                "Create a terrifying TRUE CRIME or PARANORMAL story.\n"
                "Max length: 4 minutes when read aloud (about 500-550 words)\n"
                "Style: Dark, suspenseful, documentary-style narration\n\n"
                "Choose ONE story type:\n"
                "- Real unsolved disappearance with creepy details\n"
                "- Paranormal event with witness accounts\n"
                "- Abandoned place with dark history\n"
                "- Urban legend that turned out to be real\n"
                "- Government cover-up with disturbing evidence\n\n"
                "Return ONLY a JSON object:\n"
                "{\n"
                "  \"title\": \"terrifying clickbait title under 60 chars\",\n"
                "  \"hook\": \"shocking first 15 seconds\",\n"
                "  \"script\": \"full scary story, max 550 words\",\n"
                "  \"visual_descriptions\": [\"scene 1\", \"scene 2\", \"scene 3\", \"scene 4\", \"scene 5\", \"scene 6\"],\n"
                "  \"dalle_prompts\": [\"horror scene 1 photorealistic\", \"horror scene 2 photorealistic\", \"horror scene 3 photorealistic\"],\n"
                "  \"tags\": [\"scary\", \"horror\", \"truecrime\", \"paranormal\", \"mystery\", \"creepy\", \"disturbing\", \"unsolved\", \"dark\", \"viral\"],\n"
                "  \"description\": \"200 word spooky description\",\n"
                "  \"thumbnail_concept\": \"exact scary thumbnail description\"\n"
                "}\n\n"
                "No markdown, raw JSON only."
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
                "visual_descriptions": ["abandoned town at night", "empty houses", "old newspaper", "dark forest", "police tape", "mysterious figure"],
                "dalle_prompts": ["abandoned ghost town night fog horror", "dark empty house interior moonlight scary", "mysterious figure foggy forest horror"],
                "tags": ["scary", "horror", "truecrime", "paranormal", "mystery", "creepy", "disturbing", "unsolved", "dark", "viral"],
                "description": "Exploring one of the most disturbing mysteries never solved.",
                "thumbnail_concept": "Dark foggy town, red glowing eyes, white bold text"
            }

        video_data["niche"] = "horror"
        video_data["is_shorts"] = is_shorts
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on scary suspenseful content."