<div align="center">
<img src="assets/banner.jpg" alt="ClawCierge — Restaurant Search & Booking" width="100%">

# ClawCierge 🦞🍽️

**Finds and books restaurants worldwide.**  
Israel via direct API · Europe & NYC via browser handoff · Michelin + Time Out recommendations baked in · Personal Google Maps saves always surfaced first.

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://github.com/yhyatt/clawcierge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://github.com/yhyatt/clawcierge)

</div>

---

## Platform Coverage

| Region | Platform | Method |
|--------|----------|--------|
| 🇮🇱 Israel | Ontopo + Tabit | Direct API |
| 🇷🇴 Romania / Bucharest | Bookingham | Browser handoff (primary) |
| 🇷🇴 Romania / Bucharest | OpenTable | Browser handoff (fallback, thin) |
| 🇫🇷🇮🇹🇪🇸 Europe | TheFork | Browser handoff |
| 🇺🇸 NYC | OpenTable + Resy | Browser handoff |
| 🌍 Worldwide | Michelin Guide | Direct API (Algolia) |

> **TheFork note:** TheFork does **not** support Romania — any Bucharest query silently redirects to Paris (verified 2026-03-21). Use Bookingham for Romania.

---

## Features

- **Declarative city registry** — adding a new city is a data change only (`city_registry.py`). No code changes needed for common platforms.
- **Personal saves first** — automatically checks your Google Maps "Want to Go" list (`wanttogo_by_city.json`) before any community/editorial source. Your saves are always `kai_pick ⭐`.
- **Multi-platform routing** — detects the right booking system per city automatically
- **Michelin filter** — Bib Gourmand + Selected only; stars excluded by default (see Michelin note below)
- **Curated lists** — TLV, NYC, Barcelona, Bucharest, Marseille, Genova, Messina, Valletta and more
- **No CC stored** — payment always via browser handoff, never raw card data in code
- **Israel-first** — Ontopo covers ~1,000 IL restaurants; Tabit covers the rest

---

## Supported Cities

| City | Country | Platforms | Michelin | Notes |
|------|---------|-----------|----------|-------|
| Tel Aviv | 🇮🇱 IL | Ontopo, Tabit | ❌ Not indexed | Maps curated list + Time Out IL |
| New York | 🇺🇸 US | Resy, OpenTable | ✅ | Full Michelin + curated 64-place list |
| Barcelona | 🇪🇸 ES | TheFork | ✅ | Michelin + Bib Gourmand |
| Bucharest | 🇷🇴 RO | Bookingham, OpenTable | ❌ Not indexed | Community curated + your Maps saves |
| Marseille | 🇫🇷 FR | TheFork | ✅ | Curated list |
| Genova | 🇮🇹 IT | TheFork | ✅ | Curated list |
| Messina | 🇮🇹 IT | TheFork | ✅ | Curated list |
| Valletta | 🇲🇹 MT | Mozrest | ❌ | TheFork thin; Mozrest primary |

---

## Bucharest

Bucharest has dedicated support with a locally-curated restaurant list:

**Booking:** [Bookingham.ro](https://bookingham.ro) (dominant local reservation platform) → OpenTable fallback

**Curated picks** (community-researched + personal Maps saves ⭐):
- NOUA — best restaurant in Bucharest, modern Romanian, tasting menu (~€75)
- Kaiamo ⭐, Vacamuuu ⭐, Osho ⭐, Nor Sky ⭐, Kupaj Gourmet ⭐ — personal saves
- Kane, deSoi, Ierbar, La Hambar, Lacrimi și Sfinți, Caru' cu Bere, Hanu' lui Manuc
- Le Bistrot Français — signed by 2-Michelin-star chef Tom Meyer
- Eggcetera ⭐ — breakfast (4.8 rating)

**Michelin:** Romania is not in the Michelin Guide. No stars, no Bib Gourmand.

---

## Personal Maps Integration

ClawCierge automatically surfaces places from your Google Maps "Want to Go" list before any editorial source:

```
memory/places/wanttogo_by_city.json   ← indexed by city (17 cities, 465 restaurants)
memory/places/bucharest.json          ← city-specific parsed saves
memory/places/athens.json
memory/places/barcelona.json
```

Personal saves are marked `kai_pick: True` and appear first in all curated lists. Community/Reddit research supplements — it never replaces.

Run `python3 personal-data/parsers/parse_wanttogo.py` to refresh the index from a new `wanttogo.txt` export.

---

## Setup

```bash
pip install requests
export RESERVATION_EMAIL="your@email.com"
export RESERVATION_PHONE="+1234567890"
export GOOGLE_MAPS_API_KEY="your-key"  # optional
```

## Quick Start

```python
from unified import search_and_format

# Tel Aviv
results = search_and_format("tel_aviv", date="2026-04-01", time="20:00", party_size=2)

# Bucharest
results = search_and_format("bucharest", date="2026-03-27", time="19:30", party_size=2)
print(results)
```

---

## Architecture

```
search_and_format()
    ├── city_registry.py  — declarative per-city config (platforms, Michelin, timezone, aliases)
    ├── maps.py           — curated lists (personal Maps saves first, community research second)
    │   └── wanttogo_by_city.json ← auto-loaded, highest signal source
    ├── recommender.py    — Michelin Algolia + Time Out (indexed countries only)
    ├── ontopo.py         — Israel direct API (Ontopo)
    ├── tabit.py          — Israel direct API (Tabit)
    ├── bookingham.py     — Romania browser handoff (Bookingham.ro)
    ├── thefork.py        — Europe browser handoff (NOT for Romania — redirects to Paris)
    └── opentable.py      — NYC + worldwide browser handoff
```

---

## Important Notes

- **Tabit `check_availability()` creates a real ~15 min hold** — always call `delete_temp_reservation()` on cancel
- **Ontopo `availability_search` is read-only** — safe to call freely
- **Michelin doesn't cover Israel or Romania** — fallback to curated Maps lists + Time Out
- **TheFork doesn't support Romania** — Bucharest queries redirect to Paris; use Bookingham
- **OpenTable worldwide** — US cities use `metroId`; international cities use term-based search

---

## OpenTable Metro IDs (US)

| City | metroId |
|------|---------|
| New York | 4 |
| Chicago | 2 |
| Los Angeles | 3 |
| San Francisco | 5 |
| Boston | 6 |
| Washington DC | 7 |
| Miami | 8 |

International cities (including Bucharest) use term-based search: `?term=restaurant+{city}`.

---

## License

MIT © [Yonatan Hyatt](https://github.com/yhyatt)
