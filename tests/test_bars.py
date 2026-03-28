"""
tests/test_bars.py — Unit tests for bars.py and unified.py bar routing.
"""
import sys
import os
import types
import importlib
from unittest.mock import patch, MagicMock

# Ensure reservation package root is on path
RESERVATION_DIR = os.path.dirname(os.path.dirname(__file__))
if RESERVATION_DIR not in sys.path:
    sys.path.insert(0, RESERVATION_DIR)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_place(name="Bar Foo", rating=8.2, price=2, address="Main St 1"):
    return {
        "name": name,
        "rating": rating,
        "price": price,
        "location": {"formatted_address": address},
        "categories": [{"name": "Bar"}],
        "tastes": ["craft beer", "live music"],
        "hours": {"open_now": True},
    }


def _mock_fsq_module(places=None):
    """Build a minimal mock of the clawtourism.foursquare module."""
    if places is None:
        places = [_make_place()]

    fsq = MagicMock()
    fsq.search_bars.return_value = places
    fsq.search_cafes.return_value = places
    fsq.format_report.side_effect = lambda ps, title: f"{title}\n" + "\n".join(
        p["name"] for p in ps
    )
    return fsq


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_search_bars_returns_string():
    """search_bars() returns a non-empty string with the location name."""
    import bars
    fsq = _mock_fsq_module([_make_place("Zum Wohl"), _make_place("Bar Central")])
    with patch.object(bars, "_load_foursquare", return_value=fsq):
        result = bars.search_bars("Vienna")
    assert isinstance(result, str)
    assert "Vienna" in result
    assert len(result) > 0


def test_search_wine_bars_returns_string():
    """search_wine_bars() passes bar_type='wine bar' to foursquare and returns a string."""
    import bars
    places = [_make_place("HaYain HaTov", rating=8.8)]
    fsq = _mock_fsq_module(places)
    with patch.object(bars, "_load_foursquare", return_value=fsq):
        result = bars.search_wine_bars("Tel Aviv")
    assert isinstance(result, str)
    assert "Tel Aviv" in result
    # Verify the correct bar_type was passed
    fsq.search_bars.assert_called_once()
    _, kwargs = fsq.search_bars.call_args
    assert kwargs.get("bar_type") == "wine bar"


def test_search_cocktail_bars_returns_string():
    """search_cocktail_bars() passes bar_type='cocktail bar'."""
    import bars
    fsq = _mock_fsq_module([_make_place("Dry Martini")])
    with patch.object(bars, "_load_foursquare", return_value=fsq):
        result = bars.search_cocktail_bars("Barcelona")
    assert isinstance(result, str)
    fsq.search_bars.assert_called_once()
    _, kwargs = fsq.search_bars.call_args
    assert kwargs.get("bar_type") == "cocktail bar"


def test_search_cafes_returns_string():
    """search_cafes() calls fsq.search_cafes and returns a string."""
    import bars
    fsq = _mock_fsq_module([_make_place("Gerbeaud Café")])
    with patch.object(bars, "_load_foursquare", return_value=fsq):
        result = bars.search_cafes("Budapest")
    assert isinstance(result, str)
    assert "Budapest" in result
    fsq.search_cafes.assert_called_once()


def test_foursquare_unavailable_returns_fallback():
    """When clawtourism cannot be imported, search_bars returns a fallback string."""
    import bars
    # Reset cached module so it re-runs import logic
    bars._fsq = None
    with patch.object(bars, "_load_foursquare", return_value=None):
        result = bars.search_bars("Vienna")
    assert isinstance(result, str)
    assert "unavailable" in result.lower() or "Foursquare" in result


def test_detect_bar_type_wine():
    import bars
    assert bars.detect_bar_type("wine bars in Tel Aviv") == "wine bar"
    assert bars.detect_bar_type("Wine Bar near me") == "wine bar"


def test_detect_bar_type_cocktail():
    import bars
    assert bars.detect_bar_type("cocktail bars Barcelona") == "cocktail bar"
    assert bars.detect_bar_type("best cocktails") == "cocktail bar"


def test_detect_bar_type_cafe():
    import bars
    assert bars.detect_bar_type("good café for working in Budapest") == "cafe"
    assert bars.detect_bar_type("coffee shops Prague") == "cafe"
    assert bars.detect_bar_type("cafe near me") == "cafe"


def test_detect_bar_type_bar():
    import bars
    assert bars.detect_bar_type("best bars in Vienna") == "bar"
    assert bars.detect_bar_type("nightlife Budapest") == "bar"
    assert bars.detect_bar_type("pub in London") == "bar"


def test_detect_bar_type_none():
    import bars
    assert bars.detect_bar_type("restaurant near me") is None
    assert bars.detect_bar_type("sushi in tokyo") is None
    assert bars.detect_bar_type("") is None


# ── unified.py routing tests ───────────────────────────────────────────────────

def test_keywords_route_to_bars():
    """unified.is_bars_query() correctly identifies bar/nightlife queries."""
    # Import unified via sys.path already set
    import unified
    assert unified.is_bars_query("best bars in Vienna") is True
    assert unified.is_bars_query("wine bars in Tel Aviv") is True
    assert unified.is_bars_query("cocktail bars Barcelona") is True
    assert unified.is_bars_query("good café for working in Budapest") is True
    assert unified.is_bars_query("nightlife") is True
    assert unified.is_bars_query("drinks in Berlin") is True


def test_restaurant_queries_not_routed_to_bars():
    """unified.is_bars_query() returns False for restaurant queries."""
    import unified
    assert unified.is_bars_query("book a restaurant in Paris") is False
    assert unified.is_bars_query("sushi place Tokyo") is False
    assert unified.is_bars_query(None) is False
    assert unified.is_bars_query("") is False


def test_search_nightlife_and_format_calls_bars():
    """unified.search_nightlife_and_format() delegates to bars module."""
    import unified
    import bars
    fsq = _mock_fsq_module([_make_place("The Ritz Bar")])
    with patch.object(bars, "_load_foursquare", return_value=fsq):
        result = unified.search_nightlife_and_format("London", "best bars")
    assert isinstance(result, str)
    assert len(result) > 0
