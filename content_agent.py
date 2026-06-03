import json


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def generate_video(self, niche, analytics_data, is_shorts=False):
        if is_shorts:
            prompt = (
                "You are an expert at creating viral YouTube SHORTS about mysteries and paranormal events.\n\n"
                "Create a terrifying SHORT video script.\n"
                "Max length: 45 seconds when read aloud (about 100-120 words)\n"
                "Style: Extremely shocking, dark, mysterious, ends with cliffhanger\n\n"
                "Choose ONE topic:\n"
                "- Paranormal event caught on camera\n"
                "- Government conspiracy nobody talks about\n"
                "- Unexplained disappearance with creepy details\n"
                "- Horror urban legend that turned out real\n\n"
                "Return ONLY a JSON object:\n"
                "{\n"
                "  \"title\": \"dark mystery shorts title with #Shorts\",\n"
                "  \"hook\": \"shocking dark opening line\",\n"
                "  \"script\": \"45 second dark mystery script, max 120 words\",\n"
                "  \"visual_descriptions\": [\"dark scene 1\", \"creepy scene 2\", \"mysterious scene 3\"],\n"
                "  \"dalle_prompts\": [\"dark horror scene 1\", \"mysterious scene 2\"],\n"
                "  \"tags\": [\"#Shorts\", \"paranormal\", \"mystery\", \"horror\", \"conspiracy\", \"creepy\", \"dark\", \"viral\", \"scary\", \"unsolved\"],\n"
                "  \"description\": \"dark mysterious short description\",\n"
                "  \"thumbnail_concept\": \"dark scary thumbnail with mystery element\"\n"
                "}\n\n"
                "No markdown, raw JSON only."
            )
        else:
            prompt = (
                "You are an expert at creating viral mystery and paranormal YouTube videos.\n\n"
                "Create a dark, mysterious video script.\n"
                "Max length: 4 minutes when read aloud (about 500-550 words)\n"
                "Style: Documentary-style, dark, suspenseful, shocking revelations\n\n"
                "Choose ONE topic:\n"
                "- Real government conspiracy with evidence\n"
                "- Paranormal event witnessed by thousands\n"
                "- Country with dark secret history\n"
                "- Unexplained horror mystery never solved\n"
                "- Secret society controlling world events\n\n"
                "Return ONLY a JSON object:\n"
                "{\n"
                "  \"title\": \"dark mystery clickbait title under 60 chars\",\n"
                "  \"hook\": \"shocking dark opening 15 seconds\",\n"
                "  \"script\": \"full dark mystery script max 550 words\",\n"
                "  \"visual_descriptions\": [\"dark scene 1\", \"creepy scene 2\", \"mysterious scene 3\", \"horror scene 4\", \"conspiracy scene 5\", \"shocking scene 6\"],\n"
                "  \"dalle_prompts\": [\"dark conspiracy scene photorealistic\", \"paranormal event dark atmosphere\", \"horror mystery scene cinematic\"],\n"
                "  \"tags\": [\"paranormal\", \"mystery\", \"horror\", \"conspiracy\", \"creepy\", \"dark\", \"viral\", \"scary\", \"unsolved\", \"secrets\"],\n"
                "  \"description\": \"200 word dark mysterious description\",\n"
                "  \"thumbnail_concept\": \"dark scary thumbnail with mystery element and shocking text\"\n"
                "}\n\n"
                "No markdown, raw JSON only."
            )

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
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
                "title": "The Government Secret Nobody Talks About",
                "hook": "In 1987, classified documents revealed something terrifying...",
                "script": content,
                "visual_descriptions": ["dark government building", "classified documents", "mysterious figure", "dark forest", "conspiracy board", "shocking evidence"],
                "dalle_prompts": ["dark government conspiracy scene cinematic", "paranormal event dark atmosphere photorealistic", "horror mystery scene dramatic lighting"],
                "tags": ["paranormal", "mystery", "horror", "conspiracy", "creepy", "dark", "viral", "scary", "unsolved", "secrets"],
                "description": "The dark secrets they never wanted you to know.",
                "thumbnail_concept": "Dark mysterious figure, red glowing eyes, dramatic lighting, white bold text"
            }

        video_data["niche"] = "mystery_horror"
        video_data["is_shorts"] = is_shorts
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on dark mysterious content that shocks viewers."
