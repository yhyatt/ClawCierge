# Restaurant Reservation Skill 🍽️

**Built:** March 2026  
**Status:** Production-ready (Israel API ✅, Europe/USA browser-handoff ✅, Recommendations ✅)

---

## Architecture

```
unified.py          ← single entry point (search_and_format / initiate_booking)
  ├── ontopo.py     ← Israel (direct API, anonymous JWT) ✅
  ├── tabit.py      ← Israel (direct API, OTP required for booking) ✅
  ├── thefork.py    ← Europe (browser handoff — DataDome protected) 🔗
  ├── opentable.py  ← USA / NYC (browser handoff — 403 without session) 🔗
  ├── recommender.py← Michelin Algolia + Time Out + Condé Nast 🌟
  └── maps.py       ← Curated lists + Google Maps (primary for Israel) 🗺️
```

---

## Recommendation Philosophy

Per Yonatan's explicit preference (non-negotiable):

| Source | Rule |
|--------|------|
| Michelin | ✅ **Bib Gourmand** — great food, great value, no fuss |
| Michelin | ✅ **Selected / Plate** — recommended, good cooking |
| Michelin | ❌ **1/2/3 Stars** — too fancy, not the vibe, never surfaced |
| Time Out | ✅ "Best of" lists per city |
| Condé Nast | ✅ Gallery pages when available |
| Google Maps | ✅ Primary for Israel (not in Michelin index); curated + saved places |
| אופטיקאי מדופלם | ❌ Strategy blog (like Stratechery) — no restaurant content |

---

## Platform Details

### 🇮🇱 Ontopo (Israel — primary)
- **Auth:** `POST /api/loginAnonymously` → `jwt_token` (anonymous, no credentials)
- **Header:** `token: <jwt>` — NOT `Authorization: Bearer`
- **Date format:** `YYYYMMDD` — wrong format returns sparse response with no slots
- **Time format:** `HHMM` — wrong format returns no slots
- **Size format:** string not int — `"2"` not `2`
- **Search:** `GET /api/venue_search?slug=15171493&version=7859&terms=NAME&locale=he`
  - Returns `{slug, title, address, logo}` — slug here is the INTERNAL slug, not the postSlug!
- **Two slug types (critical distinction):**
  - **Internal slug** — returned by `venue_search`, used in `slug_content`
  - **postSlug** — the numeric ID used in page URLs AND in `availability_search`
  - They are DIFFERENT numbers. Always use postSlug for availability/booking.
- **PostSlug discovery (preferred):** DuckDuckGo `site:ontopo.com <name> page` → fetch page → regex `"postSlug":"(\d+)"`
- **PostSlug discovery (fallback):** browse `https://ontopo.com/he/il/page/<url-slug>` → same regex
- **Availability (Step 1):** `POST /api/availability_search` with `{slug: postSlug, locale, criteria: {size, date, time}}` → returns `{areas: [...], availability_id}`
  - Each area has slots with `method: seat|standby|phone|disabled`
  - `seat` = confirmed ✅, `standby` = waitlist ⚠️, `phone` = call only 📞, `disabled` = unavailable ❌
- **Booking (Step 2):** `POST /api/availability_search` AGAIN with same body + `availability_id` field → returns `{checkout_id}`
  - ⚠️ NOT `/api/availability_search_marketplace` — that endpoint always returns "Invalid search input" for direct venue bookings
- **Checkout URL:** `https://www.ontopo.co.il/en/checkout/<checkout_id>` — user fills name/phone/email/CC on this page
  - ⚠️ NOT `s1.ontopo.com` — wrong domain
- **Read-only — no hold created:** `availability_search` does NOT create a table hold (unlike Tabit). Safe to search without cancel.
- **Known postSlugs:** Taizu `36960535`, Bar 51 `31338736`, Mashya `45994738` (phone-only)
- **Venues without postSlug:** some venues exist in `venue_search` (internal slug only) with no public page URL — these cannot be booked via API (e.g. האחים internal slug `85801906`)

### 🇮🇱 Tabit (Israel — secondary)
- **Auth header:** `TG-Authorization: E3AE3D44-6FE4-4264-AD3A-54D44119F802` + `Origin: https://tabitisrael.co.il`
- **API base:** `https://tgm-api.tabit.cloud`
- **Bridge base:** `https://bridge.tabit.cloud`
- **Config (public):** `GET tgm-api.tabit.cloud/rsv/booking/configuration?organization=<orgId>` — works without user auth, returns future_reservation settings
- **Availability:** `POST tgm-api.tabit.cloud/rsv/booking/temp-reservations` — creates REAL 15-min table hold ⚠️ Must call `delete_temp_reservation()` if user doesn't proceed
- **DST:** Israel is UTC+2 winter / UTC+3 summer — MUST convert local time to UTC before sending
- **Booking (full flow):** requires user OTP auth:
  1. OTP via bridge loyalty: `POST bridge.tabit.cloud/loyalty/login/mobile {mobile, customMessageSuffix}` with loyalty headers (needs `siteId` = org ID)
  2. Verify: `POST bridge.tabit.cloud/loyalty/login/mobile/pincode {mobile, pinCode}`
  3. Returns user JWT → pass as `Authorization: Bearer <token>` for booking
- **Search (BROKEN):** `GET bridge.tabit.cloud/organizations/search?searchTerm=NAME` ignores the search term — always returns the same ~15 popularity-sorted TLV restaurants (near נחלת בנימין/רוטשילד). Useless for name lookup.
- **Org ID discovery options (by priority):**
  1. **Known KNOWN_ORGS dict** in `tabit.py` — add orgs as you discover them
  2. **Tabit URL slug → org ID:** The Angular app resolves via `GET ros-tad.tabit.cloud/online-shopper/organizations?publicUrlLabel=<slug>&includeUnlisted=1` — BUT requires full user JWT auth (chicken-and-egg problem)
  3. **Browser tool:** navigate to `tabitisrael.co.il/<slug>` → intercept network calls → capture org ID from XHR to `/rsv/booking/configuration?organization=<id>`
  4. **Direct Tabit website search:** `https://tabitisrael.co.il` → search for restaurant name → note URL becomes `/online-reservations/<orgId>`
- **`call_restaurant_error` response:** means no availability OR the restaurant is closed/doesn't take online bookings for that slot — not an API error
- **Known orgs:** `molam=67dc03b26adf5bfd252aff30` (add more via browser discovery as needed)

### 🇪🇺 TheFork (Europe)
- **Protection:** DataDome blocks all direct API calls
- **Strategy:** Browser co-pilot only — construct pre-filled URL and hand off
- **Coverage:** Marseille ✅, Genoa ✅, Messina ✅, Rome ✅, Barcelona ✅, Paris ✅
- **Valletta (Malta):** Limited TheFork coverage — use Mozrest (Michelin picks show `booking_provider: Mozrest`)

### 🇺🇸 OpenTable / Resy (USA)
- **OpenTable:** GraphQL returns 403 without session. Pre-filled URL handoff only.
- **Resy:** Primary for top-tier NYC (Don Angie, Lilia, Via Carota, Carbone, etc.)
- **Resy release:** Most popular spots release 28 days ahead at midnight ET
- **Known NYC mapping:** see `opentable.py::NYC_KNOWN`

### 🌟 Michelin (Algolia API — cracked March 2026)
- **App ID:** `8NVHRD7ONV`
- **Search Key:** `3222e669cf890dc73fa5f38241117ba5` (public read-only)
- **Index:** `prod-restaurants-en`
- **Award values:** `BIB_GOURMAND` | `selected` | `ONE_STAR` | `TWO_STARS` | `THREE_STARS`
- **Israel:** NOT in index as of 2026. Use Google Maps + Time Out.
- **Filter example:** `city_slug:messina AND (michelin_award:BIB_GOURMAND OR michelin_award:selected)`

### ⏰ Time Out (scraping)
- Works with standard requests (no bot protection)
- Extracts numbered restaurant list from `<h3>` tags
- Coverage: NYC, Marseille, Paris, London, Rome, Barcelona, Milan

---

## Booking Policies

1. **NEVER AUTO-BOOK** — always present options, wait for explicit user choice
2. **CC Handling:** browser handoff (user enters card manually). No raw CC data in skill.
3. **OTP Handling:** prompt user for code after sending, wait for reply
4. **Tabit temp hold:** call `delete_temp_reservation()` if user does NOT proceed
5. **Default credentials:** Set via env vars RESERVATION_EMAIL + RESERVATION_PHONE, or pass to search()/book() directly

---

## Curated Lists (maps.py)

Pre-populated for:
- **Messina** (Apr 7, 2026 — cruise) — 4 picks
- **Marseille** (Apr 4, 2026 — cruise) — 5 picks
- **Genoa** (Apr 5, 2026 — cruise) — 4 picks
- **Valletta** (Apr 8, 2026 — cruise) — 4 picks
- **New York** (Jun 2026) — 7 picks
- **Tel Aviv** (home) — 3 picks (extend via Maps saved places)

---

## Quick Start

```python
import sys; sys.path.insert(0, "/home/openclaw/.openclaw/workspace/skills/reservation")
from unified import search_and_format

# Messina lunch, April 7, 4 people
print(search_and_format(city="messina", date="20260407", time="1300", size=4))

# TLV dinner search
print(search_and_format(city="tel aviv", date="20260315", time="2000", size=2, query="taizu"))
```

---

## Testing

```bash
cd /home/openclaw/.openclaw/workspace/skills/reservation
python3 test_messina.py    # Messina cruise day test (live, green ✅)
```

---

## Known Issues / Limits

| Issue | Status | Workaround |
|-------|--------|-----------|
| Tabit `call_restaurant_error` for some restaurants on some days | Investigated — restaurant may have no availability OR be closed | Try different date/time |
| TheFork booking URL for curated picks uses city search, not specific restaurant | Known — restaurant TF slugs need manual mapping | User lands on search, finds restaurant |
| Ontopo checkout flow not fully tested end-to-end | OTP may be required at checkout page | Browser handoff via `s1.ontopo.com/checkout/<id>` |
| Condé Nast Traveler scraping limited (needs GraphQL token) | Working for some URLs | Falls back silently to [] |
| Israel not in Michelin index | Structural limitation | Use Maps curated + Time Out Israel |

---

## Open Questions (for Yonatan to resolve)

See `decisions.md` for full list. Key open items:

1. **Tabit phone number** — DEFAULT_USER.phone is empty. Need to populate from secure store before OTP flows work.
2. **Google Maps API key** — for live `search_restaurants_maps()`. Currently falls back to URL-only mode.
3. **Resy timing for NYC** — Don Angie / Lilia release 28 days out. Should Kai check + alert on release date?
4. **TheFork partner API** — should we apply? Unlocks real-time availability for all of Europe.
5. **Valletta Mozrest** — Mozrest widget works but isn't integrated as a platform yet. Manual link only.
