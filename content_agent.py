import json
import random


DARK_CONCEPTS = [
    {"concept": "The Russian Sleep Experiment was real and is still happening today", "country": "Russia"},
    {"concept": "MK Ultra mind control program never actually stopped and targets civilians today", "country": "USA"},
    {"concept": "Japan's Unit 731 created a biological weapon that was secretly deployed in 1995", "country": "Japan"},
    {"concept": "The UK government deliberately caused the 1952 Great Smog to test population control", "country": "UK"},
    {"concept": "Brazil's Colonia hospital performed illegal experiments on 60000 patients for decades", "country": "Brazil"},
    {"concept": "China's Underground Great Wall hides a secret city built for elite survival", "country": "China"},
    {"concept": "Germany's Nazi Bell device was completed and smuggled to Argentina after WW2", "country": "Germany"},
    {"concept": "Australia's Pine Gap base is actually a portal monitoring station for interdimensional activity", "country": "Australia"},
    {"concept": "Egypt's Great Pyramid contains a hidden chamber with technology that predates humanity", "country": "Egypt"},
    {"concept": "Mexico's Zone of Silence blocks all signals and has been used for alien communication since 1970", "country": "Mexico"},
    {"concept": "Norway's Svalbard Seed Vault contains something far more terrifying than seeds", "country": "Norway"},
    {"concept": "India's Roopkund Lake skeletons are victims of a classified weather weapon test", "country": "India"},
    {"concept": "France's Paris Catacombs hide an active secret society still performing rituals today", "country": "France"},
    {"concept": "Iran's Burnt City contains evidence of an advanced civilization erased from all history books", "country": "Iran"},
    {"concept": "Peru's Nazca Lines are landing coordinates still being used by craft seen today", "country": "Peru"},
    {"concept": "Turkey's Gobekli Tepe was deliberately buried to hide proof it was built by non-humans", "country": "Turkey"},
    {"concept": "South Korea's Hwaseong Fortress tunnels connect to an underground base still operational", "country": "South Korea"},
    {"concept": "Italy's Vatican Secret Archives contain suppressed evidence of extraterrestrial contact", "country": "Italy"},
    {"concept": "Canada's Willow Creek facility was a classified mind control site that vanished from all records", "country": "Canada"},
    {"concept": "Bolivia's Gate of the Sun is actually a functional star map pointing to an incoming event", "country": "Bolivia"},
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
