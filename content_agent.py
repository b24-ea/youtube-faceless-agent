import json
import random


prompt = (
            "You are creating a viral atmospheric horror YouTube Shorts video.\n\n"
            "Style: " + style + "\n"
            "Mood: " + mood + "\n\n"
            "Create 8 cinematic horror visuals for a 30-second video.\n"
            "IMPORTANT: All 8 visuals must take place in the SAME location: " + style + "\n"
            "The video tells ONE continuous horror story in this single location.\n"
            "Camera slowly explores deeper into the location — like a found footage journey.\n"
            "Each visual is the next moment in the same continuous scene.\n"
            "NO dialogue, NO narration, NO text on screen.\n"
            "ONLY pure atmospheric horror visuals.\n"
            "Mix of VEO (video clips) and FLUX (still images).\n"
            "Build tension progressively — start unsettling, end terrifying.\n\n"
            "Story structure:\n"
            "Visual 1: Exterior or entrance of " + style + " — establishing dread\n"
            "Visual 2: First step inside — dark corridor or entry\n"
            "Visual 3: Something slightly wrong noticed — subtle detail\n"
            "Visual 4: Going deeper — another room or area\n"
            "Visual 5: Clear sign something is wrong — disturbing discovery\n"
            "Visual 6: Something moves or is heard — tension peaks\n"
            "Visual 7: The worst reveal — maximum dread\n"
            "Visual 8: Final haunting image — something watching\n\n"
            "VEO prompts must have:\n"
            "- Slow, creeping camera movements (push in, tilt, pan)\n"
            "- Subtle movement (shadows shifting, dust falling, door moving)\n"
            "- Continuous with previous shot — same location, next moment\n"
            "- Cinematic dark lighting, film grain\n\n"
            "FLUX prompts must have:\n"
            "- Same location, different angle or detail\n"
            "- Something slightly wrong in the image\n"
            "- Dark, desaturated, photorealistic horror photography\n\n"
            "IMPORTANT: English only. No text overlays.\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            "  \"title\": \"atmospheric horror title about " + style + " under 60 chars with #Shorts #horror\",\n"
            "  \"style\": \"" + style + "\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"slow approach toward entrance of " + style + ", establishing dread, cinematic horror, film grain, 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"first step inside " + style + ", dark corridor stretching ahead, photorealistic horror photography, desaturated\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"slow push deeper into " + style + ", something slightly wrong in the shadows, creeping camera, cinematic, 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"disturbing detail discovered inside " + style + ", close up, photorealistic horror, dark\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"going further into " + style + ", tension

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
            "NO dialogue, NO narration, NO text on screen.\n"
            "ONLY pure atmospheric horror visuals.\n"
            "Mix of VEO (video clips) and FLUX (still images).\n"
            "Every 3-4 seconds a new visual.\n"
            "Build tension from start to finish — start unsettling, end terrifying.\n\n"
            "VEO prompts must have:\n"
            "- Slow, creeping camera movements\n"
            "- Subtle movement (shadows shifting, water dripping, door creaking)\n"
            "- No sudden jump scares — slow building dread\n"
            "- Cinematic dark lighting\n\n"
            "FLUX prompts must have:\n"
            "- Extreme atmospheric detail\n"
            "- Something slightly wrong in the image\n"
            "- Dark, desaturated colors\n"
            "- Photorealistic horror photography style\n\n"
            "IMPORTANT: English only. No text overlays in prompts.\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            "  \"title\": \"atmospheric horror title under 60 chars with #Shorts #horror\",\n"
            "  \"style\": \"" + style + "\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"slow creeping camera push into " + style + ", cinematic horror, dark atmosphere, 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"extreme detail shot of " + style + ", something slightly wrong, photorealistic horror, dark desaturated\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"slow tilt up revealing " + style + ", shadow movement, dread, cinematic, 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"wide shot of " + style + ", unsettling details, horror photography, dark\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"something moves in the dark of " + style + ", barely visible, slow zoom, cinematic horror, 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"close up detail " + style + ", disturbing element, photorealistic, horror\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"final reveal in " + style + ", maximum dread, slow camera pull back, cinematic, 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"haunting final image of " + style + ", something watching, horror photography, dark atmosphere\", \"duration\": 3}\n"
            "  ],\n"
            "  \"description\": \"Pure atmospheric horror. No jump scares. Just dread. #horror #scary #atmospheric #shorts\",\n"
            "  \"tags\": [\"horror\", \"scary\", \"atmospheric\", \"shorts\", \"viral\", \"dark\", \"creepy\", \"dread\", \"haunted\", \"terror\"]\n"
            "}\n\n"
            "No markdown, raw JSON only. Make every visual genuinely unsettling."
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
                    {"type": "VEO", "prompt": "slow creeping camera push into " + style + ", cinematic horror, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "extreme detail " + style + ", something wrong, photorealistic horror, dark", "duration": 3},
                    {"type": "VEO", "prompt": "shadow movement in " + style + ", slow zoom, dread, cinematic, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "wide shot " + style + ", unsettling, horror photography", "duration": 3},
                    {"type": "VEO", "prompt": "something moves in " + style + ", barely visible, cinematic horror, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "close up " + style + ", disturbing, photorealistic horror", "duration": 3},
                    {"type": "VEO", "prompt": "final reveal " + style + ", maximum dread, pull back, cinematic, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "haunting final image " + style + ", something watching, horror photography", "duration": 3}
                ],
                "description": "Pure atmospheric horror. No jump scares. Just dread. #horror #scary #atmospheric #shorts",
                "tags": ["horror", "scary", "atmospheric", "shorts", "viral", "dark", "creepy", "dread", "haunted", "terror"]
            }

        video_data["niche"] = "horror"
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on atmospheric horror content."
