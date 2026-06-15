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
            "STEP 2: Determine the visual style for this video:\n"
            "- PERIOD: What era is this story from? (1940s, 1950s, 1960s, 1970s, 1980s, 1990s, modern)\n"
            "- COLOR_PALETTE: What color palette fits? (sepia/yellowed, cold blue-grey, green tint, "
            "desaturated, high contrast black and white, warm amber, sickly yellow-green)\n"
            "- CAMERA_STYLE: What camera style fits? (archival 16mm film grain, VHS found footage, "
            "security camera black and white, handheld shaky documentary, "
            "declassified military footage, modern CCTV, Super 8 home movie)\n"
            "- ATMOSPHERE: What atmosphere? (foggy, dimly lit, flickering lights, "
            "harsh fluorescent, moonlit, overcast grey sky, underground bunker lighting)\n\n"
            "STEP 2.5: Before writing the hook, internally brainstorm 5 different "
"shocking opening sentences for this concept - mix of curiosity-based, "
"shock-based, and direct-question style hooks. "
"Pick the single most attention-grabbing one and use ONLY that one "
"as the final hook. Do not show the other 4 in the output.\n\n"
            "STEP 2.6: Before finalizing the title, internally brainstorm 10 different "
"clickable title variations - mix of: titles with numbers/dates, "
"titles framed as questions, titles stating a shocking fact directly, "
"and titles using words like SECRET, HIDDEN, REAL, EXPOSED. "
"Pick the single most click-worthy one under 60 characters and use ONLY "
"that one as the final title. Do not show the other variations in the output.\n\n"
            "STEP 3: Write a 50-second script:\n"
            "HOOK (0-3s): One shocking sentence stated as absolute fact.\n"
            "STORY (3-15s): What happened, when, where, who was involved.\n"
            "DETAILS (15-30s): Specific shocking details, dates, names, evidence.\n"
            "CLIMAX (30-45s): The most disturbing revelation, the darkest truth.\n"
            "CLIFFHANGER (45-55s): End implying it is still happening today.\n\n"
            "STEP 4: Create 10 visuals. EVERY visual MUST use the SAME period, "
            "color palette, camera style and atmosphere determined in STEP 2.\n"
            "Mix of FLUX (still images) and VEO (video clips).\n"
            "Every 2-3 seconds a new visual.\n"
            "Each visual must EXACTLY match the narrative moment.\n"
            "Be extremely specific: include exact locations, clothing, props, lighting.\n\n"
            "VEO prompts must include:\n"
            "- Specific camera movement (slow push-in, aerial drone, handheld shaky, static locked)\n"
            "- Exact period aesthetic (16mm film grain, VHS distortion, security cam timestamp)\n"
            "- Specific action happening in the scene\n\n"
            "FLUX prompts must include:\n"
            "- Archival or documentary photograph style\n"
            "- Exact period (e.g. 1970s news photograph, declassified 1983 document scan)\n"
            "- Specific subject with exact details\n"
            "- Lighting and color palette\n\n"
            "Style: Like Obscura Psyche channel. Sounds completely real.\n"
            "Use phrases like: newly leaked documents reveal, classified files show, "
            "witnesses confirm, they tried to hide this.\n\n"
            "IMPORTANT: Everything in English only.\n\n"
            "STEP 5: Write an SEO-optimized description with:\n"
"- Line 1: main keyword phrase related to the concept\n"
"- Lines 2-4: three teasing hook sentences (different from the script hook)\n"
"- Then 10 hashtags: 3 broad (#conspiracy #mystery #paranormal), "
"3 medium specific (#" + country + "mystery #darksecrets #classifiedfiles), "
"4 highly specific to this exact story\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            "  \"title\": \"shocking title stated as fact under 60 chars with #Shorts\",\n"
            "  \"concept\": \"one sentence description of the invented concept\",\n"
            "  \"period\": \"era of the story\",\n"
            "  \"visual_style\": {\n"
            "    \"color_palette\": \"chosen palette\",\n"
            "    \"camera_style\": \"chosen camera style\",\n"
            "    \"atmosphere\": \"chosen atmosphere\"\n"
            "  },\n"
            "  \"script\": {\n"
            "    \"hook\": \"shocking opening sentence\",\n"
            "    \"story\": \"what happened narrative\",\n"
            "    \"details\": \"specific shocking details\",\n"
            "    \"climax\": \"most disturbing revelation\",\n"
            "    \"cliffhanger\": \"still happening implication\"\n"
            "  },\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"[period aesthetic] [camera movement] [specific scene] [color palette] [atmosphere] 9:16 vertical\", \"duration\": 3},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"[period] archival photograph, [specific subject], [exact details], [color palette], [lighting]\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"[period aesthetic] [camera movement] [specific scene] [color palette] [atmosphere] 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"[period] document or photograph, [specific subject], [exact details], [color palette]\", \"duration\": 3},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"[period] archival image, [specific subject], [exact details], [lighting]\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"[period aesthetic] [camera movement] [specific scene] [atmosphere] 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"[period] photograph or document, [specific subject], [color palette]\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"[period aesthetic] [camera movement] [climax scene] [atmosphere] 9:16 vertical\", \"duration\": 4},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"[period] archival image, [disturbing detail], [color palette], [lighting]\", \"duration\": 3},\n"
            "    {\"type\": \"VEO\", \"prompt\": \"[period aesthetic] [camera movement] [cliffhanger scene] [atmosphere] 9:16 vertical\", \"duration\": 3}\n"
            "  ],\n"
         "  \"description\": \"[main keyword phrase in first line] [3 sentence hooks that tease the content] [10 hashtags mixing broad like #conspiracy #mystery, medium like #" + country + "secrets #paranormalstories, and specific like #classifiedfiles]\",\n"
            "  \"tags\": [\"conspiracy\", \"paranormal\", \"mystery\", \"dark\", \"shorts\", \"viral\", \"scary\", \"classified\", \"leaked\", \"truth\"]\n"
            "}\n\n"
            "No markdown, raw JSON only. Replace ALL bracketed placeholders with real specific content."
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
