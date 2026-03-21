"""
Bookingham.ro — Romanian Restaurant Booking 🇷🇴
================================================
Primary local reservation platform for Romania.
No public API — browser co-pilot handoff (same pattern as TheFork).

Coverage: Bucharest, Cluj-Napoca, Timișoara, Iași, Constanța, Brașov, Sibiu, Oradea, Brașov.

URL structure (verified 2026-03-21):
  - City pages: https://bookingham.ro/{city_slug}  (e.g., /bucuresti, /cluj-napoca)
  - Search filter: ?search={query}
  - Date/time/party-size: set via the on-page widget (no URL params observed)
  
The booking widget is JavaScript-driven. Best handoff: city URL + search param.
User picks date/time in the widget.

Usage:
    from skills.reservation import bookingham
    
    # City search URL
    url = bookingham.get_city_search_url("bucharest")
    # → https://bookingham.ro/bucuresti
    
    # Restaurant search URL
    url = bookingham.get_restaurant_url("NOUA", "bucharest")
    # → https://bookingham.ro/bucuresti?search=NOUA
"""
from __future__ import annotations
import urllib.parse

BASE = "https://bookingham.ro"

# City slug mapping (Romanian city names used in URLs)
CITY_SLUGS = {
    # Bucharest
    "bucharest": "bucuresti",
    "bucuresti": "bucuresti",
    "buc": "bucuresti",
    
    # Other major Romanian cities
    "cluj": "cluj-napoca",
    "cluj-napoca": "cluj-napoca",
    "timisoara": "timisoara",
    "iasi": "iasi",
    "constanta": "constanta",
    "brasov": "brasov",
    "sibiu": "sibiu",
    "oradea": "oradea",
    "craiova": "craiova",
    "piatra-neamt": "piatra-neamt",
}


def get_city_search_url(
    city: str,
    covers: int = 2,
    date: str = "",
    time: str = "",
) -> str:
    """
    Build Bookingham city search URL for browser handoff.
    
    Args:
        city: City name or slug (case-insensitive)
        covers: Party size (informational — widget handles this)
        date: Date in YYYY-MM-DD or YYYYMMDD (informational — widget handles this)
        time: Time in HH:MM or HHMM (informational — widget handles this)
    
    Returns:
        URL to the city's restaurant listing page.
        
    Note: Bookingham's date/time/party selection is via on-page JavaScript widget.
    The covers/date/time params are accepted for API consistency but not appended to URL.
    """
    slug = CITY_SLUGS.get(city.lower().strip(), "bucuresti")
    return f"{BASE}/{slug}"


def get_restaurant_url(restaurant_name: str, city: str = "bucharest") -> str:
    """
    Build Bookingham search URL for a specific restaurant name.
    
    Args:
        restaurant_name: Name of the restaurant to search for
        city: City name or slug (default: bucharest)
    
    Returns:
        URL with search query pre-filled.
        
    Example:
        get_restaurant_url("NOUA", "bucharest")
        → https://bookingham.ro/bucuresti?search=NOUA
    """
    slug = CITY_SLUGS.get(city.lower().strip(), "bucuresti")
    q = urllib.parse.quote(restaurant_name)
    return f"{BASE}/{slug}?search={q}"


def get_direct_restaurant_url(restaurant_slug: str) -> str:
    """
    Build a direct URL to a restaurant's booking page (if slug is known).
    
    Args:
        restaurant_slug: The restaurant's URL slug on Bookingham
        
    Returns:
        Direct URL to the restaurant's booking page.
        
    Example:
        get_direct_restaurant_url("bucuresti/restaurante/noua")
        → https://bookingham.ro/bucuresti/restaurante/noua
        
    Note: Restaurant slugs must be discovered via search or prior knowledge.
    """
    return f"{BASE}/{restaurant_slug.lstrip('/')}"


# ══════════════════════════════════════════════════════════════════════════════
# Convenience: Check if a city is supported
# ══════════════════════════════════════════════════════════════════════════════

def is_city_supported(city: str) -> bool:
    """Check if a city has Bookingham coverage."""
    return city.lower().strip() in CITY_SLUGS


def list_supported_cities() -> list[str]:
    """Return list of unique city slugs with Bookingham coverage."""
    # Return deduplicated canonical slugs
    seen = set()
    result = []
    for slug in CITY_SLUGS.values():
        if slug not in seen:
            seen.add(slug)
            result.append(slug)
    return result
