"""Tests for city_registry module."""
import pytest
import sys
import os

# Add parent package to path for imports (bypass __init__.py issues)
parent_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parent_dir)

# Import directly from city_registry module
from city_registry import CITIES, get_city, list_cities, cities_for_country


def test_bucharest_routing():
    """Bucharest should have correct routing platforms."""
    cfg = get_city("bucharest")
    assert cfg is not None
    assert "bookingham" in cfg.reservation_platforms
    assert "thefork" in cfg.reservation_platforms
    # Bookingham should be primary (first)
    assert cfg.reservation_platforms[0] == "bookingham"


def test_all_aliases_resolve():
    """All aliases should resolve to their parent city."""
    for slug, cfg in CITIES.items():
        for alias in cfg.aliases:
            resolved = get_city(alias)
            assert resolved is not None, f"Alias '{alias}' did not resolve"
            assert resolved.slug == slug, f"Alias '{alias}' resolved to wrong city"


def test_michelin_slugs_correct():
    """Michelin slugs should be correct for indexed cities."""
    # Barcelona should have Michelin slug
    bcn = get_city("barcelona")
    assert bcn is not None
    assert bcn.michelin_slug == "barcelona"
    assert bcn.michelin_indexed is True
    
    # NYC should have Michelin slug
    nyc = get_city("nyc")
    assert nyc is not None
    assert nyc.michelin_slug == "new-york"
    assert nyc.michelin_indexed is True
    
    # Tel Aviv should NOT have Michelin slug
    tlv = get_city("tel-aviv")
    assert tlv is not None
    assert tlv.michelin_slug is None
    assert tlv.michelin_indexed is False
    
    # Bucharest should NOT have Michelin slug (Romania not indexed)
    buc = get_city("bucharest")
    assert buc is not None
    assert buc.michelin_slug is None
    assert buc.michelin_indexed is False


def test_timeout_paths_present_for_supported_cities():
    """Timeout paths should be present for supported cities."""
    # NYC has Time Out
    nyc = get_city("new-york")
    assert nyc is not None
    assert nyc.timeout_path is not None
    assert "newyork" in nyc.timeout_path
    
    # Barcelona has Time Out
    bcn = get_city("barcelona")
    assert bcn is not None
    assert bcn.timeout_path is not None
    assert "barcelona" in bcn.timeout_path
    
    # Tel Aviv has Time Out (Israel page)
    tlv = get_city("tel-aviv")
    assert tlv is not None
    assert tlv.timeout_path is not None
    assert "israel" in tlv.timeout_path
    
    # Bucharest does NOT have Time Out
    buc = get_city("bucharest")
    assert buc is not None
    assert buc.timeout_path is None


def test_city_routing_derived():
    """CITY_ROUTING should be derived from registry."""
    from unified import CITY_ROUTING
    
    # Tel Aviv aliases should all map to same platforms
    assert CITY_ROUTING.get("tel-aviv") == ["ontopo", "tabit"]
    assert CITY_ROUTING.get("tlv") == ["ontopo", "tabit"]
    
    # Barcelona
    assert CITY_ROUTING.get("barcelona") == ["thefork"]
    assert CITY_ROUTING.get("bcn") == ["thefork"]
    
    # NYC
    assert CITY_ROUTING.get("nyc") == ["resy", "opentable"]
    assert CITY_ROUTING.get("new-york") == ["resy", "opentable"]
    
    # Bucharest (now includes opentable as fallback)
    assert CITY_ROUTING.get("bucharest") == ["bookingham", "thefork", "opentable"]
    assert CITY_ROUTING.get("buc") == ["bookingham", "thefork", "opentable"]


def test_recommender_michelin_slugs_derived():
    """recommender.py MICHELIN_CITY_SLUGS should be derived from registry."""
    from recommender import MICHELIN_CITY_SLUGS
    
    # Should contain aliases
    assert "barcelona" in MICHELIN_CITY_SLUGS
    assert "bcn" in MICHELIN_CITY_SLUGS
    assert MICHELIN_CITY_SLUGS["barcelona"] == "barcelona"
    
    # NYC variations
    assert "nyc" in MICHELIN_CITY_SLUGS
    assert "new_york" in MICHELIN_CITY_SLUGS or "new-york" in MICHELIN_CITY_SLUGS
    assert MICHELIN_CITY_SLUGS["nyc"] == "new-york"
    
    # Non-indexed cities should be None
    assert "tel_aviv" in MICHELIN_CITY_SLUGS or "tel-aviv" in MICHELIN_CITY_SLUGS
    assert MICHELIN_CITY_SLUGS.get("tel_aviv") is None or MICHELIN_CITY_SLUGS.get("tel-aviv") is None


def test_recommender_timeout_paths_derived():
    """recommender.py TIMEOUT_PATHS should be derived from registry."""
    from recommender import TIMEOUT_PATHS
    
    # NYC
    assert "nyc" in TIMEOUT_PATHS or "new_york" in TIMEOUT_PATHS
    
    # Barcelona
    assert "barcelona" in TIMEOUT_PATHS
    
    # Bucharest should NOT be in (no Time Out coverage)
    assert "bucharest" not in TIMEOUT_PATHS


def test_cnt_paths_derived():
    """recommender.py CNT_PATHS should be derived from registry."""
    from recommender import CNT_PATHS
    
    # Barcelona has CNT
    assert "barcelona" in CNT_PATHS
    assert len(CNT_PATHS["barcelona"]) > 0
    
    # NYC has CNT
    assert "nyc" in CNT_PATHS or "new_york" in CNT_PATHS
    
    # Bucharest has no CNT
    assert "bucharest" not in CNT_PATHS


def test_israel_cities():
    """Israel should have multiple cities for reservations."""
    israel = cities_for_country("IL")
    slugs = [c.slug for c in israel]
    assert "tel-aviv" in slugs
    assert "jerusalem" in slugs
    assert "haifa" in slugs
    assert len(israel) >= 4  # tel-aviv, jerusalem, haifa, eilat, herzliya


def test_get_city_case_insensitive():
    """get_city should be case-insensitive."""
    assert get_city("TLV") is not None
    assert get_city("tlv") is not None
    assert get_city("Tlv") is not None
    assert get_city("BCN") is not None
    assert get_city("NYC") is not None


def test_list_cities_includes_all():
    """list_cities should include all cities."""
    slugs = list_cities()
    assert "tel-aviv" in slugs
    assert "barcelona" in slugs
    assert "new-york" in slugs
    assert "bucharest" in slugs
    assert "jerusalem" in slugs
    assert len(slugs) >= 10  # We have many cities in reservation skill


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
