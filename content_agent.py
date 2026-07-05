import json
import random
import os
from datetime import datetime


# 30 senaryo sablonu - tarihe gore secilir, gunun saatine gore de kayar
# boylece ayni gunde 2 video paylasilinca ikisi de farkli sablon alir
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

# Zorla verilen bakis acisi - her cagirmada rastgele biri secilir,
# Claude'a "sadece bunu kullan" denir, boylece ayni senaryo tekrar gelse bile
# icerik yapisal olarak farkli olur
FORCED_ANGLES = [
    "the counterintuitive response most people would never think of",
    "the psychological reason WHY people do this, and how knowing it gives you power",
    "the one thing you should NEVER do in this situation, and what to do instead",
    "the long-term strategy vs the short-term emotional reaction",
    "what your response reveals about YOU vs what it reveals about THEM",
    "a real-world analogy that reframes the entire situation",
    "the exact phrase or action that shuts the behavior down immediately",
    "why reacting fast is the trap, and what patience actually does",
]

# Baslik yapisi cesitliligi - her seferinde farkli bir kalip zorlanir
TITLE_STYLES = [
    "a short direct statement (e.g. 'Stop Replying To Silence')",
    "a question that creates curiosity (e.g. 'Why Do They Go Quiet?')",
    "a bold command (e.g. 'Never Chase Someone Who Ignores You')",
    "a 'do this instead' format (e.g. 'Do This When They Go Cold')",
    "a number or specific claim (e.g. 'The 1 Response That Ends It')",
    "an intriguing fragment (e.g. 'The Silence That Changes Everything')",
]

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

# fal.ai VEO3 fast sadece belirli sure degerlerini kabul ediyor
VEO_ALLOWED_DURATIONS = [4, 6, 8]


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def _get_next_scenario(self):
        """
        Tarih + saat dilimine gore senaryo secimi. Gunde 2 video paylasildiginda
        (sabah/aksam) farkli sablon almalari icin saat bazli kaydirma uygulanir.
        """
        now = datetime.now()
        day_of_year = now.timetuple().tm_yday
        # Gunun ilk yarisinda mi (sabah run'i) ikinci yarisinda mi (aksam run'i) oldugunu
        # ayirt etmek icin saat kullanilir. Aksam run'i listede yariya yakin kaydirilir.
        hour_offset = (len(SCENARIO_TEMPLATES) // 2) if now.hour >= 12 else 0

        current_index = (day_of_year + hour_offset) % len(SCENARIO_TEMPLATES)
        scenario = SCENARIO_TEMPLATES[current_index]

        print("Scenario #" + str(current_index + 1) + "/" + str(len(SCENARIO_TEMPLATES)) +
              " (hour_offset=" + str(hour_offset) + "): " + scenario[:50])
        return scenario, current_index

    def get_horror_visuals(self, target_duration):
        """
        3-4 VEO + 3-4 FLUX gorseli uretir, toplam target_duration'a (max 35sn)
        gore suresi dagitilir. Script'ten bagimsiz, cesitli korku unsurlari kullanilir.
        """
        veo_count = random.choice([3, 4])
        flux_count = random.choice([3, 4])
        total_count = veo_count + flux_count

        per_duration = target_duration / total_count

        # VEO icin en yakin izinli sureyi sec (4/6/8), sonra ffmpeg ile tam sureye kirpilir
        veo_duration = min(VEO_ALLOWED_DURATIONS, key=lambda x: abs(x - per_duration))

        # Tip sirasini olustur ve karistir (hepsi VEO sonra hepsi FLUX olmasin, karisik gelsin)
        types = ["VEO"] * veo_count + ["FLUX"] * flux_count
        random.shuffle(types)

        visuals = []
        for i, visual_type in enumerate(types):
            use_creature = random.random() < 0.65
            base = random.choice(HORROR_CREATURES) if use_creature else random.choice(HORROR_LOCATIONS)

            if visual_type == "VEO":
                prompt = (
                    "Cinematic horror short film shot. Scene: " + base + ". "
                    "Ultra slow camera push, cold desaturated blue-black, deep shadows, "
                    "unsettling atmosphere, photorealistic, 9:16 vertical, no visible faces."
                )
                duration = veo_duration
            else:
                prompt = (
                    "Photorealistic horror film still. Scene: " + base + ". "
                    "Cold desaturated blue-grey, deep shadows, cinematic composition, "
                    "something deeply wrong visible, 9:16 vertical."
                )
                duration = round(per_duration, 1)

            visuals.append({"type": visual_type, "prompt": prompt, "duration": duration})

        print(str(veo_count) + " VEO + " + str(flux_count) + " FLUX visuals planned "
              "(~" + str(round(per_duration, 1)) + "s each, target=" + str(round(target_duration, 1)) + "s)")
        return visuals

    def generate_video(self, niche=None, analytics_data=None, used_concepts=None):
        scenario, scenario_index = self._get_next_scenario()
        forced_angle = random.choice(FORCED_ANGLES)
        title_style = random.choice(TITLE_STYLES)

        prompt = (
            "You are writing a voiceover script for a YouTube Shorts video about psychology and "
            "self-respect tactics. The video teaches people how to respond with confidence when "
            "someone treats them badly.\n\n"
            "SCENARIO TEMPLATE: " + scenario + "\n\n"
            "MANDATORY ANGLE — you MUST build the entire script around this specific angle, not "
            "a generic summary of the topic:\n\"" + forced_angle + "\"\n\n"
            "MANDATORY TITLE STYLE — the title must follow this exact structural style:\n"
            + title_style + "\n\n"
            "This scenario template may have been used before with a different angle. Your script "
            "must feel like a genuinely different video — different tactic name, different specific "
            "advice, different wording throughout. Do not reuse generic phrases like 'take back "
            "control' or 'remove their power' — find fresh, specific language.\n\n"
            "SCRIPT RULES — STRICT 4-PART STRUCTURE, TOTAL 25-35 SECONDS (roughly 75-95 words):\n"
            "1. HOOK (0-6s, 1-2 short sentences): State the exact situation bluntly. Must instantly "
            "make the viewer think 'this is literally happening to me right now'.\n"
            "2. CURIOSITY GAP (6-11s, 1-2 short sentences): Say that most people respond the wrong "
            "way and it backfires. Do NOT reveal the solution yet.\n"
            "3. SOLUTION (11-28s, 3-5 punchy sentences): Deliver the actual tactic clearly and "
            "specifically, built around the mandatory angle above. Concrete, actionable, "
            "expert-level insight.\n"
            "4. CLOSING LINE (28-34s, 1 short sentence): Sharp, memorable, slightly dark. Quotable.\n\n"
            "- Tone: calm, controlled, slightly dark — a strategist, not a cheerleader.\n"
            "- Use 'you' directly. Short sentences. No filler words.\n"
            "- Do NOT use 'manipulate' or 'manipulation'.\n"
            "- Aim for the FULL 25-35 seconds — 75-95 words, do not undershoot.\n\n"
            "ALSO write a thumbnail_prompt: after you decide the title, write an image description "
            "that VISUALLY REFLECTS THE SPECIFIC CLAIM IN THAT TITLE — not just the general topic. "
            "If the title makes a specific claim or promise, the thumbnail must depict a scene that "
            "directly represents it, so someone who reads the title and sees the thumbnail together "
            "immediately understands the connection. Dark cinematic atmosphere matching the horror "
            "visuals (cold desaturated tones, dramatic shadows), 16:9 landscape, no readable text, "
            "no visible faces, visually intriguing enough to make someone click.\n\n"
            "Return ONLY this JSON, no markdown, no commentary before or after:\n"
            "{\n"
            "  \"title\": \"under 50 chars, following the mandatory title style above, #Shorts\",\n"
            "  \"format\": \"PSYCHOLOGY\",\n"
            "  \"tactic_name\": \"your original tactic name, different from generic ones\",\n"
            "  \"script\": \"the full voiceover script ready to be read aloud\",\n"
            "  \"thumbnail_prompt\": \"one detailed image prompt for the cover thumbnail\",\n"
            "  \"description\": \"#psychology #selfrespect #mindset #shorts #viral #confidence #relationships #emotionalintelligence #growth #respect\",\n"
            "  \"tags\": [\"psychology\", \"selfrespect\", \"mindset\", \"shorts\", \"viral\", \"confidence\", \"relationships\", \"emotionalintelligence\", \"growth\", \"respect\"]\n"
            "}"
        )

        return self._call_claude(prompt, scenario, scenario_index)

    def _extract_json(self, content):
        """Claude ciktisindan JSON'u guvenli sekilde cikarir"""
        content = content.strip()

        if "```" in content:
            parts = content.split("```")
            for part in parts:
                cleaned = part.strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
                if cleaned.startswith("{"):
                    content = cleaned
                    break

        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            content = content[start:end + 1]

        return json.loads(content)

    def _call_claude(self, prompt, scenario, scenario_index):
        video_data = None

        for attempt in range(2):
            try:
                response = self.client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
                video_data = self._extract_json(content)

                if video_data.get("title") and video_data.get("script"):
                    break
                else:
                    print("Attempt " + str(attempt + 1) + ": JSON parsed but missing fields, retrying...")
                    video_data = None
            except Exception as e:
                print("Attempt " + str(attempt + 1) + " parse error: " + str(e))
                video_data = None

        if video_data is None:
            print("WARNING: Using fallback content (Claude JSON failed twice)")
            fallback_tactics = [
                ("The Strategic Pause", "go completely silent and let the silence do the talking"),
                ("The Gray Rock Method", "become so emotionally neutral that you give them nothing to feed on"),
                ("The Reverse Frame", "respond as if their behavior says everything about them and nothing about you"),
                ("The Value Reset", "quietly redirect your time and energy to people who reciprocate"),
                ("The Calm Mirror", "reflect their energy back without absorbing any of it"),
                ("The Detached Observer", "watch their behavior like data, not like a personal attack"),
            ]
            tactic_name, tactic_action = random.choice(fallback_tactics)
            hook_starters = [
                "Here's the truth nobody tells you: if ",
                "Pay attention, because this matters: when ",
                "Stop what you're doing if this sounds familiar: ",
                "This is a pattern you need to recognize: ",
            ]
            hook = random.choice(hook_starters)

            video_data = {
                "title": tactic_name + " — try this #Shorts",
                "format": "PSYCHOLOGY",
                "tactic_name": tactic_name,
                "script": (
                    hook + scenario + ", most people react emotionally — and that reaction is exactly "
                    "what feeds the behavior. Instead, " + tactic_action + ". "
                    "This is called " + tactic_name + ". "
                    "It works because it removes the reward they were looking for. "
                    "No reaction, no reward. No reward, no repeat."
                ),
                "thumbnail_prompt": "dark cinematic close-up of a shadowy figure standing alone in a dim cold-toned room, dramatic lighting, mysterious atmosphere, 16:9, no visible face, no text",
                "description": "#psychology #selfrespect #mindset #shorts #viral #confidence #relationships #emotionalintelligence #growth #respect",
                "tags": ["psychology", "selfrespect", "mindset", "shorts", "viral", "confidence", "relationships", "emotionalintelligence", "growth", "respect"]
            }

        video_data["niche"] = "psychology"
        video_data["scenario"] = scenario
        video_data["scenario_index"] = scenario_index
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on rotating psychology tactics."
