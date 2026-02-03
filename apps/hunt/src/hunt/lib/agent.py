import os
from groq import Groq
from dotenv import load_dotenv

from models import GeoQuery
from tools import search_volleyball_facilities, geocode_location
from prompts import AGENT_PROMPT

load_dotenv()


class GeoAgent:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "groq/compound"

    def run(self, query: GeoQuery) -> str:
        # -----------------------------
        # 1. Resolve coordinates safely
        # -----------------------------
        if query.latitude is not None and query.longitude is not None:
            lat, lon = query.latitude, query.longitude
        elif query.location is not None:
            lat, lon = geocode_location(query.location)
        else:
            raise ValueError(
                "GeoQuery must include either (latitude & longitude) or location"
            )

        # -----------------------------
        # 2. Let AI decide what to do
        # -----------------------------
        messages = [
            {"role": "system", "content": AGENT_PROMPT},
            {"role": "user", "content": query.text_query}
        ]

        decision = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )

        decision_text = decision.choices[0].message.content.lower()

        # -----------------------------
        # 3. AI-triggered search (bridge)
        # -----------------------------
        if "volleyball" in decision_text or "court" in decision_text:
            facilities = search_volleyball_facilities(
                latitude=lat,
                longitude=lon,
                radius_km=query.radius_km
            )

            messages.append({
                "role": "assistant",
                "content": decision.choices[0].message.content
            })

            messages.append({
                "role": "user",
                "content": f"Here are the search results:\n{facilities}"
            })

            final = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            return final.choices[0].message.content

        # -----------------------------
        # 4. No search required
        # -----------------------------
        return decision.choices[0].message.content
