import json
import random
import os
from datetime import datetime


# Tamamen kurgusal korku hikaye onculleri (creepypasta / urban legend tarzi)
# Guvenli - telif/iftira riski yok, hicbir gercek olay/kisiye dayanmiyor
HORROR_STORY_PREMISES = [
    "a group of friends who explored an abandoned asylum and only one of them came back changed",
    "a family who moved into a house where the previous owners vanished without a trace",
    "a night-shift security guard who noticed the cameras kept catching something that wasn't human",
    "hikers who found a cabin deep in the woods that shouldn't exist on any map",
    "a babysitter who started receiving calls from inside the house she was watching",
    "a group of urban explorers who found a subway station that isn't on any transit map",
    "a man who inherited his grandmother's house and found a locked room she never mentioned",
    "college students who played a game late at night that none of them remember starting",
    "a delivery driver whose GPS kept sending him to the same abandoned address every night",
    "a family whose home security app started showing footage from a time that hadn't happened yet",
    "campers who woke up to find their campsite rearranged exactly like it was in an old photograph",
    "a night janitor at an elementary school who found something waiting in the same classroom every night",
    "a woman who found her own handwriting in a diary she never remembers writing",
    "fishermen who found a boat adrift with everything intact except the crew",
    "a photographer whose photos of an old hotel keep developing with an extra figure in them",
    "a man who started hearing his own voice on his answering machine leaving messages he never left",
    "siblings who discovered a hidden staircase in their new house that gets longer every night",
    "a truck driver on a night route who keeps passing the same hitchhiker no matter how far he drives",
    "an apartment tenant who found a way to hear every conversation from an apartment that officially doesn't exist",
    "a group of friends who found an old cabin livestream from a house that burned down years ago",
]

FORCED_ANGLES = [
    "tell it from the perspective of the one person who survived, recounting exactly what happened",
    "build it as a found-footage style account, as if pieced together from recovered recordings",
    "frame it as a story being told around a campfire, with the narrator addressing the listener directly",
    "focus on the small details that seemed harmless at first but turned out to be warnings",
    "structure it as a slow realization — the character doesn't understand what's happening until it's too late",
    "focus on the object or detail that was left behind afterward, and what it implies",
    "tell it as an official incident report that slowly reveals something isn't right",
]

TITLE_STYLES = [
    "a 'true story' framing (e.g. 'The Story Nobody Wanted To Tell')",
    "a survivor-account framing (e.g. 'What I Saw That Night')",
    "a warning framing (e.g. 'Never Do This After Midnight')",
    "a mystery framing (e.g. 'Nobody Knows What Happened To Them')",
    "a discovery framing (e.g. 'They Found This In The Basement')",
]


class ConspiracyContentAgent:
    def __init__(self, client):
        self.client = client

    def _get_next_premise(self):
        """Haftada 1 yayin oldugu icin haftaya gore rotasyon"""
        now = datetime.now()
        week_number = now.isocalendar()[1]
        index = week_number % len(HORROR_STORY_PREMISES)
        premise = HORROR_STORY_PREMISES[index]
        print("Premise #" + str(index + 1) + "/" + str(len(HORROR_STORY_PREMISES)) + ": " + premise[:60])
        return premise, index

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
        premise, premise_index = self._get_next_premise()
        forced_angle = random.choice(FORCED_ANGLES)
        title_style = random.choice(TITLE_STYLES)

        prompt = (
            "You are writing a narration script for a 5-minute YouTube horror story video — "
            "entirely fictional, creepypasta / urban-legend style storytelling. Dark, suspenseful, "
            "unsettling tone, like a horror story narrator building dread step by step.\n\n"
            "STORY PREMISE: " + premise + "\n\n"
            "MANDATORY NARRATIVE ANGLE:\n\"" + forced_angle + "\"\n\n"
            "MANDATORY TITLE STYLE:\n" + title_style + "\n\n"
            "FIRST, invent the specific details of this story: who the character(s) are, the exact "
            "setting, and — most importantly — invent ONE specific creepy entity, creature, or "
            "unexplained phenomenon that is the source of the horror. Keep it consistent throughout "
            "the whole script and the visuals.\n\n"
            "CRITICAL FRAMING: This is 100% fictional horror fiction, clearly in the tradition of "
            "campfire stories and creepypasta. Do not claim it is a true story from real life, and do "
            "not reference any real named individuals, real companies, or real specific addresses.\n\n"
            "SCRIPT STRUCTURE — TOTAL SCRIPT LENGTH: 750-850 words (approx 5 minutes spoken):\n"
            "1. COLD OPEN HOOK (first ~15 seconds / ~35 words): drop the listener straight into an "
            "unsettling moment. Don't explain yet.\n"
            "2. SETUP (~45 seconds): introduce the character(s) and normal situation, so the horror "
            "later feels like a violation of that normalcy.\n"
            "3. BODY (~3 minutes): escalating dread. Every 30-45 seconds, introduce a new unsettling "
            "detail or moment using tension-building transitions like 'That's when they noticed...', "
            "'It wasn't until later that they realized...', 'The next night, it happened again — but "
            "different.'\n"
            "4. CLIMAX (~30-45 seconds): the most terrifying moment of the story — the entity/creature "
            "fully revealed or the horror fully understood.\n"
            "5. UNSETTLING ENDING (~20-30 seconds): an ambiguous or dread-inducing final note — NOT a "
            "clean resolution. Leave the listener with a chill, then a natural call to subscribe for "
            "more horror stories.\n\n"
            "STYLE RULES:\n"
            "- Single continuous narrator voice, no dialogue tags like 'he said' repeated excessively.\n"
            "- Written entirely in English, one consistent dark tone throughout.\n"
            "- Short, punchy sentences for tension; slightly longer ones for atmosphere-building.\n"
            "- This is a narration script meant to be read aloud start to finish — one flowing script, "
            "not bullet points or scene headings.\n\n"
            "ALSO GENERATE A VISUAL SEQUENCE that matches the story chronologically (these visuals "
            "will play in order, in sync with the narration):\n"
            "- Provide 20 visuals total, in the exact order they should appear as the story unfolds.\n"
            "- At least 6 of them must be type \"VEO\" (short cinematic moving shots) — reserve these "
            "for the most dramatic/dread-inducing moments (the entity moving, the reveal, chase "
            "moments).\n"
            "- The rest are type \"FLUX\" (atmospheric still images) — settings, objects, quiet dread, "
            "partial glimpses of the entity.\n"
            "- Every visual prompt must depict the SPECIFIC entity/creature and settings you invented "
            "for this story — not generic horror. Keep the entity hidden/partial in early visuals, "
            "more visible as the story escalates, fully revealed at the climax visuals.\n"
            "- All prompts: photorealistic, cold desaturated horror cinematography, 16:9 landscape, "
            "no readable text, no visible clear human faces (implied dread, not gore), dramatic "
            "lighting and shadow.\n\n"
            "ALSO write a thumbnail_prompt: after you decide the title, write an image description "
            "that visually reflects the specific claim/hook in that title, depicting the entity or "
            "the key unsettling moment of the story. Dark, striking, click-worthy, 16:9 landscape, "
            "no readable text, no visible clear faces.\n\n"
            "Return ONLY this JSON, no markdown, no commentary before or after:\n"
            "{\n"
            "  \"title\": \"under 70 chars, following the mandatory title style above\",\n"
            "  \"entity_name\": \"the specific creature/entity/phenomenon you invented\",\n"
            "  \"script\": \"the full 750-850 word narration script as one continuous text\",\n"
            "  \"visuals\": [\n"
            "    {\"type\": \"VEO\", \"prompt\": \"...\"},\n"
            "    {\"type\": \"FLUX\", \"prompt\": \"...\"}\n"
            "  ],\n"
            "  \"thumbnail_prompt\": \"one detailed image prompt for the cover thumbnail\",\n"
            "  \"description\": \"2-3 sentence fictional horror story description, plus #horror #creepypasta #scarystory #horrorstory #shorts\",\n"
            "  \"tags\": [\"horror\", \"creepypasta\", \"scarystory\", \"horrorstory\", \"creepy\", \"scary\", \"darkstory\", \"nightmare\", \"unexplained\", \"fiction\"]\n"
            "}\n\n"
            "IMPORTANT: the \"visuals\" array must contain exactly 20 items total, at least 6 of type "
            "VEO, in chronological story order."
        )

        return self._call_claude(prompt, premise, premise_index)

    def _call_claude(self, prompt, premise, premise_index):
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

                if video_data.get("title") and video_data.get("script") and video_data.get("visuals"):
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
                "title": "The Story Nobody Wanted To Tell",
                "entity_name": "a pale figure with too many joints",
                "script": (
                    "This story was passed around for years before anyone would say it out loud. " +
                    premise + ". At first, everything seemed normal. But then the small things started "
                    "— things that didn't add up, things that felt wrong in a way no one could explain. "
                    "By the time they understood what was happening, it was already too late to leave. "
                    "What they found in the end, no one who heard the story ever fully believed. "
                    "But those who lived it never went back."
                ),
                "visuals": [
                    {"type": "VEO", "prompt": "dark empty hallway at night, cold blue light, slow cinematic push, 16:9, no faces"},
                    {"type": "FLUX", "prompt": "shadowy figure barely visible at the end of a dark corridor, cold desaturated tones, 16:9"},
                    {"type": "VEO", "prompt": "pale humanoid figure with elongated limbs moving in darkness, slow reveal, 16:9, no faces"},
                    {"type": "FLUX", "prompt": "abandoned room with a single flickering light, dread atmosphere, 16:9"},
                ] * 5,
                "thumbnail_prompt": "dark hallway with a pale humanoid silhouette barely visible at the end, cold blue light, dramatic shadows, 16:9, no text",
                "description": "A fictional horror story. #horror #creepypasta #scarystory #horrorstory #shorts",
                "tags": ["horror", "creepypasta", "scarystory", "horrorstory", "creepy", "scary", "darkstory", "nightmare", "unexplained", "fiction"]
            }

        video_data["topic"] = premise
        video_data["topic_index"] = premise_index
        return video_data
