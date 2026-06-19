import json
import random
import os


HORROR_LOCATIONS = [
    "dark forest road with a single streetlight, impossibly tall creature standing beneath it",
    "abandoned mental asylum corridor at 3am, something crawling on the ceiling",
    "empty hospital room with a figure standing motionless in the corner",
    "dense fog covered cemetery, pale hands rising from the ground",
    "dark lake at midnight, something enormous moving just beneath the surface",
    "abandoned Soviet bunker, glowing eyes watching from the ventilation shaft",
    "old Victorian mansion hallway, mirrors showing wrong reflections",
    "empty subway tunnel, something breathing heavily in the darkness ahead",
    "flooded basement, pale figure standing completely still in black water",
    "dark mountain road, creature with broken limbs crawling toward the camera",
    "abandoned carnival at night, clown figure that should not be moving",
    "empty church with black candles, faceless congregation sitting in pews",
    "nuclear plant ruins, glowing humanoid figure walking through walls",
    "dense dark forest, dozens of eyes watching from between the trees",
    "empty school hallway at 4am, child standing at the far end facing away",
]

NIGHTMARE_SCENARIOS = [
    "you are running through an endless dark corridor that keeps getting longer, something follows",
    "you look in a mirror and your reflection does not move with you",
    "you are falling through infinite darkness and something is falling with you",
    "you are in your childhood home but every door leads to the same dark room",
    "you try to scream but no sound comes out, a figure gets closer",
    "you are underwater and cannot find the surface, something swims below",
    "you wake up in a dark room and realize you cannot move, a shadow approaches",
    "you are being chased through fog so thick you cannot see your hands",
    "you are in a familiar place but everyone you know has wrong faces",
    "you open a door and there is nothing behind it except infinite void",
    "you are climbing stairs that never end, something is climbing behind you",
    "you are in a dream within a dream, each layer darker than the last",
    "you are standing in a field at night, the stars begin going out one by one",
    "you reach out to touch someone and they turn to face you, it is not human",
    "you realize you have been sleepwalking and are standing at the edge of something",
]

CHARACTER_SCENARIOS = [
    "terrified Asian woman with flashlight exploring abandoned hospital, discovers something moving",
    "young man investigating strange sounds in his basement with a phone flashlight, finds something",
    "woman waking up at 3am seeing a dark figure standing in her bedroom doorway",
    "security guard doing night rounds in empty office building, cameras show something on floor 7",
    "woman in bathtub realizes the water has turned black and something is pulling her down",
    "man driving on empty night highway sees something wrong standing in the road ahead",
    "woman home alone hears her name whispered from inside the walls",
    "child wakes up and sees their reflection in the window is not copying their movements",
    "woman looking through old photos finds one where someone is standing behind her",
    "man hears knocking from inside his closet, opens it and finds it leads somewhere impossible",
    "nurse doing late shift discovers a patient room that should not exist on that floor",
    "woman FaceTiming a friend realizes the background behind them is not their home",
    "man looks out window at 3am and sees himself standing in the street looking back up",
    "woman in shower hears the bathroom door slowly open, then silence",
    "detective investigating disappearances finds a mirror that shows who was last in the room",
]

CREATURES = [
    "impossibly tall figure with elongated limbs bent the wrong way, no face, just smooth skin",
    "creature made entirely of shadow that absorbs light around it, dozens of eyes",
    "humanoid with too many joints, moves like a broken marionette, jaw unhinged",
    "pale woman with black void eyes, hair covering face, crawls on ceiling",
    "massive spider-like entity with a human torso where the head should be",
    "figure with hands where its feet should be, walking on all fours backwards",
    "translucent entity, internal organs visible and still moving, no skin",
    "creature with a mouth that opens vertically across its entire face",
    "child-sized figure with adult hands, moves in jerky stop-motion way",
    "entity made of static and distortion, flickers in and out of reality",
    "tall hooded figure with fingers 3 feet long that drag on the ground",
    "woman whose body is slowly folding inward like paper, still alive",
    "creature with a second face on the back of its head, both screaming silently",
    "figure standing perfectly still, moves only when not being looked at directly",
    "mass of black tendrils forming a vaguely human shape, constantly shifting",
    "entity with no lower body, just a torso dragging itself with broken arms",
    "creature whose reflection does not match its movements, reflection attacks",
    "pale humanoid with no eyes or mouth, just smooth featureless skin, tilts head",
    "entity that looks exactly like a normal person but always slightly out of focus",
    "figure with limbs that extend impossibly, reaching across the room from the doorway",
]

FORMAT_SEQUENCE_FILE = "format_sequence.json"


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def _get_next_format(self):
        try:
            with open(FORMAT_SEQUENCE_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = {"index": 0}
        
        formats = ["HORROR", "NIGHTMARE", "CHARACTER"]
        current_index = data.get("index", 0)
        current_format = formats[current_index % 3]
        
        data["index"] = (current_index + 1) % 3
        with open(FORMAT_SEQUENCE_FILE, "w") as f:
            json.dump(data, f)
        
        return current_format

    def _get_unused_scenario(self, scenario_list, used_key):
        used_file = "used_" + used_key + ".json"
        try:
            with open(used_file, "r") as f:
                used = json.load(f)
        except Exception:
            used = []
        
        available = [s for s in scenario_list if s not in used]
        if not available:
            used = []
            available = scenario_list
        
        chosen = random.choice(available)
        used.append(chosen)
        with open(used_file, "w") as f:
            json.dump(used, f)
        return chosen

    def generate_video(self, niche=None, analytics_data=None, used_concepts=None):
        fmt = self._get_next_format()
        print("Format: " + fmt)

        if fmt == "HORROR":
            return self._generate_horror()
        elif fmt == "NIGHTMARE":
            return self._generate_nightmare()
        else:
            return self._generate_character()

    def _generate_horror(self):
        scenario = self._get_unused_scenario(HORROR_LOCATIONS, "horror")
        print("Scenario: " + scenario[:60])
        creature = random.choice(CREATURES)
        print("Creature: " + creature[:60])
        prompt = (
            "Create 8 cinematic horror visuals for a 35-second YouTube Shorts video.\n\n"
            "Scenario: " + scenario + "\n\n"
            "RULES:\n"
            "- Featured creature: " + creature + "\n"
            "- Creature HIDDEN for first 20 seconds — only shadows, glimpses, wrong shapes\n"
            "- Creature PARTIALLY REVEALED at second 25\n"
            "- Creature FULLY VISIBLE at final shot — maximum terror\n"
            "- All visuals in the SAME location, continuous journey\n"
            "- NO dialogue, NO text, NO subtitles\n"
            "- Desaturated cold blue-grey color palette throughout\n"
            "- Start with establishing dread, end with maximum terror\n"
            "- Creature must be visible but partially hidden — never fully revealed until end\n"
            "- Wrong anatomy: too tall, too many joints, limbs bent wrong way\n"
            "- Slow creeping camera movements only\n\n"
            "VEO: slow cinematic push/pull/tilt, creature movement barely visible, "
            "film grain, cold desaturated, 9:16 vertical\n"
            "FLUX: photorealistic horror photography, something deeply wrong, "
            "cold blue-grey, dark shadows, wrong anatomy visible\n\n"
            "Return ONLY JSON:\n"
            "{\n"
            "  \"title\": \"creepy horror title under 50 chars #Shorts #horror #creepy\",\n"
            "  \"format\": \"HORROR\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4}\n"
            "  ],\n"
            "  \"description\": \"#horror #creepy #scary #nightmare #dark #shorts #viral #cursed #ghost #creature\",\n"
            "  \"tags\": [\"horror\", \"creepy\", \"scary\", \"nightmare\", \"dark\", \"shorts\", \"viral\", \"cursed\", \"ghost\", \"creature\"]\n"
            "}\n\nNo markdown, raw JSON only."
        )

        return self._call_claude(prompt, "HORROR", scenario)

    def _generate_nightmare(self):
        scenario = self._get_unused_scenario(NIGHTMARE_SCENARIOS, "nightmare")
        print("Scenario: " + scenario[:60])
        creature = random.choice(CREATURES)
        print("Creature: " + creature[:60])
        prompt = (
            "Create 8 cinematic nightmare POV visuals for a 35-second YouTube Shorts video.\n\n"
            "Nightmare scenario: " + scenario + "\n\n"
            "RULES:\n"
            "- The nightmare creature: " + creature + "\n"
            "- Creature barely glimpsed in first 20 seconds — peripheral vision only\n"
            "- Creature gets closer each shot\n"
            "- Final shot: creature face to face with viewer POV — inescapable\n"
            "- First person POV — viewer IS the person in the dream\n"
            "- Everything slightly wrong, reality distorting\n"
            "- NO dialogue, NO text, NO subtitles\n"
            "- Dreamlike but terrifying — colors desaturated and wrong\n"
            "- Camera movement mimics someone running, looking around, panicking\n"
            "- Each shot feels like next moment in the same nightmare\n"
            "- End with the most terrifying reveal\n\n"
            "VEO: first person POV camera, shaky/running/turning movement, "
            "dreamlike distortion, desaturated wrong colors, 9:16 vertical\n"
            "FLUX: POV nightmare still, reality slightly melting, "
            "something wrong in every corner, photorealistic nightmare\n\n"
            "Return ONLY JSON:\n"
            "{\n"
            "  \"title\": \"nightmare POV title under 50 chars #Shorts #nightmare #dream\",\n"
            "  \"format\": \"NIGHTMARE\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4}\n"
            "  ],\n"
            "  \"description\": \"#nightmare #dream #horror #scary #pov #shorts #viral #creepy #dark #sleep\",\n"
            "  \"tags\": [\"nightmare\", \"dream\", \"horror\", \"scary\", \"pov\", \"shorts\", \"viral\", \"creepy\", \"dark\", \"sleep\"]\n"
            "}\n\nNo markdown, raw JSON only."
        )

        return self._call_claude(prompt, "NIGHTMARE", scenario)

    def _generate_character(self):
        scenario = self._get_unused_scenario(CHARACTER_SCENARIOS, "character")
        print("Scenario: " + scenario[:60])
        creature = random.choice(CREATURES)
        print("Creature: " + creature[:60])
        prompt = (
            "Create 8 cinematic horror visuals for a 35-second YouTube Shorts video.\n\n"
            "Character scenario: " + scenario + "\n\n"
            "RULES:\n"
            "- The entity stalking the character: " + creature + "\n"
            "- Entity invisible for first 20 seconds — character senses it but we dont see it\n"
            "- Entity glimpsed at second 20-25 — partial, shadowy, wrong\n"
            "- Entity fully revealed in final shot — character and viewer see it at same time\n"
            "- Realistic human character visible throughout — photorealistic, not cartoon\n"
            "- Character shows extreme fear: trembling, sweating, wide eyes, pale\n"
            "- NO dialogue, NO text, NO subtitles\n"
            "- Cold desaturated color palette, cinematic horror film look\n"
            "- Mix of character close-ups and wide shots showing their environment\n"
            "- The horror is revealed gradually — character reacts before we see what\n"
            "- End with the most shocking reveal\n\n"
            "VEO: photorealistic terrified human character, cinematic camera, "
            "horror film lighting, slow push/pull, desaturated cold, 9:16 vertical\n"
            "FLUX: photorealistic horror film still, character extreme fear expression, "
            "cinematic composition, cold blue-grey, dramatic shadows\n\n"
            "Return ONLY JSON:\n"
            "{\n"
            "  \"title\": \"character horror title under 50 chars #Shorts #horror #scary\",\n"
            "  \"format\": \"CHARACTER\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4}\n"
            "  ],\n"
            "  \"description\": \"#horror #scary #creepy #dark #shorts #viral #nightmare #ghost #cursed #fear\",\n"
            "  \"tags\": [\"horror\", \"scary\", \"creepy\", \"dark\", \"shorts\", \"viral\", \"nightmare\", \"ghost\", \"cursed\", \"fear\"]\n"
            "}\n\nNo markdown, raw JSON only."
        )

        return self._call_claude(prompt, "CHARACTER", scenario)

    def _call_claude(self, prompt, fmt, scenario):
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
                "title": "Something Is Out There #Shorts #horror #creepy",
                "format": fmt,
                "visuals": [
                    {"type": "VEO", "prompt": "slow cinematic establishing horror shot, dark desaturated, cold blue-grey, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "photorealistic horror still, something wrong, cold desaturated, dark shadows", "duration": 4},
                    {"type": "VEO", "prompt": "slow push forward into darkness, horror, desaturated cold, 9:16 vertical", "duration": 5},
                    {"type": "FLUX", "prompt": "disturbing detail, photorealistic horror, cold blue-grey", "duration": 4},
                    {"type": "VEO", "prompt": "tension peaks, something moves, slow zoom, horror, 9:16 vertical", "duration": 5},
                    {"type": "FLUX", "prompt": "maximum unease, horror photography, dark cold", "duration": 4},
                    {"type": "VEO", "prompt": "reveal begins, horror escalates, cinematic, 9:16 vertical", "duration": 5},
                    {"type": "FLUX", "prompt": "final haunting image, something watching, dark horror", "duration": 4}
                ],
                "description": "#horror #creepy #scary #nightmare #dark #shorts #viral #cursed #ghost #creature",
                "tags": ["horror", "creepy", "scary", "nightmare", "dark", "shorts", "viral", "cursed", "ghost", "creature"]
            }

        video_data["niche"] = "horror"
        video_data["scenario"] = scenario
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on rotating horror formats."
