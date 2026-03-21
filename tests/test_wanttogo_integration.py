"""
Tests for wanttogo.txt integration with maps.py curated lists.

These tests verify:
1. Personal saves from wanttogo.txt are loaded and marked as kai_pick
2. Personal saves take priority over hardcoded entries
3. Non-restaurants are filtered out
4. Bucharest specifically includes Vacamuuu
"""

import sys
from pathlib import Path

# Add skills path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.reservation.maps import get_curated, _load_wanttogo_index


def test_bucharest_curated_includes_vacamuuu():
    """Vacamuuu must be in Bucharest curated list (Yonatan's saved place)."""
    bucharest = get_curated("bucharest")
    names = [e.get("name", "").lower() for e in bucharest]
    assert "vacamuuu" in names, f"Vacamuuu not found in Bucharest. Got: {names}"


def test_bucharest_curated_marks_kai_picks():
    """Personal saves from wanttogo should have kai_pick=True."""
    bucharest = get_curated("bucharest")
    vacamuuu = [e for e in bucharest if "vacamu" in e.get("name", "").lower()]
    assert vacamuuu, "Vacamuuu not found in Bucharest"
    assert vacamuuu[0].get("kai_pick") is True, "Vacamuuu should be marked as kai_pick"


def test_curated_wanttogo_takes_priority():
    """Personal saves should appear before hardcoded entries."""
    bucharest = get_curated("bucharest")
    
    # Find first kai_pick and first non-kai_pick
    first_kai_pick_idx = None
    first_non_kai_pick_idx = None
    
    for i, entry in enumerate(bucharest):
        if entry.get("kai_pick") and first_kai_pick_idx is None:
            first_kai_pick_idx = i
        if not entry.get("kai_pick") and first_non_kai_pick_idx is None:
            first_non_kai_pick_idx = i
    
    # If both exist, kai_pick should come first
    if first_kai_pick_idx is not None and first_non_kai_pick_idx is not None:
        assert first_kai_pick_idx < first_non_kai_pick_idx, \
            f"kai_pick entries should come first. kai_pick at {first_kai_pick_idx}, non-kai_pick at {first_non_kai_pick_idx}"


def test_no_non_restaurants_in_curated():
    """Zoo, water parks, hotels, etc. should not appear in curated lists."""
    non_restaurants = ["zoo bucharest", "therme bucharest", "children's town bucharest", 
                       "bran castle", "sinaia", "mamaia"]
    
    bucharest = get_curated("bucharest")
    names = [e.get("name", "").lower() for e in bucharest]
    
    for bad in non_restaurants:
        assert bad not in names, f"Non-restaurant '{bad}' found in curated list"


def test_wanttogo_index_loads():
    """wanttogo_by_city.json should load successfully."""
    index = _load_wanttogo_index()
    assert isinstance(index, dict), "Index should be a dict"
    # Should have at least bucharest after parsing
    assert "bucharest" in index or "tel-aviv" in index, f"Index should have cities. Got keys: {list(index.keys())}"


def test_bucharest_has_expected_restaurants():
    """Bucharest should include key restaurants from wanttogo.txt."""
    expected = ["jw steakhouse", "vacamuuu", "kaiamo", "osho", "nor sky casual restaurant", 
                "kupaj gourmet", "eggcetera"]
    
    bucharest = get_curated("bucharest")
    names = [e.get("name", "").lower() for e in bucharest]
    
    for restaurant in expected:
        assert restaurant in names, f"Expected '{restaurant}' in Bucharest, not found"


def test_no_cluj_restaurants_in_bucharest():
    """Cluj restaurants should not appear in Bucharest list."""
    cluj_restaurants = ["twelve by brava", "hamburger cluj - meat up", "london brothers cluj"]
    
    bucharest = get_curated("bucharest")
    names = [e.get("name", "").lower() for e in bucharest]
    
    for cluj_place in cluj_restaurants:
        assert cluj_place not in names, f"Cluj restaurant '{cluj_place}' found in Bucharest"


def test_deduplication_by_name():
    """Same restaurant shouldn't appear twice in curated list."""
    bucharest = get_curated("bucharest")
    names = [e.get("name", "").lower() for e in bucharest]
    
    # Check for duplicates
    seen = set()
    for name in names:
        assert name not in seen, f"Duplicate restaurant: {name}"
        seen.add(name)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
