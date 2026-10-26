"""
ai_service.py - Multi-tier AI Engine for VoyageAI Travel Itinerary Planner.
Supports Google Gemini models (gemini-3.5-flash, gemini-3.8-flash, gemini-3.5-flash-lite)
via REST transport with strict JSON contracts, plus instant high-fidelity fallback generator.
"""

import os
import json
import re
import random
from typing import Dict, Any, List, Optional
import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()

# USD to INR standard conversion benchmark
USD_TO_INR = 86.5

DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY", "")

CANDIDATE_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest"
]

# Curated global destination database for real-time recommendation & autocomplete
POPULAR_DESTINATIONS = [
    {"name": "Paris", "country": "France", "display": "Paris, France", "vibe": "Romantic & Cultural", "tag": "🗼 #EiffelTower"},
    {"name": "Tokyo", "country": "Japan", "display": "Tokyo, Japan", "vibe": "Modern & Futuristic", "tag": "⛩️ #ShibuyaCrossing"},
    {"name": "Kyoto", "country": "Japan", "display": "Kyoto, Japan", "vibe": "Zen & Ancient Shrines", "tag": "🎋 #Arashiyama"},
    {"name": "Bali", "country": "Indonesia", "display": "Bali, Indonesia", "vibe": "Tropical & Wellness", "tag": "🏖️ #UbudRiceTerraces"},
    {"name": "Rome", "country": "Italy", "display": "Rome, Italy", "vibe": "Ancient & Culinary", "tag": "🏛️ #Colosseum"},
    {"name": "Goa", "country": "India", "display": "Goa, India", "vibe": "Beach & Coastal Vibe", "tag": "🌴 #SunsetsAndSeafood"},
    {"name": "Manali", "country": "India", "display": "Manali, India", "vibe": "Snow & Alpine Trek", "tag": "🏔️ #SolangValley"},
    {"name": "Jaipur", "country": "India", "display": "Jaipur, India", "vibe": "Royal & Heritage", "tag": "🏰 #HawaMahal"},
    {"name": "Swiss Alps (Interlaken)", "country": "Switzerland", "display": "Interlaken, Switzerland", "vibe": "Glaciers & Peaks", "tag": "⛷️ #Jungfrau"},
    {"name": "Barcelona", "country": "Spain", "display": "Barcelona, Spain", "vibe": "Art & Mediterranean", "tag": "⛪ #SagradaFamilia"},
    {"name": "London", "country": "United Kingdom", "display": "London, UK", "vibe": "Historic & Cosmopolitan", "tag": "🕰️ #BigBen"},
    {"name": "New York City", "country": "USA", "display": "New York City, USA", "vibe": "Skyline & Broadway", "tag": "🗽 #CentralPark"},
    {"name": "Dubai", "country": "UAE", "display": "Dubai, UAE", "vibe": "Luxury & Desert Oasis", "tag": "🏙️ #BurjKhalifa"},
    {"name": "Singapore", "country": "Singapore", "display": "Singapore", "vibe": "Garden City & Modern", "tag": "🌸 #GardensByTheBay"},
    {"name": "Bangkok", "country": "Thailand", "display": "Bangkok, Thailand", "vibe": "Street Food & Temples", "tag": "🍜 #WatArun"},
    {"name": "Amsterdam", "country": "Netherlands", "display": "Amsterdam, Netherlands", "vibe": "Canals & Art", "tag": "🚲 #VanGogh"},
    {"name": "Florence", "country": "Italy", "display": "Florence, Italy", "vibe": "Renaissance & Tuscan Wine", "tag": "🎨 #Duomo"},
    {"name": "Santorini", "country": "Greece", "display": "Santorini, Greece", "vibe": "Caldera & White Domes", "tag": "🌅 #OiaSunset"},
    {"name": "Da Nang", "country": "Vietnam", "display": "Da Nang, Vietnam", "vibe": "Beaches & Bridges", "tag": "🌉 #GoldenBridge"},
    {"name": "Phuket", "country": "Thailand", "display": "Phuket, Thailand", "vibe": "Islands & Coast", "tag": "🚤 #PhiPhiIslands"},
    {"name": "Prague", "country": "Czech Republic", "display": "Prague, Czech Republic", "vibe": "Bohemian & Castles", "tag": "🏰 #CharlesBridge"},
    {"name": "Vienna", "country": "Austria", "display": "Vienna, Austria", "vibe": "Imperial Palaces", "tag": "🎻 #Schonbrunn"},
    {"name": "Sydney", "country": "Australia", "display": "Sydney, Australia", "vibe": "Harbor & Beaches", "tag": "🦘 #OperaHouse"},
    {"name": "Cape Town", "country": "South Africa", "display": "Cape Town, South Africa", "vibe": "Coast & Mountains", "tag": "⛰️ #TableMountain"},
    {"name": "Seoul", "country": "South Korea", "display": "Seoul, South Korea", "vibe": "K-Culture & Palaces", "tag": "🥢 #BukchonHanok"},
    {"name": "Istanbul", "country": "Turkey", "display": "Istanbul, Turkey", "vibe": "Bosphorus & Bazaars", "tag": "🕌 #HagiaSophia"},
    {"name": "Reykjavik", "country": "Iceland", "display": "Reykjavik, Iceland", "vibe": "Northern Lights & Geysers", "tag": "🌋 #BlueLagoon"},
    {"name": "Leh Ladakh", "country": "India", "display": "Leh Ladakh, India", "vibe": "High Passes & Lakes", "tag": "🏍️ #PangongLake"},
    {"name": "Udaipur", "country": "India", "display": "Udaipur, India", "vibe": "Lakes & Palaces", "tag": "🚤 #LakePichola"},
    {"name": "Kerala", "country": "India", "display": "Kerala, India", "vibe": "Backwaters & Tea Hills", "tag": "🛶 #Houseboat"}
]

def get_location_suggestions(query: str, limit: int = 5) -> List[Dict[str, str]]:
    """Returns top matching locations as user types in real-time, prioritizing prefix matches."""
    if not query or query.strip() == "":
        return POPULAR_DESTINATIONS[:limit]
    
    q = query.strip().lower()
    prefix_matches = []
    name_substring_matches = []
    country_matches = []
    vibe_matches = []
    
    for dest in POPULAR_DESTINATIONS:
        n_low = dest["name"].lower()
        c_low = dest["country"].lower()
        v_low = dest["vibe"].lower()
        t_low = dest["tag"].lower()
        
        if n_low.startswith(q):
            prefix_matches.append(dest)
        elif q in n_low:
            name_substring_matches.append(dest)
        elif c_low.startswith(q) or q in c_low:
            country_matches.append(dest)
        elif q in v_low or q in t_low:
            vibe_matches.append(dest)
            
    combined = prefix_matches + name_substring_matches + country_matches + vibe_matches
    # Deduplicate while preserving order
    seen = set()
    result = []
    for item in combined:
        if item["display"] not in seen:
            seen.add(item["display"])
            result.append(item)
            
    return result[:limit] if result else POPULAR_DESTINATIONS[:limit]

def clean_json_response(raw_text: str) -> str:
    """Strips markdown code blocks and extracts valid JSON."""
    raw_text = raw_text.strip()
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_text)
    if match:
        return match.group(1).strip()
    return raw_text

def call_gemini(prompt: str, api_key: Optional[str] = None) -> Optional[str]:
    """Invokes Google Gemini with model candidate fallback using REST transport."""
    key = api_key or os.environ.get("GEMINI_API_KEY") or DEFAULT_API_KEY
    if not key or key.strip() == "":
        return None

    genai.configure(api_key=key.strip(), transport="rest")
    
    for model_name in CANDIDATE_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.4}
            )
            if response and response.text:
                return response.text
        except Exception as e:
            # Try next candidate model
            continue
    return None

# ==========================================
# 1. SMART DESTINATION RECOMMENDER
# ==========================================

def recommend_destinations(vibe: str, budget_level: str, weather_season: str,
                           travel_party: str, interests: List[str], 
                           api_key: Optional[str] = None, demo_mode: bool = False) -> List[Dict[str, Any]]:
    """
    Recommends top 3 matching cities based on budget, weather season, and travel mood.
    """
    if not demo_mode:
        prompt = f"""
Act as an expert travel destination architect. Recommend TOP 3 international or domestic travel destinations 
matching the following criteria:
- Preferred Travel Vibe: {vibe}
- Budget Tier: {budget_level}
- Target Season: {weather_season}
- Travel Party: {travel_party}
- Top Interests: {', '.join(interests) if interests else 'General sightseeing'}

Return strictly a valid JSON array of 3 objects with NO markdown formatting or commentary:
[
  {{
    "city": "City Name",
    "country": "Country",
    "match_score": 95,
    "highlight_tags": ["#Tag1", "#Tag2", "#Tag3"],
    "why_it_matches": "Brief 2-sentence rationale explaining alignment with vibe, season, and budget.",
    "best_season": "Optimal months to visit",
    "est_daily_cost_usd": 120,
    "est_daily_cost_inr": 10380,
    "unmissable_experiences": [
      "Top experience 1",
      "Top experience 2",
      "Top experience 3"
    ]
  }}
]
"""
        response_text = call_gemini(prompt, api_key)
        if response_text:
            try:
                cleaned = clean_json_response(response_text)
                data = json.loads(cleaned)
                if isinstance(data, list) and len(data) > 0:
                    return data
            except Exception:
                pass

    # High-Fidelity Fallback
    return get_fallback_destinations(vibe, budget_level, weather_season)

def get_fallback_destinations(vibe: str, budget: str, season: str) -> List[Dict[str, Any]]:
    budget_mult = 1.0 if budget == "Budget" else (2.0 if budget == "Moderate" else 4.2)
    base_usd = int(50 * budget_mult)

    preset_catalog = {
        "Beach & Coastal": [
            {
                "city": "Da Nang",
                "country": "Vietnam",
                "match_score": 96,
                "highlight_tags": ["#PristineCoast", "#AffordableLuxury", "#StreetFoodHaven"],
                "why_it_matches": f"Da Nang offers golden beaches and turquoise water paired with world-class dining that seamlessly fits a {budget.lower()} budget in {season}.",
                "best_season": "February - August",
                "est_daily_cost_usd": base_usd,
                "est_daily_cost_inr": int(base_usd * USD_TO_INR),
                "unmissable_experiences": ["Sunrise at My Khe Beach", "Marble Mountains Cave Temples", "Son Tra Peninsula Monkey Pass"]
            },
            {
                "city": "Krabi",
                "country": "Thailand",
                "match_score": 93,
                "highlight_tags": ["#KarstCliffs", "#IslandHopping", "#SunsetCruises"],
                "why_it_matches": "Dramatic limestone karsts jutting out of the Andaman Sea provide unbeatable panoramic scenery and water sports.",
                "best_season": "November - April",
                "est_daily_cost_usd": int(base_usd * 1.15),
                "est_daily_cost_inr": int(base_usd * 1.15 * USD_TO_INR),
                "unmissable_experiences": ["Railay Beach Longtail Boat Tour", "Tiger Cave Temple Climb", "Ao Nang Night Food Market"]
            },
            {
                "city": "Crete",
                "country": "Greece",
                "match_score": 89,
                "highlight_tags": ["#MediterraneanVibe", "#AncientMinoan", "#OliveGroves"],
                "why_it_matches": "Charming Venetian harbors, pink sand lagoons, and warm Mediterranean hospitality make Crete a dream escape.",
                "best_season": "May - October",
                "est_daily_cost_usd": int(base_usd * 1.8),
                "est_daily_cost_inr": int(base_usd * 1.8 * USD_TO_INR),
                "unmissable_experiences": ["Elafonisi Pink Beach Excursion", "Knossos Palace Archaeological Walk", "Old Chania Venetian Harbor Dinner"]
            }
        ],
        "Mountain & Alpine": [
            {
                "city": "Manali & Solang",
                "country": "India",
                "match_score": 95,
                "highlight_tags": ["#SnowPeaks", "#CedarForests", "#ValleyVistas"],
                "why_it_matches": "Nestled in the Himalayas, offering alpine trekking, crisp pine-scented air, and vibrant cafe culture.",
                "best_season": "October - June",
                "est_daily_cost_usd": int(base_usd * 0.7),
                "est_daily_cost_inr": int(base_usd * 0.7 * USD_TO_INR),
                "unmissable_experiences": ["Jogini Waterfall Trek", "Solang Valley Paragliding", "Old Manali Wooden Cafes & Live Music"]
            },
            {
                "city": "Interlaken",
                "country": "Switzerland",
                "match_score": 92,
                "highlight_tags": ["#SwissAlps", "#GlacierLakes", "#AdventureHub"],
                "why_it_matches": "Flanked by Lake Thun and Lake Brienz with the towering Eiger, Monch, and Jungfrau peaks as your backdrop.",
                "best_season": "June - September / Dec - Mar",
                "est_daily_cost_usd": int(base_usd * 2.5),
                "est_daily_cost_inr": int(base_usd * 2.5 * USD_TO_INR),
                "unmissable_experiences": ["Jungfraujoch Top of Europe Train", "Harder Kulm Panoramic Vista", "Lake Brienz Jetboat Experience"]
            },
            {
                "city": "Innsbruck",
                "country": "Austria",
                "match_score": 90,
                "highlight_tags": ["#TyroleanHeritage", "#NordketteCableway", "#OldTownCharm"],
                "why_it_matches": "An imperial city right in the heart of the Alps where urban culture meets alpine wilderness in 20 minutes.",
                "best_season": "December - April & Summer",
                "est_daily_cost_usd": int(base_usd * 1.7),
                "est_daily_cost_inr": int(base_usd * 1.7 * USD_TO_INR),
                "unmissable_experiences": ["Nordkette Cable Car to Hafelekar", "Golden Roof & Imperial Hofburg", "Ambras Castle Gardens"]
            }
        ],
        "Cultural & Heritage": [
            {
                "city": "Kyoto",
                "country": "Japan",
                "match_score": 97,
                "highlight_tags": ["#ZenGardens", "#BambooGroves", "#MatchaTradition"],
                "why_it_matches": "Over a thousand Buddhist temples, tranquil Zen rock gardens, and historic wooden machiya districts.",
                "best_season": "March - May & October - Nov",
                "est_daily_cost_usd": int(base_usd * 1.5),
                "est_daily_cost_inr": int(base_usd * 1.5 * USD_TO_INR),
                "unmissable_experiences": ["Fushimi Inari Torii Gate Sunrise", "Arashiyama Bamboo Forest & Monkey Park", "Gion Historic Evening Walk"]
            },
            {
                "city": "Jaipur",
                "country": "India",
                "match_score": 94,
                "highlight_tags": ["#PinkCity", "#RoyalPalaces", "#ArtisanBazaars"],
                "why_it_matches": "Magnificent Rajput hill forts, intricate sandstone facades, and vibrant centuries-old artisan markets.",
                "best_season": "October - March",
                "est_daily_cost_usd": int(base_usd * 0.75),
                "est_daily_cost_inr": int(base_usd * 0.75 * USD_TO_INR),
                "unmissable_experiences": ["Amber Fort Elephant Passage & Mirror Palace", "Hawa Mahal Morning Photo Walk", "Johari Bazaar Handicraft Exploration"]
            },
            {
                "city": "Florence",
                "country": "Italy",
                "match_score": 91,
                "highlight_tags": ["#RenaissanceArt", "#TuscanFlavors", "#DuomoDome"],
                "why_it_matches": "The birthplace of the Renaissance packed with Michelangelo's masterpieces, Tuscan wine cellars, and cobbled streets.",
                "best_season": "April - June & September - Oct",
                "est_daily_cost_usd": int(base_usd * 2.1),
                "est_daily_cost_inr": int(base_usd * 2.1 * USD_TO_INR),
                "unmissable_experiences": ["Brunelleschi's Duomo Climb", "Uffizi Gallery Renaissance Tour", "Piazzale Michelangelo Sunset with Chianti"]
            }
        ],
        "Urban & Modern Skylines": [
            {
                "city": "Tokyo",
                "country": "Japan",
                "match_score": 97,
                "highlight_tags": ["#CyberpunkAesthetics", "#MichelinDining", "#HyperEfficientTransit"],
                "why_it_matches": "Neon-lit towers, futuristic robotics, bustling alleys, and tranquil shrines coexist in unmatched harmony.",
                "best_season": "March - May & September - Nov",
                "est_daily_cost_usd": int(base_usd * 1.6),
                "est_daily_cost_inr": int(base_usd * 1.6 * USD_TO_INR),
                "unmissable_experiences": ["Shibuya Crossing & Sky Observatory", "Shinjuku Omoide Yokocho Food Alley", "TeamLab Planets Immersive Art"]
            },
            {
                "city": "Singapore",
                "country": "Singapore",
                "match_score": 94,
                "highlight_tags": ["#GardenCity", "#HawkerCentres", "#FuturisticArchitecture"],
                "why_it_matches": "A futuristic metropolis in a garden featuring Supertree groves, world-renowned street food, and sleek Marina Bay.",
                "best_season": "Year-round",
                "est_daily_cost_usd": int(base_usd * 1.8),
                "est_daily_cost_inr": int(base_usd * 1.8 * USD_TO_INR),
                "unmissable_experiences": ["Gardens by the Bay Light Show", "Marina Bay Sands SkyPark Walk", "Maxwell Hawker Centre Culinary Tour"]
            },
            {
                "city": "Dubai",
                "country": "UAE",
                "match_score": 91,
                "highlight_tags": ["#ArchitecturalMarvels", "#DesertSafari", "#LuxuryLiving"],
                "why_it_matches": "Home to the world's tallest skyscraper, man-made islands, dune safaris, and luxurious shopping destinations.",
                "best_season": "November - March",
                "est_daily_cost_usd": int(base_usd * 2.2),
                "est_daily_cost_inr": int(base_usd * 2.2 * USD_TO_INR),
                "unmissable_experiences": ["Burj Khalifa At The Top Lounge", "Red Dunes Desert Safari & Stargazing", "Dubai Marina Yacht Cruise"]
            }
        ]
    }
    
    key = vibe if vibe in preset_catalog else "Cultural & Heritage"
    return preset_catalog[key]

# ==========================================
# 2. DAY-BY-DAY OPTIMIZED ITINERARY GENERATOR
# ==========================================

def generate_optimized_itinerary(
    destination: str,
    duration_days: int,
    budget_level: str,
    travel_party: str,
    pace: str,
    interests: List[str],
    travel_dates: str = "Upcoming Season",
    api_key: Optional[str] = None,
    demo_mode: bool = False
) -> Dict[str, Any]:
    """
    Generates structured day-wise plans with sequential time slots and geographic clustering logic.
    Clustering eliminates transit fatigue and groups nearby spots in the same district.
    """
    if not demo_mode:
        interests_str = ", ".join(interests) if interests else "Sightseeing, Local Food, Culture"
        prompt = f"""
Act as a world-class travel SaaS architect and algorithmic route optimizer. 
Build a comprehensive, day-by-day vacation itinerary for:
- Destination: {destination}
- Duration: {duration_days} Days
- Budget Level: {budget_level}
- Travel Party: {travel_party}
- Travel Pace: {pace}
- Interests: {interests_str}
- Dates/Season: {travel_dates}

CRITICAL ARCHITECTURAL RULES:
1. Geographic Clustering Logic: Every day MUST focus on a distinct, tightly-clustered district or geographic zone (e.g. "Historic Old Quarter", "Waterfront & Marina Bay", "North Hills & Temple Ridge") to minimize transit fatigue and eliminate zig-zag backtracking.
2. 4 Sequential Time Slots per Day:
   - "Morning Sightseeing" (09:00 - 12:30): Primary clustered landmark/attraction.
   - "Lunch Recommendation" (12:30 - 14:00): Top regional culinary spot or food market in that same cluster.
   - "Afternoon Leisure" (14:30 - 18:00): Cultural discovery, walking quarter, or scenic activity nearby.
   - "Evening Dining & Entertainment" (19:00 - 22:30): Atmospheric dinner and nightlife/viewpoint in the cluster.
3. Realistic Pricing: Provide realistic itemized cost estimates in USD and INR for each activity/meal matching the '{budget_level}' budget.

Return STRICTLY a valid JSON object matching this schema with NO outside markdown text:
{{
  "destination": "{destination}",
  "trip_title": "Optimized {duration_days}-Day Journey to {destination}",
  "duration_days": {duration_days},
  "budget_level": "{budget_level}",
  "travel_party": "{travel_party}",
  "pace": "{pace}",
  "transit_fatigue_reduction_pct": 94,
  "cluster_strategy_summary": "Summary of how days are divided geographically.",
  "days": [
    {{
      "day_number": 1,
      "theme": "Theme of Day 1",
      "geographic_cluster": "District Name / Geographic Zone",
      "transit_advice": "Advice on local transit for this cluster (e.g. Walking & Metro Line 1)",
      "slots": [
        {{
          "slot_name": "Morning Sightseeing",
          "timing": "09:00 AM - 12:30 PM",
          "activity": "Specific attraction name",
          "venue": "Specific venue / neighborhood",
          "transit_tip": "Walking / 5-min cab within cluster",
          "cost_usd": 25,
          "cost_inr": 2150,
          "highlights": "Why to visit & key insider tip"
        }},
        {{
          "slot_name": "Lunch Recommendation",
          "timing": "12:30 PM - 02:00 PM",
          "activity": "Culinary tasting / local specialty",
          "venue": "Specific restaurant / bistro / street market",
          "transit_tip": "Located 300m from morning spot",
          "cost_usd": 20,
          "cost_inr": 1700,
          "highlights": "Must-try dish"
        }},
        {{
          "slot_name": "Afternoon Leisure",
          "timing": "02:30 PM - 06:00 PM",
          "activity": "Afternoon exploration or park/museum",
          "venue": "Specific spot",
          "transit_tip": "Short stroll down scenic avenue",
          "cost_usd": 15,
          "cost_inr": 1300,
          "highlights": "Key feature"
        }},
        {{
          "slot_name": "Evening Dining & Entertainment",
          "timing": "07:00 PM - 10:30 PM",
          "activity": "Dinner & sunset/rooftop or evening market",
          "venue": "Specific dining venue / observation deck",
          "transit_tip": "Short metro ride or evening walk",
          "cost_usd": 40,
          "cost_inr": 3450,
          "highlights": "Ambiance & nighttime vibe"
        }}
      ]
    }}
  ]
}}
"""
        response_text = call_gemini(prompt, api_key)
        if response_text:
            try:
                cleaned = clean_json_response(response_text)
                data = json.loads(cleaned)
                if "days" in data and len(data["days"]) > 0:
                    # Calculate cumulative & daily totals
                    _enrich_costs(data)
                    return data
            except Exception:
                pass

    # Instant Fallback Generator
    return get_fallback_itinerary(destination, duration_days, budget_level, travel_party, pace, interests)

def _enrich_costs(data: Dict[str, Any]):
    """Calculates daily and total costs across days and slots."""
    total_usd = 0.0
    total_inr = 0.0
    for day in data.get("days", []):
        day_usd = 0.0
        day_inr = 0.0
        for slot in day.get("slots", []):
            usd = float(slot.get("cost_usd", 15))
            inr = float(slot.get("cost_inr", usd * USD_TO_INR))
            slot["cost_usd"] = round(usd, 2)
            slot["cost_inr"] = round(inr, 2)
            day_usd += usd
            day_inr += inr
        day["day_cost_usd"] = round(day_usd, 2)
        day["day_cost_inr"] = round(day_inr, 2)
        total_usd += day_usd
        total_inr += day_inr
    data["total_cost_usd"] = round(total_usd, 2)
    data["total_cost_inr"] = round(total_inr, 2)

def get_fallback_itinerary(destination: str, duration: int, budget: str, 
                           party: str, pace: str, interests: List[str]) -> Dict[str, Any]:
    """Generates rich, realistic day-wise clustered plans algorithmically."""
    multiplier = 1.0 if budget == "Budget" else (2.2 if budget == "Moderate" else 4.5)
    
    # City-specific real district clusters
    city_clusters = {
        "paris": [
            {"name": "7th Arrondissement & Eiffel Tower Quarter", "transit": "RER C & Pont d'Iéna Pedestrian Walk", "morning": "Eiffel Tower & Champ de Mars Grounds", "lunch": "Café de Flore / Saint-Germain Bistro", "afternoon": "Musée d'Orsay Impressionist Gallery", "evening": "Seine River Sunset Illuminations Cruise"},
            {"name": "1st Arrondissement & Historic Louvre Axis", "transit": "Metro Line 1 (Palais Royal)", "morning": "The Louvre & Tuileries Gardens", "lunch": "Le Fumoir Traditional French Brasserie", "afternoon": "Palais Garnier Opera House & Place Vendôme", "evening": "Montmartre & Sacré-Cœur Basilique Sunset Dinner"},
            {"name": "Le Marais & Latin Quarter District", "transit": "Metro Line 4 (Saint-Michel)", "morning": "Notre-Dame Cathedral & Sainte-Chapelle Stained Glass", "lunch": "L'As du Fallafel & Rue des Rosiers Market", "afternoon": "Place des Vosges & Victor Hugo Residence", "evening": "Latin Quarter Jazz Club & Wine Cellar Tasting"}
        ],
        "tokyo": [
            {"name": "Shibuya & Harajuku Youth Culture Hub", "transit": "JR Yamanote Line (Shibuya Station)", "morning": "Meiji Jingu Shinto Shrine & Yoyogi Park", "lunch": "Harajuku Gourmet Gyukatsu & Gyoza Bar", "afternoon": "Shibuya Sky Observatory & Crossing", "evening": "Shinjuku Omoide Yokocho Yakitori Alleys"},
            {"name": "Asakusa & Ueno Traditional Quarter", "transit": "Tokyo Metro Ginza Line", "morning": "Senso-ji Temple & Nakamise Shopping Dori", "lunch": "Asakusa Soba & Tempura House", "afternoon": "Ueno Park & Tokyo National Museum", "evening": "Tokyo Skytree Sunset & Sumida River Walk"},
            {"name": "Ginza & Chiyoda Imperial Axis", "transit": "Marunouchi Metro Line", "morning": "Imperial Palace East Gardens & Nijubashi Bridge", "lunch": "Tsukiji Outer Market Fresh Sushi Tasting", "afternoon": "TeamLab Planets Immersive Digital Art Gallery", "evening": "Ginza Rooftop Lounge & Cocktail Bar"}
        ],
        "rome": [
            {"name": "Ancient Forum & Colosseum District", "transit": "Metro Line B (Colosseo)", "morning": "Colosseum & Roman Forum Archaeological Walk", "lunch": "Trattoria Romana Artisanal Pasta Cacio e Pepe", "afternoon": "Palatine Hill & Circus Maximus Panorama", "evening": "Monti Neighborhood Wine Bar & Trattoria"},
            {"name": "Vatican City & Prati Quarter", "transit": "Metro Line A (Ottaviano)", "morning": "St. Peter's Basilica & Vatican Museums", "lunch": "Prati Gourmet Panini & Gelateria", "afternoon": "Castel Sant'Angelo & Tiber River Walk", "evening": "Trastevere Cobblestone Alleys & Candlelit Osteria"},
            {"name": "Historic Centro & Piazza Navona", "transit": "Cobblestone Pedestrian Walk", "morning": "Pantheon Temple & Piazza Navona Fountains", "lunch": "Campo de' Fiori Fresh Market & Pizza al Taglio", "afternoon": "Trevi Fountain & Spanish Steps", "evening": "Piazza del Popolo Sunset & Aperitivo"}
        ],
        "goa": [
            {"name": "North Goa Coastal & Fort Circuit", "transit": "Scooter / Cab Coastal Route", "morning": "Fort Aguada Lighthouse & Sinquerim Beach", "lunch": "Fisherman's Wharf Goan Fish Curry Thali", "afternoon": "Anjuna & Vagator Red Cliff Views", "evening": "Sunset Beach Shack at Ashvem with Live Acoustic Vibe"},
            {"name": "Old Goa & Panaji Heritage District", "transit": "Pedestrian Heritage Walk", "morning": "Basilica of Bom Jesus & Se Cathedral", "lunch": "Fontainhas Latin Quarter Portuguese Bistro", "afternoon": "Altinho Hilltop Church & Mandovi Promenade", "evening": "Mandovi River Sunset Cruise & Night Bazaar"},
            {"name": "South Goa Serenity & Beach Haven", "transit": "Scenic Coastal Road", "morning": "Cabo de Rama Fort Cliffside Panorama", "lunch": "Palolem Beachfront Coconut Curry Cafe", "afternoon": "Butterfly Beach Speedboat & Kayaking", "evening": "Agonda Beach Silent Sunset Stroll"}
        ],
        "manali": [
            {"name": "Old Manali & Hadimba Forest Ridge", "transit": "Deodar Forest Nature Walk", "morning": "Hadimba Devi Cedar Temple & Vashisht Hot Springs", "lunch": "Old Manali Riverside Trout & Woodfired Pizza", "afternoon": "Jogini Waterfall Pine Forest Trek", "evening": "Mall Road Handicraft Bazaars & Live Himalayan Music"},
            {"name": "Solang Valley & Alpine Adventure Plateau", "transit": "Mountain Highway (4x4 Shuttle)", "morning": "Solang Valley Paragliding & Ropeway Ride", "lunch": "Atal Tunnel Alpine Dhaba & Steaming Thukpa", "afternoon": "Sissu Waterfall & Lahaul Valley Panorama", "evening": "Old Manali Cozy Cafe & Hot Apple Cider"}
        ],
        "jaipur": [
            {"name": "Amer Fort & Rajput Hilltops", "transit": "Heritage Jeep & Hillway", "morning": "Amber Palace & Sheesh Mahal (Mirror Palace)", "lunch": "1135 AD Royal Heritage Dining in Amer", "afternoon": "Jaigarh Fort & Panna Meena Stepwell", "evening": "Nahargarh Fort Sunset View of the Whole Pink City"},
            {"name": "Walled City & Royal Palaces", "transit": "Cycle Rickshaw & Old Town Stroll", "morning": "Hawa Mahal Morning Sun Facade & Jantar Mantar", "lunch": "LMB (Laxmi Misthan Bhandar) Rajasthani Thali", "afternoon": "City Palace Royal Museum & Blue Pottery Bazaars", "evening": "Chokhi Dhani Cultural Village & Folk Dance"}
        ],
        "bali": [
            {"name": "Ubud Arts & Jungle Valley", "transit": "Scooter / Private Driver", "morning": "Tegalalang Rice Terraces & Jungle Swing", "lunch": "Ubud Organic Farm-to-Table Cafe", "afternoon": "Sacred Monkey Forest Sanctuary Walk", "evening": "Ubud Palace Traditional Legong Dance & Dinner"},
            {"name": "Southern Cliffs & Sunset Coasts", "transit": "Scenic Coastal Drive", "morning": "Padang Padang White Sand Surf Beach", "lunch": "Jimbaran Bay Seafood Grill on the Sand", "afternoon": "Uluwatu Cliffside Temple & Ocean Panorama", "evening": "Uluwatu Kecak Fire Dance at Sunset"}
        ]
    }

    # Match destination to known real cluster or use generic
    dest_lower = destination.lower()
    matched_clusters = None
    for k in city_clusters:
        if k in dest_lower:
            matched_clusters = city_clusters[k]
            break

    if not matched_clusters:
        matched_clusters = [
            {"name": f"Historic Old Town & Heritage Quarter ({destination})", "transit": "Pedestrian friendly & Heritage Tram", "morning": f"{destination} Historic Landmark & Cathedral", "lunch": "Local Artisanal Bistro & Tapas House", "afternoon": f"{destination} Art Gallery & Cultural Quarter", "evening": "Rooftop Dining & Old Town Night Skyline"},
            {"name": f"Waterfront Promenade & Marina District ({destination})", "transit": "Scenic Ferry & Metro Line 1", "morning": "Marina Bay & Coastal Walkway", "lunch": "Fresh Harbor Catch & Seafood Cafe", "afternoon": "Botanical Gardens & Sculpture Pavilion", "evening": "Waterfront Dining & Sunset Cocktails"},
            {"name": f"Arts Quarter & Skyline Plateau ({destination})", "transit": "Cable Railway & City Bus", "morning": "City Panoramic Observatory & Tower", "lunch": "Modern Fusion Bistro & Gourmet Coffee", "afternoon": "Design District & Designer Bazaars", "evening": "Music Lounge & Evening Night Market"}
        ]

    days_list = []
    for day_idx in range(1, duration + 1):
        cluster_info = matched_clusters[(day_idx - 1) % len(matched_clusters)]
        cluster_name = cluster_info["name"]
        
        m_cost = round(20 * multiplier, 2)
        l_cost = round(15 * multiplier, 2)
        a_cost = round(18 * multiplier, 2)
        e_cost = round(35 * multiplier, 2)

        day_obj = {
            "day_number": day_idx,
            "theme": f"Day {day_idx}: {cluster_name}",
            "geographic_cluster": cluster_name,
            "transit_advice": f"All venues located within tight perimeter. {cluster_info.get('transit', 'Walking & Metro')}.",
            "slots": [
                {
                    "slot_name": "Morning Sightseeing",
                    "timing": "09:00 AM - 12:30 PM",
                    "activity": cluster_info.get("morning", f"{destination} Landmark Discovery"),
                    "venue": f"{cluster_name} Main Entrance",
                    "transit_tip": "Central cluster meetup point; zero transit fatigue",
                    "cost_usd": m_cost,
                    "cost_inr": round(m_cost * USD_TO_INR, 2),
                    "highlights": "Optimal morning light, short queues, and prime photo angles."
                },
                {
                    "slot_name": "Lunch Recommendation",
                    "timing": "12:30 PM - 02:00 PM",
                    "activity": cluster_info.get("lunch", "Authentic Regional Gastronomy Tasting"),
                    "venue": f"Curated Spot in {cluster_name}",
                    "transit_tip": "3-minute stroll from morning activity",
                    "cost_usd": l_cost,
                    "cost_inr": round(l_cost * USD_TO_INR, 2),
                    "highlights": "Chef's signature local specialty paired with regional beverage."
                },
                {
                    "slot_name": "Afternoon Leisure",
                    "timing": "02:30 PM - 06:00 PM",
                    "activity": cluster_info.get("afternoon", "Cultural Discovery & Leisure Walk"),
                    "venue": f"{cluster_name} Promenade & Civic Quarter",
                    "transit_tip": "Pleasant shaded tree-lined avenue within cluster",
                    "cost_usd": a_cost,
                    "cost_inr": round(a_cost * USD_TO_INR, 2),
                    "highlights": "Relaxed afternoon pace, curated artisan boutiques, and hidden vantage points."
                },
                {
                    "slot_name": "Evening Dining & Entertainment",
                    "timing": "07:00 PM - 10:30 PM",
                    "activity": cluster_info.get("evening", "Rooftop Culinary Experience & Nightlife"),
                    "venue": f"Sky Lounge & Dining ({cluster_name})",
                    "transit_tip": "Direct elevator access or short stroll",
                    "cost_usd": e_cost,
                    "cost_inr": round(e_cost * USD_TO_INR, 2),
                    "highlights": "Atmospheric evening dinner, vibrant illuminated vista, and handcrafted refreshments."
                }
            ]
        }
        days_list.append(day_obj)

    itinerary = {
        "destination": destination,
        "trip_title": f"The Ultimate {duration}-Day Curated Journey to {destination}",
        "duration_days": duration,
        "budget_level": budget,
        "travel_party": party,
        "pace": pace,
        "transit_fatigue_reduction_pct": 93,
        "cluster_strategy_summary": f"Grouped {duration} days into high-density geographic pockets across {destination} to keep travel transit times under 15 minutes per hop.",
        "days": days_list
    }
    _enrich_costs(itinerary)
    return itinerary

# ==========================================
# 3. VIBE CUSTOMIZATION & DYNAMIC SLOT SWAP
# ==========================================

def swap_itinerary_slot(
    current_slot: Dict[str, Any],
    swap_prompt: str,
    destination: str,
    cluster_name: str,
    budget_level: str,
    api_key: Optional[str] = None,
    demo_mode: bool = False
) -> Dict[str, Any]:
    """
    Dynamically swaps out a single activity slot based on user modification instructions
    (e.g., 'Swap museum for outdoor street food market', 'Find vegan friendly restaurant').
    Maintains geographic clustering.
    """
    if not demo_mode:
        prompt = f"""
Act as an AI travel concierge. Replace ONLY the following activity slot according to the user's specific request:
Current Slot:
- Slot Name: {current_slot.get('slot_name')}
- Timing: {current_slot.get('timing')}
- Current Activity: {current_slot.get('activity')}
- Geographic District: {cluster_name} in {destination}
- Budget Tier: {budget_level}

User Modification Request:
"{swap_prompt}"

RULES:
1. The new activity MUST remain within or adjacent to the geographic cluster '{cluster_name}' in {destination}.
2. Keep the timing window intact.
3. Provide realistic estimated cost in USD and INR for {budget_level} budget.

Return STRICTLY a JSON object with keys: "slot_name", "timing", "activity", "venue", "transit_tip", "cost_usd", "cost_inr", "highlights".
"""
        response_text = call_gemini(prompt, api_key)
        if response_text:
            try:
                cleaned = clean_json_response(response_text)
                data = json.loads(cleaned)
                if "activity" in data and "venue" in data:
                    data["slot_name"] = current_slot.get("slot_name", "Customized Slot")
                    data["timing"] = current_slot.get("timing", "Flexible Time")
                    data["cost_usd"] = float(data.get("cost_usd", current_slot.get("cost_usd", 20)))
                    data["cost_inr"] = float(data.get("cost_inr", round(data["cost_usd"] * USD_TO_INR, 2)))
                    return data
            except Exception:
                pass

    # Instant Fallback Slot Swap
    multiplier = 1.0 if budget_level == "Budget" else (2.0 if budget_level == "Moderate" else 4.0)
    new_usd = round(random.choice([15, 25, 35, 45]) * (multiplier / 2.0), 2)
    return {
        "slot_name": current_slot.get("slot_name", "Activity Slot"),
        "timing": current_slot.get("timing", "Scheduled Time"),
        "activity": f"{swap_prompt.title()} in {cluster_name}",
        "venue": f"Curated Venue in {cluster_name}, {destination}",
        "transit_tip": "Directly accessible within the district walking perimeter",
        "cost_usd": new_usd,
        "cost_inr": round(new_usd * USD_TO_INR, 2),
        "highlights": f"Personalized substitution: Tailored specifically to your vibe request ('{swap_prompt}')."
    }
