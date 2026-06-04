import json
import random


DARK_CONCEPTS = [
    "government secretly controls weather and uses it as a weapon",
    "shadow organization has been replacing world leaders with clones",
    "ancient evil entity awakens beneath a modern city",
    "paranormal investigator discovers portal to another dimension",
    "scientist uncovers proof that reality is a simulation gone wrong",
    "secret society performs ritual that summons something terrifying",
    "astronaut encounters alien presence that follows them back to earth",
    "small town residents discover they are all part of a dark experiment",
    "historian finds evidence that a historical disaster was deliberately caused",
    "deep sea explorer finds underwater civilization with horrifying secret",
    "journalist investigates disappearances and uncovers government cover-up",
    "family moves into house and discovers previous owners never left",
    "detective investigates case and realizes the killer is not human",
    "whistleblower leaks footage of something that should not exist",
    "archaeologist discovers ancient prophecy that is coming true now",
]


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def generate_video(self, niche, analytics_data, used_concepts=None):
        used = used_concepts or []
        available = [c for c in DARK_CONCEPTS if c not in used]
        if not available:
            available = DARK_CONCEPTS
        concept = random.choice(available)

        prompt = (
            "You are creating a viral dark mystery and paranormal YouTube Shorts video.\n\n"
            "Concept: " + concept + "\n\n"
            "Create a 30-second EXTREMELY suspenseful and shocking dark video.\n"
            "Fast-paced cuts, dynamic camera, dramatic dark lighting.\n"
            "Shocking and terrifying visuals with paranormal elements.\n"
            "Intense build-up with shocking twist ending.\n\n"
            "IMPORTANT: Everything must be in English only.\n\n"
            "Return ONLY a JSON object with these exact keys:\n"
            "title, video_prompt, description, tags\n\n"
            "video_prompt must be: cinematic dark thriller, dramatic lighting, "
            + concept +
            ", terrifying atmosphere, shocking visuals, intense pacing, "
            "photorealistic, 9:16 vertical video.\n\n"
            "tags must be a list: paranormal, mystery, horror, conspiracy, dark, shorts, viral, scary, thriller, secrets\n\n"
            "No markdown, raw JSON only."
        )

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
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
                "title": "The Government Secret Nobody Talks About #Shorts",
                "video_prompt": "Cinematic dark thriller, government facility at night, mysterious scientist discovers horrifying experiment, dark lighting, shadows, conspiracy documents, shocking revelation, photorealistic, 9:16 vertical.",
                "description": "The dark secrets they never wanted you to know.",
                "tags": ["paranormal", "mystery", "horror", "conspiracy", "dark", "shorts", "viral", "scary", "thriller", "secrets"]
            }

        video_data["niche"] = niche
        video_data["concept"] = concept
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on dark mysterious shocking content."
