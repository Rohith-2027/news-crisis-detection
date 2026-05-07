"""
Helpers: Indian state extraction + crisis risk scoring.
Improved version with city-to-state mapping and categorized keyword scoring.
"""

from datetime import datetime
from django.utils.timezone import make_aware, is_naive


# ✅ Indian States + Union Territories
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
    "Chhattisgarh", "Goa", "Gujarat", "Haryana",
    "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",

    # Union Territories
    "Delhi", "Jammu and Kashmir", "Ladakh", "Puducherry",
    "Chandigarh", "Andaman and Nicobar Islands",
    "Dadra and Nagar Haveli", "Daman and Diu",
    "Lakshadweep",
]


# ✅ Major Indian city → state mapping
CITY_TO_STATE = {

    # Maharashtra
    "mumbai": "Maharashtra",
    "pune": "Maharashtra",
    "nagpur": "Maharashtra",

    # Karnataka
    "bengaluru": "Karnataka",
    "bangalore": "Karnataka",
    "mysuru": "Karnataka",

    # Tamil Nadu
    "chennai": "Tamil Nadu",
    "coimbatore": "Tamil Nadu",
    "madurai": "Tamil Nadu",

    # Telangana
    "hyderabad": "Telangana",
    "warangal": "Telangana",

    # West Bengal
    "kolkata": "West Bengal",
    "howrah": "West Bengal",

    # Gujarat
    "ahmedabad": "Gujarat",
    "surat": "Gujarat",
    "vadodara": "Gujarat",

    # Rajasthan
    "jaipur": "Rajasthan",
    "udaipur": "Rajasthan",

    # Uttar Pradesh
    "lucknow": "Uttar Pradesh",
    "kanpur": "Uttar Pradesh",
    "agra": "Uttar Pradesh",
    "varanasi": "Uttar Pradesh",

    # Madhya Pradesh
    "bhopal": "Madhya Pradesh",
    "indore": "Madhya Pradesh",

    # Bihar
    "patna": "Bihar",

    # Odisha
    "bhubaneswar": "Odisha",
    "cuttack": "Odisha",

    # Kerala
    "kochi": "Kerala",
    "thiruvananthapuram": "Kerala",

    # Punjab
    "amritsar": "Punjab",
    "ludhiana": "Punjab",

    # Delhi
    "new delhi": "Delhi",
    "delhi": "Delhi",

    # Assam
    "guwahati": "Assam",

    # Jammu & Kashmir
    "srinagar": "Jammu and Kashmir",

    # Andhra Pradesh
    "visakhapatnam": "Andhra Pradesh",

    # Chhattisgarh
    "raipur": "Chhattisgarh",
}


# ✅ High-risk keywords
HIGH_KEYWORDS = [
    "war", "attack", "missile", "strike",
    "conflict", "violence", "terror",
    "bomb", "shooting", "gunfire",
    "military", "explosion", "blast",
    "hostage", "terrorist"
]


# ✅ Medium-risk keywords
MEDIUM_KEYWORDS = [
    "protest", "riot", "demonstration",
    "clash", "unrest", "crime",
    "murder", "arrest", "violence",

    # Education-related
    "school", "college", "university",
    "exam", "student", "education",
    "scholarship", "campus", "academic",

    # Health/Social
    "infection", "virus", "disease",
    "hospital", "emergency"
]


# ✅ Disaster-related keywords
DISASTER_KEYWORDS = [
    "flood", "earthquake", "cyclone",
    "disaster", "fire", "landslide",
    "storm", "tsunami", "drought",
    "rainfall", "heatwave"
]


def extract_state(*texts):
    """
    Extract Indian state from title/description/content.
    First checks direct state names,
    then checks city-to-state mapping.
    """

    blob = " ".join([t for t in texts if t]).lower()

    # ✅ Direct state matching
    for state in INDIAN_STATES:
        if state.lower() in blob:
            return state

    # ✅ City-to-state matching
    for city, state in CITY_TO_STATE.items():
        if city in blob:
            return state

    return "National"


def compute_risk(title, description):
    """
    Compute crisis risk score using categorized keywords.
    """

    blob = f"{title or ''} {description or ''}".lower()

    risk_score = 0

    # ✅ High-risk keywords
    high_hits = sum(1 for word in HIGH_KEYWORDS if word in blob)
    risk_score += high_hits * 5

    # ✅ Medium-risk keywords
    medium_hits = sum(1 for word in MEDIUM_KEYWORDS if word in blob)
    risk_score += medium_hits * 3

    # ✅ Disaster keywords
    disaster_hits = sum(1 for word in DISASTER_KEYWORDS if word in blob)
    risk_score += disaster_hits * 4

    # ✅ Risk classification
    if risk_score >= 8:
        level = "HIGH"

    elif risk_score >= 3:
        level = "MEDIUM"

    else:
        level = "LOW"

    return risk_score, level


def parse_pubdate(value):
    """
    Convert NewsData.io date string
    into timezone-aware datetime.
    """

    if not value:
        return None

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return make_aware(dt) if is_naive(dt) else dt

        except ValueError:
            continue

    return None