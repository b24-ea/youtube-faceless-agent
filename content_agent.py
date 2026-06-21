import json
import random
import os


# Sabit liste artik birebir kullanilmiyor - Claude'a ilham/stil ornegi olarak veriliyor.
# Claude her seferinde bunlardan FARKLI, kendi uydurdugu ozgun bir senaryo+taktik uretiyor.
TOPICS = [
    {
        "trigger": "someone constantly ignores your messages or leaves you on read",
        "tactic_name": "The Mirror Method"
    },
    {
        "trigger": "someone talks down to you or belittles you in front of others",
        "tactic_name": "The Silent Reset"
    },
    {
        "trigger": "someone uses guilt to control your decisions",
        "tactic_name": "The Detachment Frame"
    },
    {
        "trigger": "someone gives you the silent treatment to punish you",
        "tactic_name": "The Non-Reaction"
    },
    {
        "trigger": "someone constantly cancels plans last minute",
        "tactic_name": "The Value Shift"
    },
    {
        "trigger": "someone tries to make you jealous on purpose",
        "tactic_name": "The Unbothered Response"
    },
    {
        "trigger": "someone love bombs you then suddenly goes cold",
        "tactic_name": "The Pattern Recognition"
    },
    {
        "trigger": "someone gaslights you into doubting your own memory",
        "tactic_name": "The Evidence Anchor"
    },
    {
        "trigger": "someone only reaches out when they need something from you",
        "tactic_name": "The Reciprocity Test"
    },
    {
        "trigger": "someone disrespects your boundaries repeatedly",
        "tactic_name": "The Hard Line"
    },
    {
        "trigger": "someone compares you to other people to control you",
        "tactic_name": "The Comparison Immunity"
    },
    {
        "trigger": "someone uses your kindness against you",
        "tactic_name": "The Strategic Withdrawal"
    },
    {
        "trigger": "someone tries to rush you into a decision or commitment",
        "tactic_name": "The Time Delay"
    },
    {
        "trigger": "someone publicly disrespects you to seem powerful",
        "tactic_name": "The Calm Authority"
    },
    {
        "trigger": "someone plays mind games to keep you uncertain",
        "tactic_name": "The Certainty Shield"
    },
    {
        "trigger": "someone takes credit for your work or effort",
        "tactic_name": "The Quiet Documentation"
    },
    {
        "trigger": "someone uses your insecurities against you",
        "tactic_name": "The Neutral Ground"
    },
    {
        "trigger": "someone tests your limits to see what they can get away with",
        "tactic_name": "The Immediate Correction"
    },
    {
        "trigger": "someone manipulates you with fake apologies and no change",
        "tactic_name": "The Action Filter"
    },
    {
        "trigger": "someone tries to isolate you from your friends or family",
        "tactic_name": "The Outside Anchor"
    },
]


# Görseller artik script konusuyla eslesmiyor - eski korku formatindaki gibi
# bagimsiz, COK CESITLI korku unsurlari kullaniliyor: yaratiklar, hayaletler,
# garip varliklar, aciklanamayan fenomenler, surreal korku goruntuleri
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
    # Hayaletler
    "translucent ghostly woman in a tattered white dress, floating slightly above the ground, glowing faintly in the dark",
    "semi-transparent spectral figure standing perfectly still in an old abandoned bedroom, cold blue glow",
    "ghostly child silhouette flickering in and out of visibility at the end of a dark hallway",
    "apparition of a man made of mist and static, walking through a wall, barely visible",
    "pale glowing spirit hovering near the ceiling of an empty attic, distorted and flickering like old film",
    "ghostly figure reflected in an antique mirror, not present in the room itself, reaching through the glass",
    "spectral hands emerging from a wall, faint and translucent, fingers grasping at the air",
    # Garip / siradisi varliklar ve fenomenler
    "impossible geometric shape hovering in the air, edges that hurt to look at, glitching reality around it",
    "swarm of black moths forming a humanoid silhouette in a dark room, slowly dispersing and reforming",
    "old television static forming a face that turns to look directly at camera, in a dark living room",
    "deer with too many legs and a human eye standing motionless at the edge of a dark forest",
    "floating mass of eyes blinking in unison, suspended in the darkness of an empty room",
    "shadow on the wall that moves independently of any person casting it, in a dimly lit corridor",
    "doll-like figure with cracked porcelain skin sitting upright in a dark abandoned nursery, head slowly turning",
    "a second moon visible through a window, wrong color, pulsing faintly, something watching from below it",
    "water rising from cracks in the floor forming a humanoid shape, dripping black liquid, in a dark basement",
    "old photograph on a wall where the person's face slowly changes when not directly observed",
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
    # Daha siradisi / sureal mekanlar
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


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def _get_horror_visuals(self, count=3):
        """Script'ten bagimsiz, eski korku formatindaki gibi yaratik/karanlik sahne prompt'lari uretir"""
        visuals = []
        durations = [7, 8, 6][:count]

        for i in range(count):
            use_creature = random.random() < 0.6  # cogu zaman yaratik gorunsun
            if use_creature:
                creature = random.choice(HORROR_CREATURES)
                base = creature
            else:
                base = random.choice(HORROR_LOCATIONS)

            visual_type = "VEO" if i % 2 == 0 else "FLUX"

            if visual_type == "VEO":
                prompt = (
                    base + ". Cinematic horror, slow creeping camera movement, "
                    "cold desaturated blue-grey color palette, dark shadows, film grain, "
                    "9:16 vertical, no text, ominous atmosphere."
                )
            else:
                prompt = (
                    base + ". Photorealistic horror photography, dramatic lighting, "
                    "cold desaturated blue-grey tones, deep shadows, unsettling detail, "
                    "9:16 vertical, cinematic horror film still."
                )

            visuals.append({"type": visual_type, "prompt": prompt, "duration": durations[i]})

        return visuals

    def _get_inspiration_seed(self):
        """Sabit listeden rastgele birkac ornek secer - Claude bunlardan ilham alir, kopyalamaz"""
        sample = random.sample(TOPICS, k=min(4, len(TOPICS)))
        return sample

    def _get_recent_scenarios(self, limit=15):
        """Son uretilen senaryolarin ozetini getirir, boylece Claude tekrara dusmez"""
        history_file = "scenario_history.json"
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
        return history[-limit:]

    def _save_scenario_to_history(self, scenario_summary):
        history_file = "scenario_history.json"
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except Exception:
            history = []

        history.append(scenario_summary)
        history = history[-50:]
        with open(history_file, "w") as f:
            json.dump(history, f)

    def generate_video(self, niche=None, analytics_data=None, used_concepts=None):
        inspiration = self._get_inspiration_seed()
        recent = self._get_recent_scenarios()

        inspiration_text = "\n".join(
            "- " + t["trigger"] + " (style example: " + t["tactic_name"] + ")" for t in inspiration
        )
        recent_text = "\n".join("- " + r for r in recent) if recent else "(none yet, this is the first video)"

        prompt = (
            "You are writing a voiceover script for a YouTube Shorts video about psychology and "
            "self-respect tactics. The video teaches people how to respond with confidence when "
            "someone treats them badly.\n\n"
            "STEP 1 — Invent a fresh, specific situation and a named tactic for it.\n"
            "Use these only as loose inspiration for tone and style. Do NOT copy them word for word — "
            "invent your own specific situation and your own original tactic name:\n"
            + inspiration_text + "\n\n"
            "These situations were already used in recent videos — your new situation must be "
            "clearly different from all of these (different trigger, different relationship context, "
            "different angle):\n"
            + recent_text + "\n\n"
            "SCRIPT RULES — STRICT 4-PART STRUCTURE, TOTAL 15-25 SECONDS (roughly 40-55 words):\n"
            "1. HOOK (0-4s, 1 short sentence): State the exact situation bluntly. Must instantly make "
            "the viewer think 'this is literally happening to me right now'. No setup, no warmup — "
            "drop straight into it.\n"
            "2. CURIOSITY GAP (4-7s, 1 short sentence): Say that most people respond the wrong way and "
            "it backfires, WITHOUT yet revealing the correct response. Creates a 'wait, what should I "
            "do then?' itch that keeps them watching.\n"
            "3. SOLUTION (7-18s, 2-3 punchy sentences): Deliver the actual tactic clearly and "
            "specifically. Concrete and actionable, not vague self-help fluff — sound like an expert "
            "revealing an insider secret.\n"
            "4. CLOSING LINE (18-22s, 1 short sentence): A sharp, memorable, slightly dark/powerful "
            "statement that locks in the mindset shift. Should feel quotable, like a line people would "
            "screenshot.\n\n"
            "- Tone: calm, controlled, slightly dark and serious — like someone who has mastered "
            "emotional control speaking with quiet authority. NOT motivational-speaker energy. "
            "NOT cheerful. Think: a strategist, not a cheerleader.\n"
            "- Use 'you' directly. Short sentences. No filler words. No emojis in the script text.\n"
            "- Every single word must earn its place — this is a tight 15-25 second script, there is "
            "no room for warmup, repetition, or padding.\n"
            "- Do NOT use the words 'manipulate' or 'manipulation' — keep it framed as self-respect "
            "and emotional intelligence, not as scheming against others.\n\n"
            "Return ONLY this JSON, no markdown:\n"
            "{\n"
            "  \"title\": \"under 50 chars, intriguing, no clickbait spam #Shorts\",\n"
            "  \"format\": \"PSYCHOLOGY\",\n"
            "  \"situation_summary\": \"one short sentence summarizing the invented situation, for internal tracking only\",\n"
            "  \"tactic_name\": \"the original tactic name you invented\",\n"
            "  \"script\": \"the full voiceover script as one continuous text, ready to be read aloud\",\n"
            "  \"description\": \"#psychology #selfrespect #mindset #shorts #viral #confidence #relationships #emotionalintelligence #growth #respect\",\n"
            "  \"tags\": [\"psychology\", \"selfrespect\", \"mindset\", \"shorts\", \"viral\", \"confidence\", \"relationships\", \"emotionalintelligence\", \"growth\", \"respect\"]\n"
            "}"
        )

        return self._call_claude(prompt)

    def _call_claude(self, prompt):
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

        fallback_topic = random.choice(TOPICS)

        try:
            video_data = json.loads(content)
        except Exception:
            video_data = {
                "title": fallback_topic["tactic_name"] + " #Shorts",
                "format": "PSYCHOLOGY",
                "situation_summary": fallback_topic["trigger"],
                "tactic_name": fallback_topic["tactic_name"],
                "script": (
                    "If " + fallback_topic["trigger"] + ", do not react with emotion. "
                    "Most people respond the wrong way, and it backfires every time. "
                    "Stay completely silent and create distance instead. "
                    "When you stop reacting, you take back control. "
                    "Remove the reaction, and you remove their power."
                ),
                "description": "#psychology #selfrespect #mindset #shorts #viral #confidence #relationships #emotionalintelligence #growth #respect",
                "tags": ["psychology", "selfrespect", "mindset", "shorts", "viral", "confidence", "relationships", "emotionalintelligence", "growth", "respect"]
            }

        # Gorseller script'ten bagimsiz - eski korku formatindaki gibi
        # yaratik/karanlik orman havuzundan rastgele secilir
        video_data["visuals"] = self._get_horror_visuals(count=3)

        video_data["niche"] = "psychology"
        scenario_label = video_data.get("tactic_name") or video_data.get("title") or "unknown"
        video_data["scenario"] = scenario_label

        summary_for_history = video_data.get("situation_summary", "") + " (" + scenario_label + ")"
        self._save_scenario_to_history(summary_for_history)

        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on rotating psychology tactics."
