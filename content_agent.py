import json
import random


COUNTRIES = [
    "Russia", "USA", "Japan", "UK", "Brazil", "China", "Germany", "Australia",
    "Egypt", "Mexico", "Norway", "India", "France", "Iran", "Peru", "Turkey",
    "South Korea", "Italy", "Canada", "Bolivia", "Argentina", "Sweden", "Greece",
    "Ethiopia", "Indonesia", "Pakistan", "Nigeria", "Ukraine", "Poland", "Romania",
    "Czech Republic", "Hungary", "Portugal", "Spain", "Netherlands", "Belgium",
    "Switzerland", "Austria", "Denmark", "Finland", "New Zealand", "South Africa",
    "Morocco", "Iraq", "Syria", "Afghanistan", "Tibet", "Mongolia", "Cambodia",
    "Vietnam", "Thailand", "Philippines", "Malaysia", "Chile", "Colombia", "Venezuela"
]

USED_COUNTRIES_FILE = "used_countries.json"


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def _get_unused_country(self):
        try:
            with open(USED_COUNTRIES_FILE, "r") as f:
                used = json.load(f)
        except Exception:
            used = []
        available = [c for c in COUNTRIES if c not in used]
        if not available:
            used = []
            available = COUNTRIES
        country = random.choice(available)
        used.append(country)
        with open(USED_COUNTRIES_FILE, "w") as f:
            json.dump(used, f)
        return country

    def generate_video(self, niche, analytics_data, used_concepts=None):
        country = self._get_unused_country()
        print("Country: " + country)

        prompt = (
            "You are creating a viral conspiracy and paranormal YouTube Shorts video.\n\n"
            "Country: " + country + "\n\n"
            "STEP 1: Invent a completely unique, shocking conspiracy or paranormal concept "
            "specifically tied to " + country + ". "
            "It must sound real, be based on real locations or history, "
            "and feel like a leaked documentary. Never use concepts already famous online.\n\n"
            "STEP 2: Write a 50-second script with EXACTLY this structure:\n"
            "HOOK (0-3s): One shocking sentence stated as absolute fact.\n"
            "STORY (3-15s): What happened, when, where, who was involved.\n"
            "DETAILS (15-30s): Specific shocking details, dates, names, evidence.\n"
            "CLIMAX (30-45s): The most disturbing revelation, the darkest truth.\n"
            "CLIFFHANGER (45-55s): End implying it is still happening today.\n\n"
            "STEP 3: Create 10 unique visuals for this video.\n"
            "Mix of FLUX (still images) and VEO (video clips).\n"
            "Every 2-3 seconds a new visual - keep viewer hooked.\n"
            "Each visual must EXACTLY match the narrative at that moment.\n"
            "All visuals must be dark, cinematic, photorealistic, 9:16 vertical.\n"
            "VEO prompts must include camera movement descriptions.\n"
            "FLUX prompts must include dramatic lighting descriptions.\n\n"
            "Style: Like Obscura Psyche channel. Sounds completely real. "
            "Use phrases like: newly leaked documents reveal, "
            "classified files show, witnesses confirm, they tried to hide this.\n\n"
            "IMPORTANT: Everything in English only.\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            "  \"title\": \"shocking title stated as fact under 60 chars with #Shorts\",\n"
            "  \"concept\": \"one sentence description of the invented concept\",\n"
            "  \"script\": {\n"
            "    \"hook\": \"shocking opening sentence\",\n"
            "    \"story\": \"what happened narrative\",\n"
            "    \"details\": \"specific shocking details\",\n"
            "    \"climax\": \"most disturbing revelation\",\n"
            "    \"cliffhanger\": \"still happening implication\"\n"
            "  },\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 3},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 3},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\", \"duration\": 3}\n"
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
                "title": "The " + country + " Secret Nobody Talks About #Shorts",
                "concept": "Classified experiment in " + country + " that was never revealed",
                "script": {
                    "hook": "What happened in " + country + " in 1973 was buried by the government.",
                    "story": "Classified documents show a secret facility operated for decades.",
                    "details": "Witnesses were silenced. Files were destroyed. But one survived.",
                    "climax": "What they found inside defied everything we know.",
                    "cliffhanger": "The facility is still active. The experiments never stopped."
                },
                "visuals": [
                    {"type": "VEO", "prompt": "Dark government facility in " + country + " at night, slow camera push, cinematic horror, 9:16 vertical", "duration": 3},
                    {"type": "FLUX", "prompt": "Classified documents stamped SECRET, dark desk in " + country + ", dramatic shadows, photorealistic", "duration": 3},
                    {"type": "VEO", "prompt": "Scientists in hazmat suits entering dark vault, flashlights, tension, " + country + ", cinematic 9:16", "duration": 4},
                    {"type": "FLUX", "prompt": "Conspiracy evidence board with red strings and photographs, dark room, atmospheric", "duration": 3},
                    {"type": "FLUX", "prompt": "Close up of leaked experiment files, disturbing notes, dramatic lighting", "duration": 3},
                    {"type": "VEO", "prompt": "Shocking discovery inside sealed chamber, dramatic reveal, cinematic horror, 9:16 vertical", "duration": 4},
                    {"type": "FLUX", "prompt": "Dark facility corridor in " + country + ", shadows, someone watching, eerie", "duration": 3},
                    {"type": "VEO", "prompt": "Modern facility same design, active monitors, ongoing experiment, camera slowly zooms, 9:16", "duration": 4},
                    {"type": "FLUX", "prompt": "Leaked document dated recent year, classified stamp, dark atmosphere", "duration": 3},
                    {"type": "VEO", "prompt": "Mystery figure entering facility, door closing, darkness, cliffhanger, 9:16 vertical", "duration": 3}
                ],
                "description": "They tried to hide this. Newly leaked documents reveal the truth.",
                "tags": ["conspiracy", "paranormal", "mystery", "dark", "shorts", "viral", "scary", "classified", "leaked", "truth"]
            }

        video_data["niche"] = niche
        video_data["country"] = country
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on unique conspiracy theories stated as real facts."
