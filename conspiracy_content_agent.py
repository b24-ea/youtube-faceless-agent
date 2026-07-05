import json
import random
import os
from datetime import datetime


# Gercek/bilinen, genelde "teori/eglence" olarak islenen ve YouTube'da yaygin
# monetize edilen konular. Guncel saglik/asi/secim gibi hassas konulardan kaciniliyor.
CONSPIRACY_TOPICS = [
    "Area 51 and the alleged extraterrestrial cover-up",
    "The Montauk Project time experiments",
    "The MKUltra mind control program",
    "The Denver International Airport murals and underground rumors",
    "The Dulce Base underground facility theory",
    "The Majestic 12 declassified documents",
    "Project Blue Book and the UFO investigations",
    "The Philadelphia Experiment",
    "Operation Northwoods declassified plan",
    "Operation Paperclip and the Nazi scientists brought to America",
    "The Roswell incident",
    "The Jonestown massacre and government involvement theories",
    "The Nazi Antarctica base theory (Base 211)",
    "The Bilderberg Group secrecy",
    "COINTELPRO and domestic surveillance",
    "The Tuskegee syphilis experiment",
    "The Iran-Contra affair",
    "The Georgia Guidestones mystery",
    "Skinwalker Ranch phenomena",
    "Declassified files from the Black Vault",
    "The D.B. Cooper hijacking mystery",
    "The Voynich Manuscript and government interest in it",
    "The Rendlesham Forest UFO incident",
    "Project Stargate, the psychic remote viewing program",
    "The Phoenix Lights incident",
]

FORCED_ANGLES = [
    "focus on the one declassified document that changed everything",
    "focus on a witness whose story was dismissed for decades until new evidence emerged",
    "focus on the strange coincidences and unanswered questions officials still won't address",
    "focus on what official reports admit versus what they conveniently leave out",
    "focus on the timeline of cover-up: what was denied, then later quietly confirmed",
    "focus on the connections between this event and other unexplained incidents",
    "focus on why the full truth may never be declassified",
]

TITLE_STYLES = [
    "a shocking claim format (e.g. 'The Government Finally Admitted This')",
    "a question format (e.g. 'What Really Happened At...')",
    "a declassified/secret format (e.g. 'Newly Declassified: The Truth About...')",
    "a warning/ominous format (e.g. 'They Don't Want You To Know This About...')",
    "a mystery format (e.g. 'The Unexplained Mystery Of...')",
]

# VEO/FLUX icin karanlik, gizemli, "government cover-up documentary" atmosferi
# Gercek kisi/logo/marka gorunmuyor, sadece atmosfer
ATMOSPHERE_SCENES = [
    "dimly lit government archive room, endless rows of filing cabinets, single hanging light",
    "redacted document close-up, black bars covering text, held under a desk lamp",
    "abandoned military base hallway at night, flickering emergency lights",
    "dark underground bunker corridor, concrete walls, distant echoing drip",
    "old file room with dust floating in a single beam of light through blinds",
    "shadowy figure silhouette behind frosted glass door, government building at night",
    "vintage reel-to-reel tape recorder spinning in a dark office, red light blinking",
    "empty interrogation room, single chair under a bare bulb, two-way mirror",
    "foggy military airfield at night, silhouette of a hangar in the distance",
    "old typewriter on a wooden desk, papers scattered, dim desk lamp light",
    "chain-link fence with warning sign, desert landscape at dusk, distant lights beyond",
    "dark archive vault door slowly closing, heavy metal, dim red warning light",
]


class ConspiracyContentAgent:
    def __init__(self, client):
        self.client = client

    def _get_next_topic(self):
        """Haftada 1 yayin oldugu icin haftaya gore rotasyon (ISO hafta numarasi)"""
        now = datetime.now()
        week_number = now.isocalendar()[1]
        index = week_number % len(CONSPIRACY_TOPICS)
        topic = CONSPIRACY_TOPICS[index]
        print("Topic #" + str(index + 1) + "/" + str(len(CONSPIRACY_TOPICS)) + ": " + topic)
        return topic, index

    def _extract_json(self, content):
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

    def generate_video(self):
        topic, topic_index = self._get_next_topic()
        forced_angle = random.choice(FORCED_ANGLES)
        title_style = random.choice(TITLE_STYLES)

        prompt = (
            "You are writing a narration script for an 8-minute YouTube documentary-style video "
            "about a real historical conspiracy theory. The tone is dark, mysterious, and "
            "suspenseful — like a true-crime or unexplained-mysteries documentary narrator.\n\n"
            "TOPIC: " + topic + "\n\n"
            "MANDATORY ANGLE — build the narrative around this specific angle:\n\"" + forced_angle + "\"\n\n"
            "MANDATORY TITLE STYLE:\n" + title_style + "\n\n"
            "CRITICAL FRAMING RULES (legal/policy safety):\n"
            "- Present this as a THEORY and historical narrative, not as verified fact. Use phrases "
            "like 'according to declassified documents', 'some researchers believe', 'officially "
            "denied, but...', 'the theory suggests'.\n"
            "- Do NOT name or accuse any specific living private individual of wrongdoing.\n"
            "- Do NOT include modern health, vaccine, or election-related claims — this is strictly "
            "about historical/Cold-War-era government secrecy and unexplained phenomena.\n"
            "- Base it on the real historical event/theory as it is popularly known and documented.\n\n"
            "SCRIPT STRUCTURE — TOTAL SCRIPT LENGTH: 1100-1300 words (approx 8 minutes spoken):\n"
            "1. COLD OPEN HOOK (first ~15 seconds / ~35 words): a shocking claim or question that "
            "stops the viewer from scrolling. Do not explain yet.\n"
            "2. SETUP (~1 minute): explain what officially happened, in clear simple terms.\n"
            "3. BODY (~5-6 minutes): a series of escalating revelations. Every 45-60 seconds "
            "(~100-130 words per beat), introduce a new twist, detail, or piece of 'evidence', "
            "using pattern-interrupt transitions like 'But here's where it gets stranger...', "
            "'That's when investigators found something nobody expected...', 'Here's what they "
            "don't want you to think about...'\n"
            "4. CLIMAX: the most disturbing or shocking revelation of the theory.\n"
            "5. OPEN-ENDED ENDING (~30 seconds): leave the viewer with an unanswered question, "
            "then a natural call to subscribe for more declassified stories.\n\n"
            "STYLE RULES:\n"
            "- Single continuous narrator voice. No dialogue, no other characters speaking.\n"
            "- Written entirely in English, one consistent tone throughout.\n"
            "- Short, punchy sentences mixed with a few longer explanatory ones for pacing variety.\n"
            "- No filler, no repeating the same point twice.\n"
            "- This is a narration script meant to be read aloud start to finish — write it as one "
            "flowing script, not as bullet points or scene headings.\n\n"
            "ALSO GENERATE A VISUAL PLAN:\n"
            "- 4 VEO video prompts: short cinematic moving shots, dark documentary atmosphere, "
            "16:9 landscape, no readable text/logos, no real identifiable people, based on the "
            "ATMOSPHERE mood (redacted documents, archives, shadowy government buildings, foggy "
            "military sites, dim interrogation rooms).\n"
            "- 10 FLUX still image prompts: photorealistic moody documentary-style stills, same "
            "dark atmosphere, 16:9 landscape, no readable text/logos, no real identifiable people.\n"
            "- 14 stock footage search queries: short 2-4 word generic search terms for real stock "
            "footage that would fit a documentary about this topic (e.g. 'old newspaper archive', "
            "'military base fence', 'vintage typewriter', 'foggy forest road', 'government building "
            "exterior', 'filing cabinet documents', 'night surveillance camera', 'clock ticking "
            "close up', 'old film grain', 'abandoned hallway', 'declassified stamp paper', "
            "'radio static tv'). Keep them generic and safe (no brand names, no real people's names).\n\n"
            "ALSO write a thumbnail_prompt: after you decide the title, write an image description "
            "that VISUALLY REFLECTS THE SPECIFIC CLAIM IN THAT TITLE — not just the general topic. "
            "If the title makes a specific claim or promise, the thumbnail must depict a scene that "
            "directly represents it, so someone who reads the title and sees the thumbnail together "
            "immediately understands the connection. Dark documentary atmosphere, high detail, "
            "visually intriguing enough to make someone click, 16:9 landscape, no readable text/logos, "
            "no real identifiable people.\n\n"
            "Return ONLY this JSON, no markdown, no commentary before or after:\n"
            "{\n"
            "  \"title\": \"under 70 chars, following the mandatory title style above\",\n"
            "  \"script\": \"the full 1100-1300 word narration script as one continuous text\",\n"
            "  \"veo_prompts\": [\"...\", \"...\", \"...\", \"...\"],\n"
            "  \"flux_prompts\": [\"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\"],\n"
            "  \"stock_queries\": [\"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\", \"...\"],\n"
            "  \"thumbnail_prompt\": \"one detailed image prompt for the cover thumbnail\",\n"
            "  \"description\": \"2-3 sentence description mentioning this is a theory/documentary, plus #conspiracy #mystery #declassified #documentary\",\n"
            "  \"tags\": [\"conspiracy\", \"mystery\", \"government\", \"declassified\", \"documentary\", \"unexplained\", \"darkhistory\", \"coldwar\", \"classified\", \"truestory\"]\n"
            "}"
        )

        return self._call_claude(prompt, topic, topic_index)

    def _call_claude(self, prompt, topic, topic_index):
        video_data = None

        for attempt in range(2):
            try:
                response = self.client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
                video_data = self._extract_json(content)

                if video_data.get("title") and video_data.get("script") and video_data.get("veo_prompts"):
                    break
                else:
                    print("Attempt " + str(attempt + 1) + ": JSON parsed but missing fields, retrying...")
                    video_data = None
            except Exception as e:
                print("Attempt " + str(attempt + 1) + " parse error: " + str(e))
                video_data = None

        if video_data is None:
            print("WARNING: Using fallback content (Claude JSON failed twice)")
            video_data = {
                "title": "The Declassified Truth About " + topic.split(" and ")[0][:40],
                "script": (
                    "What you're about to hear was hidden for decades. " + topic + " has puzzled "
                    "researchers, witnesses, and even government officials for years. Officially, "
                    "the story is simple. But the more you look, the less it adds up. Documents "
                    "were classified. Witnesses were silenced. And questions that should have been "
                    "answered decades ago remain open today. This is the story they don't want you "
                    "to fully understand."
                ),
                "veo_prompts": [
                    "dimly lit government archive room, endless filing cabinets, single hanging light, cinematic slow push, 16:9",
                    "redacted document close-up under a desk lamp, slow reveal, 16:9",
                    "abandoned military hallway at night, flickering lights, slow dolly, 16:9",
                    "foggy military airfield at night, distant hangar silhouette, slow pan, 16:9"
                ],
                "flux_prompts": [ATMOSPHERE_SCENES[i % len(ATMOSPHERE_SCENES)] for i in range(10)],
                "stock_queries": [
                    "old newspaper archive", "military base fence", "vintage typewriter",
                    "foggy forest road", "government building exterior", "filing cabinet documents",
                    "night surveillance camera", "clock ticking close up", "old film grain",
                    "abandoned hallway", "declassified stamp paper", "radio static tv",
                    "dark storm clouds", "empty office night"
                ],
                "thumbnail_prompt": "dramatic dark government archive room with a single redacted document under harsh desk lamp light, cinematic shadows, mysterious atmosphere, 16:9, no text, no faces",
                "description": "A look into one of history's most debated theories. #conspiracy #mystery #declassified #documentary",
                "tags": ["conspiracy", "mystery", "government", "declassified", "documentary", "unexplained", "darkhistory", "coldwar", "classified", "truestory"]
            }

        video_data["topic"] = topic
        video_data["topic_index"] = topic_index
        return video_data
