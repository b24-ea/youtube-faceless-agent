import json


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def generate_video(self, niche, analytics_data, is_shorts=False):
        if is_shorts:
            prompt = (
                "You are an expert at creating fun, viral YouTube SHORTS for kids and families.\n\n"
                "Create a hilarious and entertaining SHORT video script.\n"
                "Max length: 45 seconds when read aloud (about 100-120 words)\n"
                "Style: Super energetic, funny, surprising facts, jokes for kids\n\n"
                "Choose ONE topic:\n"
                "- Funny animal facts that will blow your mind\n"
                "- Hilarious science experiments gone wrong\n"
                "- Weird and wacky world records\n"
                "- Funny optical illusions explained\n"
                "- Crazy food facts kids will love\n\n"
                "Return ONLY a JSON object:\n"
                "{\n"
                "  \"title\": \"funny kids shorts title with #Shorts\",\n"
                "  \"hook\": \"super funny shocking opening line\",\n"
                "  \"script\": \"45 second funny script, max 120 words, energetic and fun\",\n"
                "  \"visual_descriptions\": [\"funny scene 1\", \"funny scene 2\", \"funny scene 3\"],\n"
                "  \"dalle_prompts\": [\"cute funny cartoon animal scene\", \"colorful fun kids illustration\"],\n"
                "  \"tags\": [\"#Shorts\", \"kids\", \"funny\", \"animals\", \"facts\", \"comedy\", \"fun\", \"viral\", \"cartoon\", \"amazing\"],\n"
                "  \"description\": \"fun short description for kids\",\n"
                "  \"thumbnail_concept\": \"bright colorful funny thumbnail\"\n"
                "}\n\n"
                "No markdown, raw JSON only."
            )
        else:
            prompt = (
                "You are an expert at creating fun, viral YouTube videos for kids and families.\n\n"
                "Create a hilarious and entertaining video script.\n"
                "Max length: 4 minutes when read aloud (about 500-550 words)\n"
                "Style: Super energetic, funny, educational but entertaining\n\n"
                "Choose ONE topic:\n"
                "- Top 10 funniest animal behaviors with crazy facts\n"
                "- Hilarious science facts that sound fake but are real\n"
                "- Weird world records that will make you laugh\n"
                "- Funny history facts nobody taught you in school\n"
                "- Amazing nature facts with funny commentary\n\n"
                "Return ONLY a JSON object:\n"
                "{\n"
                "  \"title\": \"funny engaging title under 60 chars\",\n"
                "  \"hook\": \"hilarious shocking opening line\",\n"
                "  \"script\": \"full funny script max 550 words, energetic narration\",\n"
                "  \"visual_descriptions\": [\"funny scene 1\", \"funny scene 2\", \"funny scene 3\", \"funny scene 4\", \"funny scene 5\", \"funny scene 6\"],\n"
                "  \"dalle_prompts\": [\"cute funny cartoon scene 1 colorful\", \"funny cute animal illustration 2\", \"colorful fun kids scene 3\"],\n"
                "  \"tags\": [\"kids\", \"funny\", \"animals\", \"facts\", \"comedy\", \"fun\", \"viral\", \"cartoon\", \"amazing\", \"educational\"],\n"
                "  \"description\": \"200 word fun description for kids and families\",\n"
                "  \"thumbnail_concept\": \"bright colorful funny thumbnail with cartoon character\"\n"
                "}\n\n"
                "No markdown, raw JSON only."
            )

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4000,
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
                "title": "10 Funniest Animal Facts That Will Make You LOL",
                "hook": "Did you know a group of flamingos is called a flamboyance?",
                "script": content,
                "visual_descriptions": ["funny cartoon animals", "colorful nature scene", "kids laughing", "cute animals playing", "funny science experiment", "cartoon explosion"],
                "dalle_prompts": ["cute funny cartoon animals laughing colorful", "funny science experiment cartoon kids", "colorful funny nature scene cartoon"],
                "tags": ["kids", "funny", "animals", "facts", "comedy", "fun", "viral", "cartoon", "amazing", "educational"],
                "description": "The funniest animal facts that will make you and your kids laugh!",
                "thumbnail_concept": "Bright colorful cartoon animals laughing, big text"
            }

        video_data["niche"] = "kids_funny"
        video_data["is_shorts"] = is_shorts
        return video_data

    def _get_performance_insight(self, analytics_data):
        return "Focus on funny engaging content for kids and families."
