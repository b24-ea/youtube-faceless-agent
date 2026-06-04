import json
import random


DARK_CONCEPTS = [
    "government secretly controls weather and uses it as a weapon",
    "shadow organization has been replacing world leaders with clones",
    "ancient evil entity awakens beneath a modern city",
    "paranormal investigator discovers portal to another dimension",
    "scientist uncovers proof that reality is a simulation gone wrong",
    "secret society performs ritual that summons something terrifying",
    "astronaut encounters alien presence that follows them back to earth",
    "small town residents discover they are all part of a dark experiment",
    "historian finds evidence that a historical disaster was deliberately caused",
    "deep sea explorer finds underwater civilization with horrifying secret",
    "journalist investigates disappearances and uncovers government cover-up",
    "family moves into house and discovers previous owners never left",
    "detective investigates case and realizes the killer is not human",
    "whistleblower leaks footage of something that should not exist",
    "archaeologist discovers ancient prophecy that is coming true now",
]


class ContentAgent:
    def __init__(self, client):
        self.client = client

    def generate_video(self, niche, analytics_data, used_concepts=None):
        used = used_concepts or []
        available = [c for c in DARK_CONCEPTS if c not in used]
        if not available:
            available = DARK_CONCEPTS
        concept = random.choice(available)

        prompt = (
            "You are creating a viral dark mystery and paranormal YouTube Shorts video.\n\n"
            "Concept: " + concept + "\n\n"
            "Create a 30-second EXTREMELY suspenseful and shocking dark video with:\n"
            "- Cinematic dark atmosphere with dramatic lighting\n"
            "- Shocking and terrifying visuals\n"
            "- Fast-paced cuts and dynamic camera movements\n"
            "- Dark conspiracy and paranormal elements\n"
            "- Intense build-up with shocking twist ending\n"
            "- Mysterious and eerie mood throughout\n\n"
            "The video_prompt must describe 4 connected dark scenes:\n"
            "Scene 1: Mysterious shocking opening that immediately creates dread\n"
            "Scene 2: Dark situation escalates with terrifying revelations\n"
            "Scene 3: Maximum horror and conspiracy at peak intensity\n"
            "Scene 4: Shocking unexpected dark twist ending\n\n"
            "IMPORTANT: Everything must be in English only.\n\n"
            "Return ONLY a JSON object:\n"
            "{\n"
            "  \"title\": \"dark mystery shorts title under 60 chars with #Shorts\",\n"
            "  \"video_prompt\": \"cinematic dark thriller scene, dramatic lighting, " +
            concept + ". Terrifying atmosphere, shocking visuals, intense pacing. "
            "Dark conspiracy and paranormal elements. Photorealistic, 9:16 vertical video.\",\n"
            "  \"description\": \"dark mysterious short description\",\n"
            "  \"tags\": [\"paranormal\", \"mystery\", \"horror\", \"conspiracy\", \"dark\", \"shorts\",
