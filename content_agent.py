import json
import random


NIGHTMARE_FORMATS = [
    {
        "format": "monster_attack",
        "description": "Colossal creature attacks a city or location",
        "style": "epic cinematic blockbuster horror"
    },
    {
        "format": "cursed_footage",
        "description": "Seemingly innocent moment reveals something terrifying",
        "style": "found footage realistic cursed video"
    },
    {
        "format": "atmospheric_horror",
        "description": "Slow exploration of haunted location building dread",
        "style": "atmospheric cinematic horror photography"
    },
    {
        "format": "cosmic_horror",
        "description": "Incomprehensible entity from space or other dimension",
        "style": "cosmic lovecraftian cinematic horror"
    },
    {
        "format": "psychological_nightmare",
        "description": "Reality distorts and breaks down in terrifying ways",
        "style": "surreal psychological horror dreamlike"
    },
    {
        "format": "stalker_chase",
        "description": "Someone or something hunts a person through darkness",
        "style": "tense thriller horror POV cinematic"
    },
]

USED_CONCEPTS_FILE = "used_concepts.json"


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def _get_unused_concept(self):
        try:
            with open(USED_CONCEPTS_FILE, "r") as f:
                used = json.load(f)
        except Exception:
            used = []
        if not isinstance(used, list):
            used = []
        return used

    def _save_used_concept(self, concept, used):
        used.append(concept)
        with open(USED_CONCEPTS_FILE, "w") as f:
            json.dump(used, f)

    def generate_video(self, niche=None, analytics_data=None, used_concepts=None):
        used = self._get_unused_concept()
        nightmare_format = random.choice(NIGHTMARE_FORMATS)
        fmt = nightmare_format["format"]
        description = nightmare_format["description"]
        style = nightmare_format["style"]

        print("Format: " + fmt)
        print("Description: " + description)

        prompt = (
            "You are creating a viral nightmare horror YouTube Shorts video.\n\n"
            "Format: " + fmt + "\n"
            "Description: " + description + "\n"
            "Visual style: " + style + "\n\n"
            "Create a completely unique, terrifying concept for this format.\n"
"CRITICAL: Every video must have a DIFFERENT location and a DIFFERENT creature/entity.\n"
"Locations must vary wildly: deep ocean, Arctic tundra, ancient jungle temple, "
"Soviet bunker, flooded city, volcanic island, desert ruins, frozen forest, "
"medieval dungeon, space station, underground cave, Victorian mansion, "
"abandoned nuclear plant, misty mountains, dark swamp, etc.\n"
"Creatures/entities must be bizarre and original: not standard zombies or vampires.\n"
"Think: impossible geometry creatures, entities made of shadow/water/static, "
"things with too many eyes or limbs, creatures that defy physics, "
"beings from other dimensions, ancient gods awakening, parasitic entities, "
"creatures that mimic humans but wrong, dark matter beings, sound-based horrors, etc.\n"
"Make each concept feel like something never seen before.\n\n"
            "The video is 40-45 seconds long.\n"
            "NO dialogue, NO narration, NO text on screen.\n"
            "ONLY pure cinematic horror visuals.\n"
            "10 visuals total, mix of VEO and FLUX.\n"
            "Every 3-4 seconds a new visual.\n"
            "Build tension from start to maximum terror at the end.\n\n"
            "Format-specific rules:\n\n"
            "If monster_attack: Show scale progression — first hint, then partial reveal, then full devastating reveal. Cinematic wide shots.\n\n"
            "If cursed_footage: Start completely normal and innocent. Slowly introduce something wrong. End with pure terror. Found footage VHS aesthetic.\n\n"
            "If atmospheric_horror: Single location, continuous journey deeper in. Each shot reveals something worse. Film grain, slow camera.\n\n"
            "If cosmic_horror: Something that should not exist. Incomprehensible scale. Reality breaking. Dark cosmic aesthetic.\n\n"
            "If psychological_nightmare: Reality distorts. What was safe becomes wrong. Dreamlike but terrifying. Surreal visuals.\n\n"
            "If stalker_chase: POV or close third person. Something following. Darkness closing in. Tense handheld camera.\n\n"
            "VEO prompts: slow cinematic camera movements, atmospheric lighting, no sudden cuts, build dread.\n"
            "FLUX prompts: photorealistic horror photography, something wrong in the image, dark desaturated.\n\n"
            "IMPORTANT: English only. No text overlays. Every concept must be completely original and genuinely terrifying.\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            "  \"title\": \"terrifying nightmare title under 60 chars with #Shorts #horror\",\n"
            "  \"format\": \"" + fmt + "\",\n"
            "  \"concept\": \"one sentence describing the unique nightmare concept\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 3}\n"
            "  ],\n"
            "  \"description\": \"#nightmare #horror #scary #cursed #creepy #aivideo #shorts #viral\",\n"
            "  \"tags\": [\"nightmare\", \"horror\", \"scary\", \"cursed\", \"creepy\", \"aivideo\", \"shorts\", \"viral\", \"dark\", \"terror\"]\n"
            "}\n\n"
            "No markdown, raw JSON only. Make it genuinely terrifying and completely original."
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
    "title": "Something Is Wrong Here #Shorts #horror",
    "format": fmt,
    "concept": "A terrifying nightmare scenario unfolds",
    "visuals": [
    {"type": "VEO", "prompt": "single continuous shot, creature with too many limbs and eyes slowly turning to face camera, impossible anatomy, wrong geometry, visceral horror, dark oppressive atmosphere, slow cinematic movement, something that should not exist staring directly at viewer, 9:16 vertical", "duration": 15}
],

        video_data["niche"] = "nightmare_horror"
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on diverse nightmare horror formats."
