import json
import random


HORROR_STYLES = [
    {"style": "abandoned mental asylum at night with shadowy figures in corridors", "mood": "dread and isolation"},
    {"style": "deep ocean trench with massive unknown creature circling below", "mood": "cosmic horror"},
    {"style": "dark forest where trees have human faces and something follows", "mood": "primal fear"},
    {"style": "empty hospital corridor at 3am with boogeyman at the end", "mood": "dread and silence"},
    {"style": "underground cave system where walls are covered in human handprints", "mood": "claustrophobic terror"},
    {"style": "abandoned Soviet military bunker with something alive inside", "mood": "cold war dread"},
    {"style": "dense fog covered cemetery where the dead are standing upright", "mood": "supernatural fear"},
    {"style": "flooded basement with pale hands reaching from the black water", "mood": "trapped horror"},
    {"style": "dark church where the congregation has no faces", "mood": "religious dread"},
    {"style": "empty subway tunnel where something breathes in the darkness", "mood": "urban horror"},
    {"style": "old Victorian mansion where mirrors show wrong reflections", "mood": "gothic terror"},
    {"style": "abandoned factory where machines run with no one operating them", "mood": "industrial horror"},
    {"style": "dark lighthouse where the light reveals something circling outside", "mood": "isolation and dread"},
    {"style": "ancient ruins where carved faces on walls slowly turn to look", "mood": "archaeological horror"},
    {"style": "empty airport terminal at 4am with a child standing still in darkness", "mood": "liminal space horror"},
    {"style": "dark lake surface where a pale figure slowly rises from below", "mood": "aquatic dread"},
    {"style": "abandoned carnival at night where clown statues move between blinks", "mood": "uncanny terror"},
    {"style": "nuclear power plant where glowing figures walk through walls", "mood": "apocalyptic dread"},
    {"style": "dark mountain cave where ancient evil has slept for centuries and wakes", "mood": "prehistoric terror"},
    {"style": "empty shopping mall at midnight where mannequins follow your movement", "mood": "liminal horror"},
    {"style": "dense fog covered playground where swings move with no children", "mood": "childhood nightmare"},
    {"style": "abandoned house where every room has a figure standing in the corner", "mood": "home invasion dread"},
    {"style": "dark bedroom where something under the bed slowly pulls itself out", "mood": "boogeyman terror"},
    {"style": "empty school hallway at night with lockers that open by themselves", "mood": "institutional dread"},
    {"style": "dark well in a field where pale hands grip the edges from inside", "mood": "folklore horror"},
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
            "Create 10 cinematic horror visuals for a 45-second video.\n"
            "IMPORTANT: All 10 visuals must take place in the SAME location: " + style + "\n"
            "The video tells ONE continuous horror story in this single location.\n"
            "Camera slowly explores deeper into the location like a found footage journey.\n"
            "Each visual is the next moment in the same continuous scene.\n"
            "NO dialogue, NO narration, NO text on screen.\n"
            "ONLY pure atmospheric horror visuals.\n"
            "Mix of VEO video clips and FLUX still images.\n"
            "Build tension progressively, start unsettling, end terrifying.\n\n"
"NIGHTMARE RULES:\n"
"- Every video must feel like a real nightmare, not a movie\n"
"- Include classic nightmare elements: boogeyman, ghosts, pale figures, wrong faces\n"
"- Locations must feel deeply wrong and corrupted\n"
"- Creatures must be humanoid but fundamentally broken: wrong proportions, too many joints, blank faces, hollow eyes\n"
"- Use childhood fears: things under the bed, figures in corners, something following\n"
"- The horror must feel PERSONAL, like it is coming for the viewer\n\n"
            "Story structure:\n"
            "Visual 1: Exterior or entrance, establishing dread\n"
            "Visual 2: First step inside, dark corridor or entry\n"
            "Visual 3: Something slightly wrong noticed, subtle detail\n"
            "Visual 4: Going deeper, another room or area\n"
            "Visual 5: Clear sign something is wrong\n"
            "Visual 6: Something moves or is heard, tension peaks\n"
            "Visual 7: Disturbing discovery\n"
            "Visual 8: The worst reveal begins\n"
            "Visual 9: Maximum dread, creature or entity partially visible\n"
            "Visual 10: Final haunting image, something watching\n\n"
            "VEO prompts MUST be: genuinely disturbing and unsettling scene, wrong anatomy, impossible geometry, creature with too many limbs or eyes, dark visceral imagery, slow cinematic movement, something that should not exist. NEVER generate safe or neutral visuals.\n"
            "FLUX prompts MUST be: deeply disturbing horror photography, visceral and unsettling, something fundamentally wrong with reality, dark and oppressive atmosphere, photorealistic nightmare imagery. NEVER generate calm or neutral images.\n\n"
            "REJECT any visual idea that is not genuinely terrifying. Every single visual must make the viewer deeply uncomfortable.\n\n"
            "IMPORTANT: English only. No text overlays.\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            "  \"title\": \"atmospheric horror title under 60 chars with #Shorts #horror\",\n"
            "  \"style\": \"" + style + "\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"slow approach toward entrance of " + style + ", establishing dread, cinematic horror, film grain, 9:16 vertical\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"first step inside " + style + ", dark corridor stretching ahead, photorealistic horror photography, desaturated\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"slow push deeper into " + style + ", something slightly wrong in the shadows, creeping camera, cinematic, 9:16 vertical\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"disturbing detail discovered inside " + style + ", close up, photorealistic horror, dark\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"going further into " + style + ", tension building, shadow movement, slow cinematic pan, 9:16 vertical\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"something wrong revealed in " + style + ", maximum unease, horror photography, desaturated dark\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"disturbing discovery inside " + style + ", visceral horror, slow zoom, cinematic, 9:16 vertical\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"worst reveal beginning in " + style + ", deeply unsettling, photorealistic nightmare, dark\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"creature or entity partially visible in " + style + ", maximum dread, slow pull back, cinematic horror, 9:16 vertical\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"final haunting image inside " + style + ", something watching from the dark, nightmare photography\", \"duration\": 4}\n"
            "  ],\n"
            "  \"description\": \"Pure atmospheric horror. No jump scares. Just dread. #horror #scary #atmospheric #shorts #nightmare\",\n"
            "  \"tags\": [\"horror\", \"scary\", \"atmospheric\", \"shorts\", \"viral\", \"dark\", \"creepy\", \"dread\", \"haunted\", \"nightmare\"]\n"
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
                    {"type": "VEO", "prompt": "slow approach toward entrance of " + style + ", establishing dread, cinematic horror, film grain, 9:16 vertical", "duration": 5},
                    {"type": "FLUX", "prompt": "first step inside " + style + ", dark corridor, photorealistic horror photography, desaturated", "duration": 4},
                    {"type": "VEO", "prompt": "slow push deeper into " + style + ", shadows, creeping camera, cinematic, 9:16 vertical", "duration": 5},
                    {"type": "FLUX", "prompt": "disturbing detail inside " + style + ", close up, photorealistic horror, dark", "duration": 4},
                    {"type": "VEO", "prompt": "going further into " + style + ", tension building, slow pan, cinematic, 9:16 vertical", "duration": 5},
                    {"type": "FLUX", "prompt": "something wrong in " + style + ", maximum unease, horror photography, dark", "duration": 4},
                    {"type": "VEO", "prompt": "disturbing discovery in " + style + ", visceral horror, slow zoom, cinematic, 9:16 vertical", "duration": 5},
                    {"type": "FLUX", "prompt": "worst reveal in " + style + ", deeply unsettling, nightmare photography, dark", "duration": 4},
                    {"type": "VEO", "prompt": "creature partially visible in " + style + ", maximum dread, slow pull back, cinematic, 9:16 vertical", "duration": 5},
                    {"type": "FLUX", "prompt": "final haunting image " + style + ", something watching from dark, nightmare photography", "duration": 4}
                ],
                "description": "Pure atmospheric horror. No jump scares. Just dread. #horror #scary #atmospheric #shorts #nightmare",
                "tags": ["horror", "scary", "atmospheric", "shorts", "viral", "dark", "creepy", "dread", "haunted", "nightmare"]
            }

        video_data["niche"] = "horror"
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on atmospheric horror content."
