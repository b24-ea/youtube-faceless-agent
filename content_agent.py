import json
import random
import os


# Konu havuzu: manipülasyon / dark psychology / kötü davranışlara karşı taktikler
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

# Görsel sahneler — korku atmosferi korunuyor ama artık yaratık yok
# gerilim / gizem / güç hissi veren sahneler
ATMOSPHERE_SCENES = [
    "empty dark room lit by a single cold window light, rain on glass",
    "dark hallway with one flickering light at the far end",
    "person standing alone in fog, back turned to camera, city lights distant",
    "close up of hands resting calmly on a dark wooden table, single candle",
    "empty night street, wet asphalt reflecting cold blue light",
    "person sitting in shadow, only silhouette visible against window",
    "dark mirror reflecting a dim room, nobody visible in reflection",
    "abandoned building interior, moonlight through broken windows",
    "rain falling on dark glass, blurred city lights behind",
    "empty chair in a dark room, single light from above",
    "person walking slowly away down a long dark corridor",
    "close up of a phone screen glowing in a dark room, notification fading",
    "dark forest path at dusk, cold mist between the trees",
    "quiet rooftop at night, city skyline in cold blue tones",
    "old clock ticking in a dim empty room, shadows stretching",
]


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def _get_unused_topic(self):
        used_file = "used_topics.json"
        try:
            with open(used_file, "r") as f:
                used = json.load(f)
        except Exception:
            used = []

        available = [t for t in TOPICS if t["tactic_name"] not in used]
        if not available:
            used = []
            available = TOPICS

        chosen = random.choice(available)
        used.append(chosen["tactic_name"])
        with open(used_file, "w") as f:
            json.dump(used, f)
        return chosen

    def generate_video(self, niche=None, analytics_data=None, used_concepts=None):
        topic = self._get_unused_topic()
        print("Topic: " + topic["tactic_name"] + " - " + topic["trigger"][:50])

        prompt = (
            "You are writing a voiceover script for a YouTube Shorts video about psychology and "
            "self-respect tactics. The video teaches people how to respond with confidence when "
            "someone treats them badly.\n\n"
            "SITUATION: " + topic["trigger"] + "\n"
            "TACTIC NAME: " + topic["tactic_name"] + "\n\n"
            "SCRIPT RULES:\n"
            "- Total spoken length: 25-35 seconds when read aloud at normal pace (roughly 65-90 words).\n"
            "- HOOK (first sentence): State the situation directly and create immediate relatability. "
            "Something that makes the viewer think 'this is literally me'.\n"
            "- BODY: Explain the psychological tactic in 3-4 short, punchy sentences. Practical, "
            "specific, actionable. Not generic self-help fluff — sound like an expert revealing "
            "an insider secret.\n"
            "- CLOSING LINE: A short, memorable, slightly dark/powerful statement that summarizes "
            "the mindset shift. Should feel quotable.\n"
            "- Tone: calm, controlled, slightly dark and serious — like someone who has mastered "
            "emotional control speaking with quiet authority. NOT motivational-speaker energy. "
            "NOT cheerful. Think: a strategist, not a cheerleader.\n"
            "- Use 'you' directly. Short sentences. No filler words. No emojis in the script text.\n"
            "- Do NOT use the words 'manipulate' or 'manipulation' — keep it framed as self-respect "
            "and emotional intelligence, not as scheming against others.\n\n"
            "VISUAL RULES:\n"
            "- This video uses dark, moody, cinematic atmosphere visuals (NOT literal illustrations "
            "of the advice — abstract mood pieces: empty rooms, rain, shadows, silhouettes, cold "
            "light). No people's faces shown clearly. No text in the visuals themselves.\n"
            "- Generate 4 visuals total. They will play under the voiceover, looping/cross-fading "
            "as needed to fill the audio duration.\n"
            "- Color: cold desaturated blue-grey-black palette, cinematic, atmospheric.\n\n"
            "VEO prompts: slow cinematic camera movement, moody atmosphere, 9:16 vertical, no people's faces\n"
            "FLUX prompts: photorealistic moody photography, cinematic shadows, cold tones, 9:16 vertical\n\n"
            "Return ONLY this JSON, no markdown:\n"
            "{\n"
            "  \"title\": \"under 50 chars, intriguing, no clickbait spam #Shorts\",\n"
            "  \"format\": \"PSYCHOLOGY\",\n"
            "  \"script\": \"the full voiceover script as one continuous text, ready to be read aloud\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 6},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 6},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 6},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 6}\n"
            "  ],\n"
            "  \"description\": \"#psychology #selfrespect #mindset #shorts #viral #confidence #relationships #emotionalintelligence #growth #respect\",\n"
            "  \"tags\": [\"psychology\", \"selfrespect\", \"mindset\", \"shorts\", \"viral\", \"confidence\", \"relationships\", \"emotionalintelligence\", \"growth\", \"respect\"]\n"
            "}"
        )

        return self._call_claude(prompt, topic)

    def _call_claude(self, prompt, topic):
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
                "title": topic["tactic_name"] + " #Shorts",
                "format": "PSYCHOLOGY",
                "script": (
                    "If " + topic["trigger"] + ", do not react with emotion. "
                    "Respond with silence and distance instead. "
                    "This is called " + topic["tactic_name"] + ". "
                    "When you stop reacting, you take back control. "
                    "People only escalate when they get a reaction. "
                    "Remove the reaction, and you remove their power."
                ),
                "visuals": [
                    {"type": "VEO", "prompt": "slow cinematic shot of empty dark room, cold window light, rain on glass, 9:16 vertical, no faces", "duration": 6},
                    {"type": "FLUX", "prompt": "photorealistic moody photography, dark hallway, single flickering light, cold blue tones, 9:16 vertical", "duration": 6},
                    {"type": "VEO", "prompt": "slow push toward dark window, city lights blurred, cold atmosphere, 9:16 vertical, no faces", "duration": 6},
                    {"type": "FLUX", "prompt": "photorealistic silhouette in shadow against window, cold cinematic light, 9:16 vertical", "duration": 6}
                ],
                "description": "#psychology #selfrespect #mindset #shorts #viral #confidence #relationships #emotionalintelligence #growth #respect",
                "tags": ["psychology", "selfrespect", "mindset", "shorts", "viral", "confidence", "relationships", "emotionalintelligence", "growth", "respect"]
            }

        video_data["niche"] = "psychology"
        video_data["scenario"] = topic["tactic_name"]
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on rotating psychology tactics."
