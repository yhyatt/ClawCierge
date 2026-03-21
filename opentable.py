"""
OpenTable / Resy client — Worldwide 🌍 (USA metro IDs, term-based for international)
=====================================================================================
Direct API returns 403. Browser co-pilot is the only path.

OpenTable: Worldwide restaurant booking
Resy:      Dominant in NYC for top-tier restaurants (Don Angie, Lilia, Via Carota, etc.)

Both are browser-handoff only. We construct pre-filled URLs.
"""
import requests

OT_BASE = "https://www.opentable.com"
RESY_BASE = "https://resy.com"

# OpenTable metro IDs for US cities (discovered via OpenTable web UI)
# International cities use term-based search (no metroId)
OT_METRO_IDS = {
    "new-york":      4,
    "new york":      4,
    "nyc":           4,
    "chicago":       2,
    "los angeles":   3,
    "los-angeles":   3,
    "san francisco": 5,
    "san-francisco": 5,
    "boston":        6,
    "washington":    7,
    "miami":         8,
    # International cities — no metroId; use term-based search
    # bucharest, rome, paris, barcelona, london, etc. → no metroId
}


def get_restaurant_search_url(city: str, query: str = "", covers: int = 2,
                               date: str = "", time: str = "") -> str:
    """
    OpenTable search URL for any city worldwide.
    
    Uses metroId for known US cities, term-based search for international.
    
    Args:
        city: City name (case-insensitive)
        query: Restaurant name or cuisine query
        covers: Party size
        date: YYYY-MM-DD format
        time: HH:MM format
        
    Returns:
        Pre-filled OpenTable search URL for browser handoff.
    """
    metro_id = OT_METRO_IDS.get(city.lower())
    term = requests.utils.quote(query or "restaurant")
    
    if metro_id:
        # US city with known metroId
        url = f"{OT_BASE}/s?metroId={metro_id}&term={term}"
    else:
        # International / unknown cities: use city name as search term
        city_term = requests.utils.quote(f"{query or 'restaurant'} {city}".strip())
        url = f"{OT_BASE}/s?term={city_term}"
    
    if covers:
        url += f"&covers={covers}"
    if date:
        url += f"&dateTime={date}T{time or '20:00'}:00"
    return url


def get_resy_url(venue_slug: str, city_slug: str, date: str, covers: int = 2) -> str:
    """Resy restaurant booking URL."""
    return f"{RESY_BASE}/cities/{city_slug}/venues/{venue_slug}?date={date}&party_size={covers}"


def get_booking_url(restaurant_key: str, date: str, time: str, covers: int) -> dict:
    """
    Get booking URL for a known NYC restaurant.
    Returns {"platform": str, "url": str}
    """
    info = NYC_KNOWN.get(restaurant_key)
    if not info:
        return {
            "platform": "opentable",
            "url": f"{OT_BASE}/s?term={requests.utils.quote(restaurant_key)}"
        }

    if info["platform"] == "resy":
        return {
            "platform": "resy",
            "url": get_resy_url(info["slug"], info.get("city_slug", "new-york"), date, covers),
        }
    elif info["platform"] == "opentable":
        ot_id = info.get("id", "")
        url = (f"{OT_BASE}/restref/booking/start?restref={ot_id}"
               f"&covers={covers}&dateTime={date}T{time}:00")
        return {"platform": "opentable", "url": url}

    return {"platform": "unknown", "url": ""}


# ── Known NYC restaurants ─────────────────────────────────────────────────────
NYC_KNOWN = {
    # Resy (most top-tier NYC spots)
    "adda":         {"platform": "resy",       "slug": "adda",         "city_slug": "new-york"},
    "tatiana":      {"platform": "resy",       "slug": "tatiana",      "city_slug": "new-york"},
    "don_angie":    {"platform": "resy",       "slug": "don-angie",    "city_slug": "new-york"},
    "lilia":        {"platform": "resy",       "slug": "lilia",        "city_slug": "new-york"},
    "via_carota":   {"platform": "resy",       "slug": "via-carota",   "city_slug": "new-york"},
    "carbone":      {"platform": "resy",       "slug": "carbone",      "city_slug": "new-york"},
    "joe_beef":     {"platform": "resy",       "slug": "joe-beef",     "city_slug": "new-york"},
    "smithereens":  {"platform": "resy",       "slug": "smithereens",  "city_slug": "new-york"},
    "borgo":        {"platform": "resy",       "slug": "borgo",        "city_slug": "new-york"},
    "theodora":     {"platform": "resy",       "slug": "theodora",     "city_slug": "new-york"},
    "roscioli_nyc": {"platform": "resy",       "slug": "roscioli-nyc", "city_slug": "new-york"},
    # OpenTable
    "la_dong":      {"platform": "opentable",  "id": 0, "note": "Look up OT ID"},
    "le_bernardin": {"platform": "opentable",  "id": 3735},
    "daniel":       {"platform": "opentable",  "id": 2027},
    "sushi_nakazawa":{"platform": "opentable", "id": 0, "note": "Look up OT ID"},
}
