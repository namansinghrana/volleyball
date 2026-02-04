import os
from groq import Groq
from dotenv import load_dotenv

from models import GeoQuery
from tools import search_volleyball_facilities, geocode_location
from prompts import AGENT_PROMPT
from langchain_core.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq

def _resolve_coordinates(
    latitude: float = None,
    longitude: float = None,
    location: str = None
) -> dict:
    """Resolve coordinates from lat/lon or a location name."""
    if latitude is not None and longitude is not None:
        return {"latitude": latitude, "longitude": longitude}
    if location is not None:
        lat, lon = geocode_location(location)
        return {"latitude": lat, "longitude": lon}
    raise ValueError("Missing location information")


resolve_coordinates = StructuredTool.from_function(
    func=_resolve_coordinates,
    name="resolve_coordinates",
    description="Resolve geographic coordinates from lat/lon or a location name"
)


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
        # 1. Resolve coordinates (LangChain tool)
        # -----------------------------
        coords = resolve_coordinates.invoke({
            "latitude": query.latitude,
            "longitude": query.longitude,
            "location": query.location
        })

        lat = coords["latitude"]
        lon = coords["longitude"]


        decision = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Classify the intent of this query.\n"
                        "Return ONLY one word: search_volleyball or other.\n\n"
                        f"Query: {query.text_query}"
                    )
                }
            ],
            temperature=0
        )

        intent = decision.choices[0].message.content.strip().lower()

        
        if intent == "search_volleyball":
            facilities = search_volleyball_facilities(
                latitude=lat,
                longitude=lon,
                radius_km=query.radius_km
            )
            return facilities

        # -----------------------------
        # 4. No search required
        # -----------------------------
        return decision.choices[0].message.content
