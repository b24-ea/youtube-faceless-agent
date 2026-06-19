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

TENSION_ARC = """
TENSION ARC — STRICTLY FOLLOW THIS 8-SHOT STRUCTURE:

SHOT 1 [HOOK - 0-4s]: Something is WRONG but not visible. The environment feels off.
  A detail that should not exist. No creature. Pure unease. Make the viewer ask "wait... what is that?"

SHOT 2 [MYSTERY - 4-8s]: A second wrong detail. Still no creature. The wrongness deepens.
  Something moved. Something changed. The viewer leans in.

SHOT 3 [FIRST SIGN - 8-13s]: A shadow. A shape. NOT the creature — just evidence it exists.
  A handprint. A silhouette. Eyes in the darkness. The viewer's heart rate rises.

SHOT 4 [DREAD - 13-17s]: The creature is ALMOST visible. Partially behind something.
  Wrong anatomy hinted — too tall, wrong number of limbs. Viewer knows something is there.

SHOT 5 [ESCALATION - 17-22s]: The creature MOVES. Still partially hidden but undeniably real.
  Camera shakes slightly. The environment reacts — lights flicker, water ripples, shadows shift.

SHOT 6 [CONFRONTATION - 22-27s]: Face to face moment. Creature partially revealed.
  Maximum dread. The viewer cannot look away. Something terrible is about to happen.

SHOT 7 [PEAK TERROR - 27-31s]: THE REVEAL. Creature fully visible. Wrong in every way.
  Maximum horror. Something the viewer will remember. Visceral, disturbing, inescapable.

SHOT 8 [AFTERMATH - 31-35s]: Silence. Then one final wrong detail.
  The creature is gone — but something has changed. The horror lingers. Cut to black.
"""


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
            "You are a master horror director creating a 35-second YouTube Shorts video.\n\n"
            "LOCATION: " + scenario + "\n"
            "CREATURE (keep mostly hidden until end): " + creature + "\n\n"
            + TENSION_ARC +
            "\nCINEMATIC RULES:\n"
            "- Color: Deep desaturated blue-black. Shadows dominate 80% of frame.\n"
            "- Lighting: Single cold light source. Everything else near-black.\n"
            "- Camera: Shots 1-4 ultra slow push. Shots 5-6 slight shake. Shots 7-8 static then cut.\n"
            "- Sound design (describe in prompts): distant dripping, low hum, silence before reveals.\n"
            "- Each prompt must describe EXACTLY what is in frame, where creature/wrongness is, camera angle.\n"
            "- NO text, NO dialogue, NO subtitles ever.\n\n"
            "VEO prompts: slow cinematic camera movement, specify direction and speed, 9:16 vertical\n"
            "FLUX prompts: photorealistic horror photography, specify exact composition and what is wrong\n\n"
            "Return ONLY this JSON, no markdown:\n"
            "{\n"
            "  \"title\": \"under 50 chars, creates dread, no clickbait #Shorts #horror #creepy\",\n"
            "  \"format\": \"HORROR\",\n"
            "  \"hook\": \"one sentence describing the first 4 seconds that will stop the scroll\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"detailed cinematic prompt\", \"duration\": 4, \"tension\": \"HOOK\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"detailed horror photography prompt\", \"duration\": 4, \"tension\": \"MYSTERY\"},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5, \"tension\": \"FIRST_SIGN\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4, \"tension\": \"DREAD\"},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5, \"tension\": \"ESCALATION\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4, \"tension\": \"CONFRONTATION\"},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5, \"tension\": \"PEAK_TERROR\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4, \"tension\": \"AFTERMATH\"}\n"
            "  ],\n"
            "  \"description\": \"#horror #creepy #scary #nightmare #dark #shorts #viral #cursed #ghost #creature\",\n"
            "  \"tags\": [\"horror\", \"creepy\", \"scary\", \"nightmare\", \"dark\", \"shorts\", \"viral\", \"cursed\", \"ghost\", \"creature\"]\n"
            "}"
        )

        return self._call_claude(prompt, "HORROR", scenario)

    def _generate_nightmare(self):
        scenario = self._get_unused_scenario(NIGHTMARE_SCENARIOS, "nightmare")
        print("Scenario: " + scenario[:60])
        creature = random.choice(CREATURES)
        print("Creature: " + creature[:60])

        prompt = (
            "You are a master horror director creating a 35-second nightmare POV YouTube Shorts video.\n\n"
            "NIGHTMARE: " + scenario + "\n"
            "THE THING PURSUING YOU: " + creature + "\n\n"
            + TENSION_ARC +
            "\nNIGHTMARE POV RULES:\n"
            "- Viewer IS the dreamer — first person perspective throughout.\n"
            "- Reality distorts progressively: shot 1 is 90% normal, shot 8 is pure nightmare.\n"
            "- Color shifts: shots 1-2 near-normal desaturated, shots 5-8 wrong impossible colors.\n"
            "- Camera: shots 1-3 slow breathing movement, shots 4-6 growing panic, shots 7-8 chaos.\n"
            "- The creature gets closer every shot. By shot 7 it fills the frame.\n"
            "- Each prompt describes exactly what the viewer sees through their own eyes.\n"
            "- NO text, NO dialogue, NO subtitles ever.\n\n"
            "VEO prompts: first person POV, specify head movement and what viewer sees, 9:16 vertical\n"
            "FLUX prompts: POV nightmare photography, reality distortion level, exact composition\n\n"
            "Return ONLY this JSON, no markdown:\n"
            "{\n"
            "  \"title\": \"under 50 chars, nightmare feeling, no clickbait #Shorts #nightmare #horror\",\n"
            "  \"format\": \"NIGHTMARE\",\n"
            "  \"hook\": \"one sentence: what does the viewer see in first 4 seconds that stops the scroll\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"detailed POV prompt\", \"duration\": 4, \"tension\": \"HOOK\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"detailed nightmare POV prompt\", \"duration\": 4, \"tension\": \"MYSTERY\"},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5, \"tension\": \"FIRST_SIGN\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4, \"tension\": \"DREAD\"},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5, \"tension\": \"ESCALATION\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4, \"tension\": \"CONFRONTATION\"},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5, \"tension\": \"PEAK_TERROR\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4, \"tension\": \"AFTERMATH\"}\n"
            "  ],\n"
            "  \"description\": \"#nightmare #dream #horror #scary #pov #shorts #viral #creepy #dark #sleep\",\n"
            "  \"tags\": [\"nightmare\", \"dream\", \"horror\", \"scary\", \"pov\", \"shorts\", \"viral\", \"creepy\", \"dark\", \"sleep\"]\n"
            "}"
        )

        return self._call_claude(prompt, "NIGHTMARE", scenario)

    def _generate_character(self):
        scenario = self._get_unused_scenario(CHARACTER_SCENARIOS, "character")
        print("Scenario: " + scenario[:60])
        creature = random.choice(CREATURES)
        print("Creature: " + creature[:60])

        prompt = (
            "You are a master horror director creating a 35-second character-driven horror YouTube Shorts video.\n\n"
            "CHARACTER SCENARIO: " + scenario + "\n"
            "THE ENTITY: " + creature + "\n\n"
            + TENSION_ARC +
            "\nCHARACTER HORROR RULES:\n"
            "- Character is photorealistic, visible throughout. We watch their fear build.\n"
            "- Shot 1: Character in normal state, but something behind them is wrong.\n"
            "- Shots 2-4: Character notices. Face transitions from confusion to fear to terror.\n"
            "- Shots 5-6: Character and entity in same frame. Character cannot escape.\n"
            "- Shot 7: Character's face at maximum terror as entity fully reveals.\n"
            "- Shot 8: Character gone. Only entity remains. Or vice versa.\n"
            "- Character fear must be readable: trembling hands, wide eyes, pale skin, frozen.\n"
            "- Color: cold blue-grey desaturated throughout. Entity darker than everything.\n"
            "- NO text, NO dialogue, NO subtitles ever.\n\n"
            "VEO prompts: cinematic camera, specify character position and entity position, 9:16 vertical\n"
            "FLUX prompts: horror film still, specify character emotion and where entity is in frame\n\n"
            "Return ONLY this JSON, no markdown:\n"
            "{\n"
            "  \"title\": \"under 50 chars, character horror feeling #Shorts #horror #scary\",\n"
            "  \"format\": \"CHARACTER\",\n"
            "  \"hook\": \"one sentence: what detail in first 4 seconds makes viewer unable to scroll away\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"detailed character + environment prompt\", \"duration\": 4, \"tension\": \"HOOK\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"detailed horror film still prompt\", \"duration\": 4, \"tension\": \"MYSTERY\"},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5, \"tension\": \"FIRST_SIGN\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4, \"tension\": \"DREAD\"},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5, \"tension\": \"ESCALATION\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4, \"tension\": \"CONFRONTATION\"},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 5, \"tension\": \"PEAK_TERROR\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 4, \"tension\": \"AFTERMATH\"}\n"
            "  ],\n"
            "  \"description\": \"#horror #scary #creepy #dark #shorts #viral #nightmare #ghost #cursed #fear\",\n"
            "  \"tags\": [\"horror\", \"scary\", \"creepy\", \"dark\", \"shorts\", \"viral\", \"nightmare\", \"ghost\", \"cursed\", \"fear\"]\n"
            "}"
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
                    {"type": "VEO", "prompt": "slow cinematic establishing horror shot, dark desaturated, cold blue-grey, 9:16 vertical", "duration": 4, "tension": "HOOK"},
                    {"type": "FLUX", "prompt": "photorealistic horror still, something wrong in the shadows, cold desaturated", "duration": 4, "tension": "MYSTERY"},
                    {"type": "VEO", "prompt": "slow push forward into darkness, shadow moves wrong, horror, 9:16 vertical", "duration": 5, "tension": "FIRST_SIGN"},
                    {"type": "FLUX", "prompt": "disturbing silhouette barely visible, photorealistic horror, cold blue-grey", "duration": 4, "tension": "DREAD"},
                    {"type": "VEO", "prompt": "tension peaks, creature movement, slight camera shake, horror, 9:16 vertical", "duration": 5, "tension": "ESCALATION"},
                    {"type": "FLUX", "prompt": "creature partially revealed, maximum unease, horror photography", "duration": 4, "tension": "CONFRONTATION"},
                    {"type": "VEO", "prompt": "full reveal, maximum horror, creature fills frame, 9:16 vertical", "duration": 5, "tension": "PEAK_TERROR"},
                    {"type": "FLUX", "prompt": "aftermath, silence, something wrong remains, dark horror", "duration": 4, "tension": "AFTERMATH"}
                ],
                "description": "#horror #creepy #scary #nightmare #dark #shorts #viral #cursed #ghost #creature",
                "tags": ["horror", "creepy", "scary", "nightmare", "dark", "shorts", "viral", "cursed", "ghost", "creature"]
            }

        video_data["niche"] = "horror"
        video_data["scenario"] = scenario
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on rotating horror formats."
