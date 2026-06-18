import json
import random


HORROR_STYLES = [
    {"style": "abandoned mental asylum at night", "mood": "dread and isolation"},
    {"style": "deep ocean trench with unknown creature", "mood": "cosmic horror"},
    {"style": "dark forest with moving shadows", "mood": "primal fear"},
    {"style": "empty hospital corridor at 3am", "mood": "dread and silence"},
    {"style": "underground cave system with strange sounds", "mood": "claustrophobic terror"},
    {"style": "abandoned Soviet military bunker", "mood": "cold war dread"},
    {"style": "dense fog covered cemetery at midnight", "mood": "supernatural fear"},
    {"style": "flooded basement with something moving", "mood": "trapped horror"},
    {"style": "dark church with flickering candles", "mood": "religious dread"},
    {"style": "empty subway tunnel with distant sounds", "mood": "urban horror"},
    {"style": "old Victorian mansion at stormy night", "mood": "gothic terror"},
    {"style": "abandoned factory with machinery sounds", "mood": "industrial horror"},
    {"style": "dark lighthouse during violent storm", "mood": "isolation and dread"},
    {"style": "ancient ruins at night with strange lights", "mood": "archaeological horror"},
    {"style": "empty airport terminal at 4am", "mood": "liminal space horror"},
    {"style": "dark lake surface with something beneath", "mood": "aquatic dread"},
    {"style": "abandoned carnival at night", "mood": "uncanny terror"},
    {"style": "nuclear power plant after meltdown", "mood": "apocalyptic dread"},
    {"style": "dark mountain cave with strange markings", "mood": "prehistoric terror"},
    {"style": "empty shopping mall at midnight", "mood": "liminal horror"},
]

USED_STYLES_FILE = "used_styles.json"


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def _get_unused_style(self):
        try:
            with open(USED_STYLES_FILE, "r") as f:
                used = json.load(f)
        except Exception:
            used = []
        available = [s for s in HORROR_STYLES if s["style"] not in used]
        if not available:
            used = []
            available = HORROR_STYLES
        chosen = random.choice(available)
        used.append(chosen["style"])
        with open(USED_STYLES_FILE, "w") as f:
            json.dump(used, f)
        return chosen

    def generate_video(self, niche=None, analytics_data=None, used_concepts=None):
        chosen = self._get_unused_style()
        style = chosen["style"]
        mood = chosen["mood"]
        print("Style: " + style)
        print("Mood: " + mood)

        prompt = (
            "You are creating a viral atmospheric horror YouTube Shorts video.\n\n"
            "Style: " + style + "\n"
            "Mood: " + mood + "\n\n"
            "Create 8 cinematic horror visuals for a 30-second video.\n"
            "IMPORTANT: All 8 visuals must take place in the SAME location: " + style + "\n"
            "The video tells ONE continuous horror story in this single location.\n"
            "Camera slowly explores deeper into the location like a found footage journey.\n"
            "Each visual is the next moment in the same continuous scene.\n"
            "NO dialogue, NO narration, NO text on screen.\n"
            "ONLY pure atmospheric horror visuals.\n"
            "Mix of VEO video clips and FLUX still images.\n"
            "Build tension progressively, start unsettling, end terrifying.\n\n"
            "Story structure:\n"
            "Visual 1: Exterior or entrance of the location, establishing dread\n"
            "Visual 2: First step inside, dark corridor or entry\n"
            "Visual 3: Something slightly wrong noticed, subtle detail\n"
            "Visual 4: Going deeper, another room or area\n"
            "Visual 5: Clear sign something is wrong, disturbing discovery\n"
            "Visual 6: Something moves or is heard, tension peaks\n"
            "Visual 7: The worst reveal, maximum dread\n"
            "Visual 8: Final haunting image, something watching\n\n"
            "VEO prompts must have slow creeping camera movements, subtle movement like shadows "
            "shifting or dust falling, continuous with previous shot in same location, "
            "cinematic dark lighting and film grain.\n\n"
            "FLUX prompts must have same location different angle or detail, something slightly "
            "wrong in the image, dark desaturated photorealistic horror photography.\n\n"
            "IMPORTANT: English only. No text overlays.\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            "  \"title\": \"atmospheric horror title under 60 chars with #Shorts #horror\",\n"
            "  \"style\": \"" + style + "\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"slow approach toward entrance of " + style + ", establishing dread, cinematic horror, film grain, 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"first step inside " + style + ", dark corridor stretching ahead, photorealistic horror photography, desaturated\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"slow push deeper into " + style + ", something slightly wrong in the shadows, creeping camera, cinematic, 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"disturbing detail discovered inside " + style + ", close up, photorealistic horror, dark\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"going further into " + style + ", tension building, shadow movement, slow cinematic pan, 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"something wrong revealed in " + style + ", maximum unease, horror photography, desaturated dark\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"worst reveal inside " + style + ", maximum dread, slow zoom into darkness, cinematic horror, 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"final haunting image inside " + style + ", something watching from the dark, horror photography\", \"duration\": 3}\n"
            "  ],\n"
            "  \"description\": \"Pure atmospheric horror. No jump scares. Just dread. #horror #scary #atmospheric #shorts\",\n"
            "  \"tags\": [\"horror\", \"scary\", \"atmospheric\", \"shorts\", \"viral\", \"dark\", \"creepy\", \"dread\", \"haunted\", \"terror\"]\n"
            "}\n\n"
            "No markdown, raw JSON only. Every visual must feel like the next moment in the same continuous horror journey."
        )

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
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
                "title": "What Lives in the Dark #Shorts #horror",
                "style": style,
                "visuals": [
                    {"type": "VEO", "prompt": "slow approach toward entrance of " + style + ", establishing dread, cinematic horror, film grain, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "first step inside " + style + ", dark corridor, photorealistic horror photography, desaturated", "duration": 3},
                    {"type": "VEO", "prompt": "slow push deeper into " + style + ", shadows, creeping camera, cinematic, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "disturbing detail inside " + style + ", close up, photorealistic horror, dark", "duration": 3},
                    {"type": "VEO", "prompt": "going further into " + style + ", tension building, slow pan, cinematic, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "something wrong in " + style + ", maximum unease, horror photography, dark", "duration": 3},
                    {"type": "VEO", "prompt": "worst reveal inside " + style + ", maximum dread, slow zoom, cinematic horror, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "final haunting image " + style + ", something watching from dark, horror photography", "duration": 3}
                ],
                "description": "Pure atmospheric horror. No jump scares. Just dread. #horror #scary #atmospheric #shorts",
                "tags": ["horror", "scary", "atmospheric", "shorts", "viral", "dark", "creepy", "dread", "haunted", "terror"]
            }

        video_data["niche"] = "horror"
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on atmospheric horror content."
