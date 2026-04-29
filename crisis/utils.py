"""
Helpers: Indian state extraction + crisis risk scoring.
Kept simple and readable for an academic viva.
"""
from datetime import datetime
from django.utils.timezone import make_aware, is_naive

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    # Union Territories commonly mentioned in news
    "Delhi", "Jammu and Kashmir", "Ladakh", "Puducherry", "Chandigarh",
    "Andaman and Nicobar Islands", "Dadra and Nagar Haveli", "Daman and Diu",
    "Lakshadweep",
]

CRISIS_KEYWORDS = [
    "war", "flood", "earthquake", "riot", "explosion",
    "attack", "cyclone", "disaster",
]


def extract_state(*texts):
    """Return the first Indian state mentioned in any of the texts, else 'National'."""
    blob = " ".join([t for t in texts if t]).lower()
    for state in INDIAN_STATES:
        if state.lower() in blob:
            return state
    return "National"


def compute_risk(title, description):
    """Count crisis-keyword hits in title + description and bucket the score."""
    blob = f"{title or ''} {description or ''}".lower()
    score = sum(blob.count(k) for k in CRISIS_KEYWORDS)
    if score == 0:
        level = "LOW"
    elif score <= 2:
        level = "MEDIUM"
    else:
        level = "HIGH"
    return score, level


def parse_pubdate(value):
    """NewsData.io returns 'YYYY-MM-DD HH:MM:SS' (UTC). Make it timezone-aware."""
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(value, fmt)
            return make_aware(dt) if is_naive(dt) else dt
        except ValueError:
            continue
    return None
