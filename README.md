# openclaw-reservation

> OpenClaw skill — finds and books restaurants worldwide.

**Israel:** Direct API integration (Ontopo + Tabit)  
**Europe & NYC:** Browser handoff (TheFork, OpenTable, Resy)  
**Recommendations:** Michelin Guide (Algolia), Time Out, Google Maps

## Features
- Search by city, date, party size
- Michelin Bib Gourmand / Selected filter (no stars)
- Curated lists for TLV, Marseille, Genova, Messina, Valletta, NYC, Barcelona, London
- Auto-detect booking platform per restaurant
- CC handled via browser handoff — no card data stored

## Setup
```bash
pip install requests
export RESERVATION_EMAIL="your@email.com"
export RESERVATION_PHONE="+972500000000"
export GOOGLE_MAPS_API_KEY="your-key"  # optional, for live ratings
```

## Usage
```python
from unified import search_and_format
results = search_and_format("tel_aviv", date="2026-04-01", time="20:00", party_size=2)
print(results)
```

## Supported Cities
Israel (TLV via Ontopo/Tabit), Marseille, Genova, Messina, Valletta, NYC, Barcelona, London, Lisbon, Prague

## License
MIT
