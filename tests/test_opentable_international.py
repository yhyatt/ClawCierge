"""
Tests for OpenTable worldwide support — metroId for US cities, term-based for international.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from opentable import get_restaurant_search_url, OT_METRO_IDS
from city_registry import get_city


class TestOpenTableMetroIds:
    """Tests for OpenTable metroId handling."""

    def test_nyc_uses_metro_id(self):
        """NYC search should use metroId=4."""
        url = get_restaurant_search_url("nyc", covers=2)
        assert "metroId=4" in url
        assert "covers=2" in url

    def test_new_york_uses_metro_id(self):
        """'new york' should use metroId=4."""
        url = get_restaurant_search_url("new york", covers=2)
        assert "metroId=4" in url

    def test_new_york_hyphenated_uses_metro_id(self):
        """'new-york' should use metroId=4."""
        url = get_restaurant_search_url("new-york", covers=2)
        assert "metroId=4" in url

    def test_chicago_uses_metro_id(self):
        """Chicago should use metroId=2."""
        url = get_restaurant_search_url("chicago", covers=2)
        assert "metroId=2" in url

    def test_los_angeles_uses_metro_id(self):
        """Los Angeles should use metroId=3."""
        url = get_restaurant_search_url("los angeles", covers=2)
        assert "metroId=3" in url

    def test_bucharest_no_metro_id(self):
        """Bucharest (international) should NOT have metroId."""
        url = get_restaurant_search_url("bucharest", covers=2)
        assert "metroId" not in url
        # Should use term-based search with city name
        assert "bucharest" in url.lower() or "Bucharest" in url

    def test_rome_no_metro_id(self):
        """Rome (international) should NOT have metroId."""
        url = get_restaurant_search_url("rome", covers=2)
        assert "metroId" not in url
        assert "rome" in url.lower()

    def test_barcelona_no_metro_id(self):
        """Barcelona (international) should NOT have metroId."""
        url = get_restaurant_search_url("barcelona", covers=2)
        assert "metroId" not in url
        assert "barcelona" in url.lower()

    def test_london_no_metro_id(self):
        """London (international) should NOT have metroId."""
        url = get_restaurant_search_url("london", covers=2)
        assert "metroId" not in url
        assert "london" in url.lower()


class TestOpenTableUrlParams:
    """Tests for OpenTable URL parameter formatting."""

    def test_covers_in_url(self):
        """Covers parameter should be in URL."""
        url = get_restaurant_search_url("nyc", covers=4)
        assert "covers=4" in url

    def test_date_in_url(self):
        """Date and time should be in URL."""
        url = get_restaurant_search_url("nyc", date="2026-04-15", time="19:30", covers=2)
        assert "dateTime=2026-04-15T19:30:00" in url

    def test_date_default_time(self):
        """Date without time should default to 20:00."""
        url = get_restaurant_search_url("nyc", date="2026-04-15", covers=2)
        assert "dateTime=2026-04-15T20:00:00" in url

    def test_query_in_url(self):
        """Query parameter should be URL-encoded."""
        url = get_restaurant_search_url("nyc", query="Italian restaurant", covers=2)
        assert "Italian" in url or "italian" in url.lower()

    def test_international_includes_city_in_term(self):
        """International search should include city in search term."""
        url = get_restaurant_search_url("bucharest", query="fine dining", covers=2)
        assert "bucharest" in url.lower()
        assert "dining" in url.lower()


class TestBucharestRoutingIncludesOpenTable:
    """Tests for Bucharest routing in city_registry."""

    def test_bucharest_has_opentable(self):
        """Bucharest reservation_platforms should include opentable."""
        cfg = get_city("bucharest")
        assert cfg is not None
        assert "opentable" in cfg.reservation_platforms

    def test_bucharest_opentable_is_fallback(self):
        """OpenTable should be after bookingham (thefork removed for Bucharest)."""
        cfg = get_city("bucharest")
        platforms = cfg.reservation_platforms
        assert platforms.index("bookingham") < platforms.index("opentable")
        assert "thefork" not in platforms  # TheFork removed: redirects to Paris
        assert "opentable" in platforms


class TestUnifiedLabels:
    """Tests for unified.py OpenTable label handling."""

    def test_unified_label_nyc(self):
        """NYC search should show 'NYC — Resy / OpenTable' label."""
        import unified
        result = unified.search_and_format(
            city="new-york",
            date="2026-04-15",
            time="19:30",
            size=2,
        )
        assert "NYC" in result
        assert "Resy" in result
        assert "OpenTable" in result

    def test_unified_label_international(self):
        """Bucharest search should show 'OpenTable (worldwide)' label."""
        import unified
        result = unified.search_and_format(
            city="bucharest",
            date="2026-04-15",
            time="19:30",
            size=2,
        )
        assert "worldwide" in result.lower() or "OpenTable" in result
        # Should NOT say NYC for Bucharest
        assert "NYC — Resy" not in result

    def test_unified_bucharest_no_resy_link(self):
        """Bucharest should NOT have Resy link (Resy is NYC-only)."""
        import unified
        result = unified.search_and_format(
            city="bucharest",
            date="2026-04-15",
            time="19:30",
            size=2,
        )
        assert "resy.com" not in result.lower()


class TestMetroIdMapping:
    """Tests for OT_METRO_IDS dictionary."""

    def test_known_us_cities_have_metro_ids(self):
        """All known US cities should have metro IDs."""
        us_cities = ["nyc", "new-york", "chicago", "los angeles", "san francisco", "boston", "washington", "miami"]
        for city in us_cities:
            assert city in OT_METRO_IDS, f"Missing metro ID for {city}"

    def test_metro_ids_are_integers(self):
        """All metro IDs should be integers."""
        for city, metro_id in OT_METRO_IDS.items():
            assert isinstance(metro_id, int), f"Metro ID for {city} should be int"

    def test_metro_ids_are_positive(self):
        """All metro IDs should be positive."""
        for city, metro_id in OT_METRO_IDS.items():
            assert metro_id > 0, f"Metro ID for {city} should be positive"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
