from agent import GeoAgent
from models import GeoQuery


if __name__ == "__main__":
    query = GeoQuery(
        text_query="Find volleyball courts",
        location="Dehradun, India",
        radius_km=5
    )

    agent = GeoAgent()
    result = agent.run(query)
    print(result)
