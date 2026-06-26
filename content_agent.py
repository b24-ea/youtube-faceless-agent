import json
import random
import os


# 30 senaryo sablonu - dongusel calisir (1->30->1->...)
# Her seferinde Claude ayni sablon uzerinde FARKLI icerik/taktik/aci uretir
SCENARIO_TEMPLATES = [
    "someone ignores your messages or leaves you on read",
    "someone talks down to you or belittles you in front of others",
    "someone uses guilt to control your decisions",
    "someone gives you the silent treatment to punish you",
    "someone constantly cancels plans last minute",
    "someone tries to make you jealous on purpose",
    "someone love bombs you then suddenly goes cold",
    "someone gaslights you into doubting your own memory",
    "someone only reaches out when they need something from you",
    "someone disrespects your boundaries repeatedly",
    "someone compares you to other people to control you",
    "someone uses your kindness against you",
    "someone tries to rush you into a decision or commitment",
    "someone publicly disrespects you to seem powerful",
    "someone plays mind games to keep you uncertain",
    "someone takes credit for your work or ideas",
    "someone uses your insecurities against you",
    "someone tests your limits to see what they can get away with",
    "someone gives fake apologies with no real change",
    "someone tries to isolate you from your support system",
    "someone constantly interrupts or talks over you",
    "someone makes everything about themselves in every conversation",
    "someone uses passive aggression instead of direct communication",
    "someone flirts with others in front of you to get a reaction",
    "someone dismisses your feelings and calls you too sensitive",
    "someone spreads rumors or talks behind your back",
    "someone never takes responsibility and always blames others",
    "someone withdraws affection when they don't get what they want",
    "someone constantly needs validation but never gives it back",
    "someone makes you feel lucky to have them while treating you poorly",
]

# Gorsel sahneler - script konusuyla eslesmiyor
# cesitli korku unsurlari: yaratiklar, hayaletler, garip varliklar, siradisi mekanlar
HORROR_CREATURES = [
    "impossibly tall figure with elongated limbs bent the wrong way, no face, just smooth skin, standing in darkness",
    "creature made entirely of shadow that absorbs light around it, dozens of eyes, lurking in a dark forest",
    "humanoid with too many joints, moves like a broken marionette, jaw unhinged, crawling in an abandoned building",
    "pale woman with black void eyes, hair covering face, crawling on a ceiling in a dark hallway",
    "massive spider-like entity with a human torso where the head should be, deep in a dark forest",
    "figure with hands where its feet should be, walking on all fours backwards through fog",
    "translucent entity, internal organs visible and still moving, no skin, standing motionless in shadow",
    "creature with a mouth that opens vertically across its entire face, emerging from darkness",
    "tall hooded figure with fingers 3 feet long that drag on the ground, walking through a dark forest road",
    "creature with a second face on the back of its head, both screaming silently, in an abandoned asylum",
    "mass of black tendrils forming a vaguely human shape, constantly shifting, in a flooded basement",
    "entity with no lower body, just a torso dragging itself with broken arms, in a dark tunnel",
    "pale humanoid with no eyes or mouth, just smooth featureless skin, tilting head, standing in fog",
    "figure with limbs that extend impossibly, reaching across a dark room from a doorway",
    "massive horned creature with glowing eyes, standing motionless deep in a dense dark forest",
    "translucent ghostly woman in a tattered white dress, floating slightly above the ground, glowing faintly in the dark",
    "semi-transparent spectral figure standing perfectly still in an old abandoned bedroom, cold blue glow",
    "ghostly child silhouette flickering in and out of visibility at the end of a dark hallway",
    "apparition of a man made of mist and static, walking through a wall, barely visible",
    "pale glowing spirit hovering near the ceiling of an empty attic, distorted and flickering like old film",
    "ghostly figure reflected in an antique mirror, not present in the room itself, reaching through the glass",
    "spectral hands emerging from a wall, faint and translucent, fingers grasping at the air",
    "impossible geometric shape hovering in the air, edges that hurt to look at, glitching reality around it",
    "swarm of black moths forming a humanoid silhouette in a dark room, slowly dispersing and reforming",
    "old television static forming a face that turns to look directly at camera, in a dark living room",
    "deer with too many legs and a human eye standing motionless at the edge of a dark forest",
    "floating mass of eyes blinking in unison, suspended in the darkness of an empty room",
    "shadow on the wall that moves independently of any person casting it, in a dimly lit corridor",
    "doll-like figure with cracked porcelain skin sitting upright in a dark abandoned nursery, head slowly turning",
    "water rising from cracks in the floor forming a humanoid shape, dripping black liquid, in a dark basement",
]

HORROR_LOCATIONS = [
    "dark forest road at night with a single streetlight, dense fog rolling between the trees",
    "abandoned asylum corridor at 3am, flickering lights, something crawling on the ceiling far away",
    "dense dark forest at night, moonlight barely breaking through the thick canopy",
    "abandoned Soviet bunker, dripping water, dim emergency lighting, long dark corridors",
    "empty subway tunnel, distant flickering lights, deep darkness ahead",
    "flooded basement, pale moonlight from a broken window, black standing water",
    "dark mountain road at night, headlights cutting through heavy fog",
    "abandoned carnival at night, broken rides silhouetted against a stormy sky",
    "empty church with rows of pews, candles flickering, deep shadows in the rafters",
    "dense dark forest, fog low to the ground, twisted bare trees",
    "old Victorian mansion hallway at night, long shadows, a single dim chandelier",
    "abandoned hospital room, flickering fluorescent light, peeling walls",
    "dark lake at midnight, mist rising off the still black water",
    "empty school hallway at 4am, lockers lining the walls, one light flickering",
    "nuclear plant ruins at night, broken machinery, eerie green emergency glow",
    "abandoned funhouse hall of mirrors, distorted reflections multiplying into infinity, dim red light",
    "endless empty parking garage at night, flickering fluorescent lights stretching into darkness",
    "old attic filled with covered furniture under white sheets, single shaft of moonlight",
    "abandoned amusement park ferris wheel at night, slowly turning with no operator, fog at its base",
    "empty elevator with mismatched floor numbers, doors opening to total darkness",
    "decrepit greenhouse at night, dead plants reaching upward, broken glass panels letting in moonlight",
    "long abandoned motel hallway, all doors slightly ajar, flickering neon sign visible through a window",
    "underground tunnel system with strange symbols carved into the walls, single dim work light",
    "abandoned lighthouse interior at night, spiral staircase disappearing into darkness above",
    "old cemetery at midnight, fog pooling between leaning gravestones, a single open grave",
]

SCENARIO_INDEX_FILE = "scenario_index.json"


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def _get_next_scenario(self):
        """Dongusel senaryo secimi - 30 sablon sirayla gider, basa doner"""
        try:
            with open(SCENARIO_INDEX_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = {"index": 0}

        current_index = data.get("index", 0) % len(SCENARIO_TEMPLATES)
        scenario = SCENARIO_TEMPLATES[current_index]

        data["index"] = (current_index + 1) % len(SCENARIO_TEMPLATES)
        with open(SCENARIO_INDEX_FILE, "w") as f:
            json.dump(data, f)

        print("Scenario #" + str(current_index + 1) + "/" + str(len(SCENARIO_TEMPLATES)) + ": " + scenario[:50])
        return scenario, current_index

    def get_horror_visuals(self, target_duration, max_visual_duration=4):
        """
        target_duration'a gore gorsel sayisini hesaplar.
        Her gorsel max_visual_duration kadar surer.
        Script'ten bagimsiz korku/hayalet/siradisi gorseller secilir.
        """
        count = max(2, round(target_duration / max_visual_duration))

        # Her 3 gorselden en az 1 lokasyon, kalanlar yaratik/hayalet olsun
        visuals = []
        for i in range(count):
            if i % 3 == 2:
                base = random.choice(HORROR_LOCATIONS)
            else:
                base = random.choice(HORROR_CREATURES)

            visual_type = "VEO" if i % 2 == 0 else "FLUX"
            duration = max_visual_duration

            if visual_type == "VEO":
                prompt = (
                    "Cinematic horror short film shot. Scene: " + base + ". "
                    "Ultra slow camera push, cold desaturated blue-black, deep shadows, "
                    "unsettling atmosphere, photorealistic, 9:16 vertical, no visible faces."
                )
            else:
                prompt = (
                    "Photorealistic horror film still. Scene: " + base + ". "
                    "Cold desaturated blue-grey, deep shadows, cinematic composition, "
                    "something deeply wrong visible, 9:16 vertical."
                )

            visuals.append({"type": visual_type, "prompt": prompt, "duration": duration})

        return visuals

    def generate_video(self, niche=None, analytics_data=None, used_concepts=None):
        scenario, scenario_index = self._get_next_scenario()

        prompt = (
            "You are writing a voiceover script for a YouTube Shorts video about psychology and "
            "self-respect tactics. The video teaches people how to respond with confidence when "
            "someone treats them badly.\n\n"
            "SCENARIO TEMPLATE: " + scenario + "\n\n"
            "IMPORTANT: This exact scenario template has been used before. You MUST create a "
            "COMPLETELY FRESH angle, tactic, and hook for it. Think of a NEW psychological insight, "
            "a different tactical approach, or an unexpected perspective that hasn't been covered. "
            "The situation is the same but the lesson, the tactic name, and the advice must be "
            "original and different from any previous video on this topic.\n\n"
            "Some angles to consider (pick one that feels fresh and unexpected):\n"
            "- The counterintuitive response most people would never think of\n"
            "- The psychological reason WHY people do this (and how knowing it gives you power)\n"
            "- The one thing you should NEVER do in this situation (and what to do instead)\n"
            "- The long-term strategy vs the short-term emotional reaction\n"
            "- What your response reveals about YOU vs what it reveals about THEM\n\n"
            "SCRIPT RULES — STRICT 4-PART STRUCTURE, TOTAL 25-30 SECONDS (roughly 70-85 words):\n"
            "1. HOOK (0-6s, 1-2 short sentences): State the exact situation bluntly. Must instantly "
            "make the viewer think 'this is literally happening to me right now'.\n"
            "2. CURIOSITY GAP (6-10s, 1-2 short sentences): Say that most people respond the wrong "
            "way and it backfires. Do NOT reveal the solution yet.\n"
            "3. SOLUTION (10-23s, 3-4 punchy sentences): Deliver the actual tactic clearly and "
            "specifically. Concrete, actionable, expert-level insight.\n"
            "4. CLOSING LINE (23-29s, 1 short sentence): Sharp, memorable, slightly dark. Quotable.\n\n"
            "- Tone: calm, controlled, slightly dark — a strategist, not a cheerleader.\n"
            "- Use 'you' directly. Short sentences. No filler words.\n"
            "- Do NOT use 'manipulate' or 'manipulation'.\n"
            "- Aim for the FULL 25-30 seconds — 70-85 words minimum.\n\n"
            "Return ONLY this JSON, no markdown:\n"
            "{\n"
            "  \"title\": \"under 50 chars, intriguing #Shorts\",\n"
            "  \"format\": \"PSYCHOLOGY\",\n"
            "  \"tactic_name\": \"your original tactic name\",\n"
            "  \"script\": \"the full voiceover script ready to be read aloud\",\n"
            "  \"description\": \"#psychology #selfrespect #mindset #shorts #viral #confidence #relationships #emotionalintelligence #growth #respect\",\n"
            "  \"tags\": [\"psychology\", \"selfrespect\", \"mindset\", \"shorts\", \"viral\", \"confidence\", \"relationships\", \"emotionalintelligence\", \"growth\", \"respect\"]\n"
            "}"
        )

        return self._call_claude(prompt, scenario, scenario_index)

    def _call_claude(self, prompt, scenario, scenario_index):
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
                "title": "They're testing you. Here's what to do. #Shorts",
                "format": "PSYCHOLOGY",
                "tactic_name": "The Strategic Pause",
                "script": (
                    "If " + scenario + ", most people react immediately — and that's exactly what they want. "
                    "Reacting gives them control. Instead, go completely silent. "
                    "Not to punish them — to recalibrate yourself. "
                    "When you respond from a place of calm, not emotion, you become unreadable. "
                    "And an unreadable person is an untouchable person."
                ),
                "description": "#psychology #selfrespect #mindset #shorts #viral #confidence #relationships #emotionalintelligence #growth #respect",
                "tags": ["psychology", "selfrespect", "mindset", "shorts", "viral", "confidence", "relationships", "emotionalintelligence", "growth", "respect"]
            }

        video_data["niche"] = "psychology"
        video_data["scenario"] = scenario
        video_data["scenario_index"] = scenario_index
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on rotating psychology tactics."
