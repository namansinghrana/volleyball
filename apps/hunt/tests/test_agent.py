from agent import GeoAgent
from models import GeoQuery

def test_agent_runs_without_error():
    agent = GeoAgent()
    query = GeoQuery(text_query="Volleyball courts in Dehradun")
    result = agent.run(query)
    assert isinstance(result, str)
