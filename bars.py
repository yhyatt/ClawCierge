"""
bars.py — Bars & Nightlife search for clawcierge.

Routes bar/nightlife/café queries through Foursquare (clawtourism).
Falls back gracefully if clawtourism is not available.

Usage:
    from bars import search_bars, search_wine_bars, search_cocktail_bars, search_cafes

Trigger keywords:
    bar, bars, nightlife, cocktail, wine bar, pub, drinks, café, cafe, coffee
"""
from __future__ import annotations

import sys
import os

# ── Foursquare import (clawtourism) ──────────────────────────────────────────
_CLAWTOURISM_PATH = "/home/openclaw/.openclaw/workspace/skills/clawtourism"
_fsq = None

def _load_foursquare():
    global _fsq
    if _fsq is not None:
        return _fsq
    if _CLAWTOURISM_PATH not in sys.path:
        sys.path.insert(0, _CLAWTOURISM_PATH)
    try:
        from clawtourism import foursquare as fsq
        _fsq = fsq
    except ImportError:
        _fsq = None
    return _fsq


def _unavailable_msg(kind: str, location: str) -> str:
    return (
        f"🍸 *{kind} in {location}*\n\n"
        "Foursquare data unavailable (clawtourism not installed).\n"
        "Try: pip install -e /home/openclaw/.openclaw/workspace/skills/clawtourism"
    )


# ── Public API ────────────────────────────────────────────────────────────────

def search_bars(
    location: str,
    top_n: int = 8,
    min_rating: float = 7.0,
    radius_m: int = 2000,
) -> str:
    """Return a formatted string of top bars in location."""
    fsq = _load_foursquare()
    if fsq is None:
        return _unavailable_msg("Bars", location)
    try:
        places = fsq.search_bars(
            location=location,
            bar_type="bar",
            radius_m=radius_m,
            min_rating=min_rating,
            top_n=top_n,
        )
        return fsq.format_report(places, f"🍺 *Bars in {location}* (Foursquare)")
    except Exception as e:
        return f"🍺 Bars in {location}\n\nError: {e}"


def search_wine_bars(
    location: str,
    top_n: int = 8,
    min_rating: float = 7.0,
    radius_m: int = 2000,
) -> str:
    """Return a formatted string of top wine bars in location."""
    fsq = _load_foursquare()
    if fsq is None:
        return _unavailable_msg("Wine Bars", location)
    try:
        places = fsq.search_bars(
            location=location,
            bar_type="wine bar",
            radius_m=radius_m,
            min_rating=min_rating,
            top_n=top_n,
        )
        return fsq.format_report(places, f"🍷 *Wine Bars in {location}* (Foursquare)")
    except Exception as e:
        return f"🍷 Wine Bars in {location}\n\nError: {e}"


def search_cocktail_bars(
    location: str,
    top_n: int = 8,
    min_rating: float = 7.0,
    radius_m: int = 2000,
) -> str:
    """Return a formatted string of top cocktail bars in location."""
    fsq = _load_foursquare()
    if fsq is None:
        return _unavailable_msg("Cocktail Bars", location)
    try:
        places = fsq.search_bars(
            location=location,
            bar_type="cocktail bar",
            radius_m=radius_m,
            min_rating=min_rating,
            top_n=top_n,
        )
        return fsq.format_report(places, f"🍸 *Cocktail Bars in {location}* (Foursquare)")
    except Exception as e:
        return f"🍸 Cocktail Bars in {location}\n\nError: {e}"


def search_cafes(
    location: str,
    top_n: int = 8,
    min_rating: float = 7.0,
    radius_m: int = 1500,
) -> str:
    """Return a formatted string of top cafés/coffee shops in location."""
    fsq = _load_foursquare()
    if fsq is None:
        return _unavailable_msg("Cafés", location)
    try:
        places = fsq.search_cafes(
            location=location,
            radius_m=radius_m,
            min_rating=min_rating,
            top_n=top_n,
        )
        return fsq.format_report(places, f"☕ *Cafés in {location}* (Foursquare)")
    except Exception as e:
        return f"☕ Cafés in {location}\n\nError: {e}"


# ── Keyword detection ─────────────────────────────────────────────────────────

BAR_KEYWORDS = {
    "bar", "bars", "nightlife", "cocktail", "cocktails",
    "wine bar", "wine bars", "pub", "pubs", "drinks",
}
CAFE_KEYWORDS = {"café", "cafe", "cafes", "cafés", "coffee"}


def detect_bar_type(query: str) -> str | None:
    """
    Return bar type for routing, or None if query is not bar/nightlife.
    Returns: "wine bar" | "cocktail bar" | "cafe" | "bar" | None
    """
    q = query.lower()
    if "wine bar" in q or "wine bars" in q:
        return "wine bar"
    if "cocktail" in q:
        return "cocktail bar"
    if any(kw in q for kw in CAFE_KEYWORDS):
        return "cafe"
    if any(kw in q for kw in BAR_KEYWORDS):
        return "bar"
    return None


def search_nightlife(location: str, query: str, top_n: int = 8) -> str:
    """
    Dispatch to the right bar/café function based on the query string.
    Returns a formatted string.
    """
    bar_type = detect_bar_type(query)
    if bar_type == "wine bar":
        return search_wine_bars(location, top_n=top_n)
    if bar_type == "cocktail bar":
        return search_cocktail_bars(location, top_n=top_n)
    if bar_type == "cafe":
        return search_cafes(location, top_n=top_n)
    return search_bars(location, top_n=top_n)
