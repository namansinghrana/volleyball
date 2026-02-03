from OSMPythonTools.overpass import Overpass
from OSMPythonTools.nominatim import Nominatim

overpass = Overpass()
nominatim = Nominatim()


def geocode_location(location: str) -> tuple[float, float]:
    """
    Convert a place name into coordinates.
    """
    results = list(nominatim.query(location))

    if not results:
        raise ValueError(
            f"Nominatim could not resolve location: '{location}'"
        )

    data = results[0].toJSON()
    return float(data["lat"]), float(data["lon"])


def search_volleyball_facilities(
    latitude: float,
    longitude: float,
    radius_km: float = 5.0
) -> list[dict]:
    """
    Deterministic, LLM-safe OSM search tool.
    """

    delta = radius_km / 111  # km → degrees

    south = latitude - delta
    north = latitude + delta
    west = longitude - delta
    east = longitude + delta

    query = f"""
    (
      node["leisure"="pitch"]["sport"="volleyball"]({south},{west},{north},{east});
      way["leisure"="pitch"]["sport"="volleyball"]({south},{west},{north},{east});
      relation["leisure"="pitch"]["sport"="volleyball"]({south},{west},{north},{east});
    );
    out center;
    """

    result = overpass.query(query)

    facilities = []
    for el in result.elements():
        tags = el.tags() or {}

        facilities.append({
            "name": tags.get("name", "Unnamed Facility"),
            "feature_type": "leisure=pitch / sport=volleyball",
            "description": tags.get("description", "No description"),
            "lat": el.centerLat() or el.lat(),
            "lon": el.centerLon() or el.lon(),
        })

    return facilities
