from tools import search_volleyball_facilities

def test_search_returns_list():
    results = search_volleyball_facilities(
        latitude=30.3165,
        longitude=78.0322
    )
    assert isinstance(results, list)
