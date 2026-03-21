"""
Tests for Bucharest restaurant support — Bookingham, curated list, TheFork routing.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import bookingham
import maps
import unified
from city_registry import get_city, CITIES
from thefork import CITY_SLUGS as THEFORK_CITY_SLUGS


class TestBookinghamModule:
    """Tests for bookingham.py module."""

    def test_bookingham_city_url_bucharest(self):
        """Verify Bucharest city URL format."""
        url = bookingham.get_city_search_url("bucharest")
        assert url == "https://bookingham.ro/bucuresti"

    def test_bookingham_city_url_bucuresti_alias(self):
        """Verify bucuresti alias works."""
        url = bookingham.get_city_search_url("bucuresti")
        assert url == "https://bookingham.ro/bucuresti"

    def test_bookingham_city_url_buc_alias(self):
        """Verify buc alias works."""
        url = bookingham.get_city_search_url("buc")
        assert url == "https://bookingham.ro/bucuresti"

    def test_bookingham_city_url_cluj(self):
        """Verify Cluj-Napoca URL."""
        url = bookingham.get_city_search_url("cluj")
        assert url == "https://bookingham.ro/cluj-napoca"

    def test_bookingham_city_url_case_insensitive(self):
        """Verify case insensitivity."""
        url = bookingham.get_city_search_url("BUCHAREST")
        assert url == "https://bookingham.ro/bucuresti"

    def test_bookingham_city_url_unknown_falls_back_to_bucuresti(self):
        """Unknown city falls back to Bucharest."""
        url = bookingham.get_city_search_url("unknown-city")
        assert url == "https://bookingham.ro/bucuresti"

    def test_bookingham_restaurant_url(self):
        """Verify restaurant search URL format."""
        url = bookingham.get_restaurant_url("NOUA", "bucharest")
        assert url == "https://bookingham.ro/bucuresti?search=NOUA"

    def test_bookingham_restaurant_url_with_spaces(self):
        """Verify restaurant name with spaces is URL-encoded."""
        url = bookingham.get_restaurant_url("Caru' cu Bere", "bucharest")
        assert "Caru" in url
        assert "search=" in url
        # URL-encoded apostrophe and space
        assert "%27" in url or "'" not in url.split("=")[1]

    def test_bookingham_direct_restaurant_url(self):
        """Verify direct restaurant URL builder."""
        url = bookingham.get_direct_restaurant_url("bucuresti/restaurante/noua")
        assert url == "https://bookingham.ro/bucuresti/restaurante/noua"

    def test_bookingham_is_city_supported(self):
        """Verify city support check."""
        assert bookingham.is_city_supported("bucharest") is True
        assert bookingham.is_city_supported("cluj") is True
        assert bookingham.is_city_supported("london") is False

    def test_bookingham_list_supported_cities(self):
        """Verify list of supported cities."""
        cities = bookingham.list_supported_cities()
        assert "bucuresti" in cities
        assert "cluj-napoca" in cities
        assert len(cities) >= 5  # At least the main Romanian cities


class TestBucharestCuratedList:
    """Tests for Bucharest entries in maps.py CURATED dict."""

    def test_bucharest_in_curated(self):
        """Curated list has Bucharest entries."""
        curated = maps.get_curated("bucharest")
        assert curated is not None
        assert len(curated) > 0

    def test_bucharest_curated_has_noua(self):
        """NOUA restaurant is in curated list."""
        curated = maps.get_curated("bucharest")
        names = [r["name"] for r in curated]
        assert "NOUA" in names

    def test_bucharest_curated_noua_is_kai_pick(self):
        """NOUA is marked as kai_pick."""
        curated = maps.get_curated("bucharest")
        noua = next((r for r in curated if r["name"] == "NOUA"), None)
        assert noua is not None
        assert noua.get("kai_pick") is True

    def test_bucharest_curated_has_expected_restaurants(self):
        """Verify expected restaurants are in the list."""
        curated = maps.get_curated("bucharest")
        names = [r["name"] for r in curated]
        expected = ["NOUA", "Kaiamo", "Kane", "deSoi", "Caru' cu Bere"]
        for name in expected:
            assert name in names, f"Missing expected restaurant: {name}"

    def test_bucharest_curated_all_have_booking_platform(self):
        """All Bucharest entries specify a booking platform."""
        curated = maps.get_curated("bucharest")
        for r in curated:
            assert "booking_platform" in r, f"{r['name']} missing booking_platform"

    def test_bucharest_curated_uses_bookingham(self):
        """All Bucharest entries use bookingham as booking platform."""
        curated = maps.get_curated("bucharest")
        for r in curated:
            assert r.get("booking_platform") == "bookingham", f"{r['name']} should use bookingham"

    def test_bucharest_curated_count(self):
        """Verify we have at least 10 curated restaurants."""
        curated = maps.get_curated("bucharest")
        assert len(curated) >= 10


class TestBucharestCityRegistry:
    """Tests for Bucharest in city_registry.py."""

    def test_bucharest_in_city_registry(self):
        """Bucharest is in the city registry."""
        cfg = get_city("bucharest")
        assert cfg is not None

    def test_bucharest_aliases(self):
        """Bucharest aliases work."""
        assert get_city("bucharest") is not None
        assert get_city("buc") is not None
        assert get_city("bucuresti") is not None

    def test_bucharest_routing_uses_bookingham(self):
        """Bucharest routing includes bookingham."""
        cfg = get_city("bucharest")
        assert "bookingham" in cfg.reservation_platforms

    def test_bucharest_routing_includes_thefork(self):
        """Bucharest routing includes thefork as secondary."""
        cfg = get_city("bucharest")
        assert "thefork" in cfg.reservation_platforms

    def test_bucharest_not_michelin_indexed(self):
        """Romania is not Michelin indexed."""
        cfg = get_city("bucharest")
        assert cfg.michelin_indexed is False

    def test_bucharest_country_is_romania(self):
        """Bucharest is in Romania."""
        cfg = get_city("bucharest")
        assert cfg.country == "RO"


class TestBucharestUnified:
    """Tests for Bucharest in unified.py."""

    def test_bucharest_in_city_routing(self):
        """Bucharest is in CITY_ROUTING."""
        platforms = unified._get_platforms("bucharest")
        assert "bookingham" in platforms

    def test_search_and_format_bucharest(self):
        """Smoke test search_and_format for Bucharest."""
        result = unified.search_and_format(
            city="bucharest",
            date="2026-04-15",
            time="19:30",
            size=2,
        )
        assert "Bucharest" in result
        assert "Curated picks" in result
        assert "NOUA" in result
        assert "Bookingham" in result
        assert "bookingham.ro" in result

    def test_search_and_format_bucharest_shows_thefork(self):
        """Bucharest search also shows TheFork link."""
        result = unified.search_and_format(
            city="bucharest",
            date="2026-04-15",
            time="19:30",
            size=2,
        )
        assert "TheFork" in result

    def test_browser_handoff_bookingham(self):
        """get_browser_handoff_url works for bookingham."""
        url = unified.get_browser_handoff_url(
            platform="bookingham",
            city="bucharest",
            date="2026-04-15",
            time="19:30",
            size=2,
        )
        assert url == "https://bookingham.ro/bucuresti"

    def test_browser_handoff_bookingham_with_restaurant_url(self):
        """get_browser_handoff_url respects direct restaurant URL."""
        direct_url = "https://bookingham.ro/bucuresti/restaurante/noua"
        url = unified.get_browser_handoff_url(
            platform="bookingham",
            city="bucharest",
            restaurant_url=direct_url,
            date="2026-04-15",
            time="19:30",
            size=2,
        )
        assert url == direct_url

    def test_get_booking_url_bookingham(self):
        """_get_booking_url handles bookingham platform."""
        restaurant = {"name": "NOUA", "booking_platform": "bookingham"}
        url = unified._get_booking_url(restaurant, "bucharest", "2026-04-15", "19:30", 2)
        assert "bookingham.ro" in url
        assert "NOUA" in url


class TestTheForkBucharest:
    """Tests for TheFork Bucharest coverage."""

    def test_thefork_has_bucharest_slug(self):
        """TheFork CITY_SLUGS includes Bucharest."""
        assert "bucharest" in THEFORK_CITY_SLUGS or "bucuresti" in THEFORK_CITY_SLUGS

    def test_thefork_bucharest_search_url(self):
        """TheFork search URL works for Bucharest."""
        from thefork import get_city_search_url
        url = get_city_search_url("bucharest", covers=2)
        assert "thefork.com" in url
        assert "bucharest" in url.lower() or "covers=2" in url
