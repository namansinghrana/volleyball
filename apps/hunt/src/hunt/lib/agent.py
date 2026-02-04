import os
from dotenv import load_dotenv

from models import GeoQuery
from tools import search_volleyball_facilities, geocode_location

from langchain_core.tools import StructuredTool
from langchain_groq import ChatGroq

# ----------------------------------------------------
# Load environment variables (.env → GROQ_API_KEY)
# ----------------------------------------------------
load_dotenv()


# ----------------------------------------------------
# TOOL FUNCTION (MUST be a plain function)
# LangChain tools CANNOT wrap class methods
# ----------------------------------------------------
def resolve_coordinates_fn(
    latitude: float = None,
    longitude: float = None,
    location: str = None
) -> dict:
    """
    Resolve geographic coordinates from:
    - explicit latitude & longitude OR
    - a human-readable location name
    """
    if latitude is not None and longitude is not None:
        return {"latitude": latitude, "longitude": longitude}

    if location is not None:
        lat, lon = geocode_location(location)
        return {"latitude": lat, "longitude": lon}

    raise ValueError("Missing location information")


# ----------------------------------------------------
# Convert the function into a LangChain StructuredTool
# ----------------------------------------------------
resolve_coordinates_tool = StructuredTool.from_function(
    func=resolve_coordinates_fn,
    name="resolve_coordinates",
    description="Resolve geographic coordinates from lat/lon or a location name"
)


# ----------------------------------------------------
# GeoAgent (Singleton)
# ----------------------------------------------------
class GeoAgent:
    """
    Agent responsible for:
    1. Resolving coordinates
    2. Classifying user intent
    3. Searching volleyball facilities if required
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """
        Initialize the Groq LLM via LangChain
        """
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
             model_name="llama-3.1-8b-instant",
            temperature=0
        )

    def run(self, query: GeoQuery):
        """
        Main execution flow for the agent
        """

        # --------------------------------------------
        # 1. Resolve coordinates using the tool
        # --------------------------------------------
        coords = resolve_coordinates_tool.invoke({
            "latitude": query.latitude,
            "longitude": query.longitude,
            "location": query.location
        })

        lat = coords["latitude"]
        lon = coords["longitude"]

        # --------------------------------------------
        # 2. Classify intent using the LLM
        # --------------------------------------------
        response = self.llm.invoke(
            "You are a classifier.\n"
            "You MUST answer with EXACTLY ONE WORD.\n"
            "Valid answers:\n"
            "- search_volleyball\n"
            "- other\n\n"
            "Do NOT explain.\n"
            "Do NOT add punctuation.\n"
            "Do NOT add extra text.\n\n"
            f"Query: {query.text_query}"
        )


        intent = response.content.strip().lower()

        # --------------------------------------------
        # 3. Conditional business logic
        # --------------------------------------------
        if intent == "search_volleyball":
            return search_volleyball_facilities(
                latitude=lat,
                longitude=lon,
                radius_km=query.radius_km
            )

        # --------------------------------------------
        # 4. Fallback response
        # --------------------------------------------
        return response.content
