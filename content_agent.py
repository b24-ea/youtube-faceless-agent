import json
import random


DARK_CONCEPTS = [
    {"concept": "The Russian Sleep Experiment was real and is still happening today", "country": "Russia"},
    {"concept": "MK Ultra mind control program never actually stopped and targets civilians today", "country": "USA"},
    {"concept": "Japan Unit 731 created a biological weapon that was secretly deployed in 1995", "country": "Japan"},
    {"concept": "The UK government deliberately caused the 1952 Great Smog to test population control", "country": "UK"},
    {"concept": "Brazil Colonia hospital performed illegal experiments on 60000 patients for decades", "country": "Brazil"},
    {"concept": "China Underground Great Wall hides a secret city built for elite survival", "country": "China"},
    {"concept": "Nazi Bell device was completed and smuggled to Argentina after WW2", "country": "Germany"},
    {"concept": "Australia Pine Gap base is a portal monitoring station for interdimensional activity", "country": "Australia"},
    {"concept": "Egypt Great Pyramid contains a hidden chamber with technology that predates humanity", "country": "Egypt"},
    {"concept": "Mexico Zone of Silence blocks all signals and used for alien communication since 1970", "country": "Mexico"},
    {"concept": "Norway Svalbard Seed Vault contains something far more terrifying than seeds", "country": "Norway"},
    {"concept": "India Roopkund Lake skeletons are victims of a classified weather weapon test", "country": "India"},
    {"concept": "France Paris Catacombs hide an active secret society still performing rituals today", "country": "France"},
    {"concept": "Iran Burnt City contains evidence of an advanced civilization erased from history", "country": "Iran"},
    {"concept": "Peru Nazca Lines are landing coordinates still being used by craft seen today", "country": "Peru"},
    {"concept": "Turkey Gobekli Tepe was deliberately buried to hide proof it was built by non-humans", "country": "Turkey"},
    {"concept": "South Korea Hwaseong Fortress tunnels connect to an underground base still operational", "country": "South Korea"},
    {"concept": "Italy Vatican Secret Archives contain suppressed evidence of extraterrestrial contact", "country": "Italy"},
    {"concept": "Canada Willow Creek facility was a classified mind control site vanished from records", "country": "Canada"},
    {"concept": "Bolivia Gate of the Sun is a functional star map pointing to an incoming event", "country": "Bolivia"},
]


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def generate_video(self, niche, analytics_data, used_concepts=None):
        used = used_concepts or []
        available = [item for item in DARK_CONCEPTS if item["concept"] not in used]
        if not available:
            available = DARK_CONCEPTS
        item = random.choice(available)
        concept = item["concept"]
        country = item["country"]
        print("Country: " + country)
        print("Concept: " + concept)

        prompt = (
            "You are creating a viral conspiracy and paranormal YouTube Shorts video.\n\n"
            "Country: " + country + "\n"
            "Concept: " + concept + "\n\n"
            "Style: Like Obscura Psyche channel. Sounds completely real. "
            "Documentary style. Use phrases like: newly leaked documents reveal, "
            "classified files show, witnesses confirm, they tried to hide this.\n\n"
            "Create a 50-second script with EXACTLY this structure:\n\n"
            "HOOK (0-3s): One shocking sentence stated as absolute fact.\n"
            "STORY (3-15s): What happened, when, where, who was involved.\n"
            "DETAILS (15-30s): Specific shocking details, dates, names, evidence.\n"
            "CLIMAX (30-45s): The most disturbing revelation, the darkest truth.\n"
            "CLIFFHANGER (45-55s): End implying it is still happening today.\n\n"
            "Also create 10 visual prompts for this video.\n"
            "Mix of: Flux Pro still images AND Veo 3 video clips.\n"
            "Label each as FLUX or VEO.\n"
            "Every 2-3 seconds a new visual - keep viewer hooked.\n"
            "Visuals must match the narrative at that moment.\n\n"
            "IMPORTANT: English only.\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            "  \"title\": \"shocking title stated as fact under 60 chars with #Shorts\",\n"
            "  \"script\": {\n"
            "    \"hook\": \"shocking opening sentence\",\n"
            "    \"story\": \"what happened narrative\",\n"
            "    \"details\": \"specific shocking details\",\n"
            "    \"climax\": \"most disturbing revelation\",\n"
            "    \"cliffhanger\": \"still happening implication\"\n"
            "  },\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"cinematic dark opening scene\", \"duration\": 3},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"dramatic still image\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"action scene\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"evidence closeup\", \"duration\": 3},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"classified documents\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"shocking revelation scene\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"dark atmospheric image\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"climax action scene\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"disturbing detail image\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"mysterious cliffhanger ending\", \"duration\": 3}\n"
            "  ],\n"
            "  \"description\": \"They tried to hide this. Newly leaked documents reveal the truth.\",\n"
            "  \"tags\": [\"conspiracy\", \"paranormal\", \"mystery\", \"dark\", \"shorts\", \"viral\", \"scary\", \"classified\", \"leaked\", \"truth\"]\n"
            "}\n\n"
            "No markdown, raw JSON only."
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
                "title": "The Russian Sleep Experiment Was REAL #Shorts",
                "script": {
                    "hook": "The Russian Sleep Experiment was not a story. It was a classified program that never ended.",
                    "story": "In 1947 Soviet scientists sealed five prisoners in a chamber with experimental stimulant gas.",
                    "details": "On day nine the screaming stopped. Researchers found subjects had removed their own organs and were still alive.",
                    "climax": "The gas had rewritten human biology. The subjects begged to stay in the chamber.",
                    "cliffhanger": "Newly leaked Kremlin files show the experiment restarted in 1984. The latest subjects checked in last year."
                },
                "visuals": [
                    {"type": "VEO", "prompt": "Dark Soviet laboratory 1947, sealed chamber door, flickering lights, cinematic horror, 9:16 vertical", "duration": 3},
                    {"type": "FLUX", "prompt": "Classified Soviet documents stamped SECRET, dark desk, dramatic shadows, photorealistic", "duration": 3},
                    {"type": "VEO", "prompt": "Scientists in gas masks entering dark vault, flashlights, tension, cinematic, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "Conspiracy evidence board, red strings, photographs, dark room, atmospheric", "duration": 3},
                    {"type": "FLUX", "prompt": "Close up of classified experiment files, disturbing notes, dramatic lighting", "duration": 3},
                    {"type": "VEO", "prompt": "Horrifying discovery inside sealed chamber, dramatic reveal, cinematic horror, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "Dark Soviet facility corridor, shadows, someone watching, eerie atmosphere", "duration": 3},
                    {"type": "VEO", "prompt": "Modern facility same design as Soviet lab, active monitors, ongoing experiment, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "Leaked document dated 1984 restart order, classified stamp, dark atmosphere", "duration": 3},
                    {"type": "VEO", "prompt": "Mystery figure entering modern facility, door closing, darkness, cliffhanger ending, 9:16 vertical", "duration": 3}
                ],
                "description": "They tried to hide this. Newly leaked documents reveal the truth.",
                "tags": ["conspiracy", "paranormal", "mystery", "dark", "shorts", "viral", "scary", "classified", "leaked", "truth"]
            }

        video_data["niche"] = niche
        video_data["concept"] = concept
        video_data["country"] = country
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on conspiracy theories stated as real facts."
