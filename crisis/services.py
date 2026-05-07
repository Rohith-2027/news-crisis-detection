"""
NewsData.io fetch + persistence service.
Called by both the management command and the /fetch-news view.
"""

import requests
from django.conf import settings

from .models import News
from .utils import extract_state, compute_risk, parse_pubdate


def fetch_and_store(country="in", query=None, state=None, fetch_all=True):
    """
    Fetch latest news from NewsData.io for the given country and save new items.
    
    Args:
        country: Country code (default: 'in' for India)
        query: Specific search query (optional)
        state: Specific state (optional)
        fetch_all: If True, fetch broad trending news; if False, only use query/state
    
    Returns (created_count, skipped_count, error_message_or_None).
    """

    if not settings.NEWSDATA_API_KEY:
        return 0, 0, "NEWSDATA_API_KEY is not set. Export it before fetching."

    params = {
        "apikey": settings.NEWSDATA_API_KEY,
        "country": country,
        "language": "en",
    }
    
    # Priority: specific state > specific query > fetch all trending news
    if state and state not in ("", "All", "National"):
        # State-specific: focus on election and politics for the state
        search_query = f"{state} election politics campaign"
        params["q"] = search_query
    elif query:
        # Use provided query if state-specific not set
        params["q"] = query
    elif fetch_all:
        # Fetch all trending news: crisis, disaster, election, politics
        search_query = "crisis disaster election politics flood earthquake protest violence"
        params["q"] = search_query

    try:
        resp = requests.get(settings.NEWSDATA_URL, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

    except requests.RequestException as e:
        return 0, 0, f"Request failed: {e}"

    results = data.get("results", []) or []

    created = 0
    skipped = 0

    for item in results:

        title = (item.get("title") or "").strip()

        if not title:
            skipped += 1
            continue

        # Skip duplicate titles
        if News.objects.filter(title=title).exists():
            skipped += 1
            continue

        description = item.get("description") or ""
        content = item.get("content") or ""

        keywords = item.get("keywords") or []

        if isinstance(keywords, list):
            keywords_text = " ".join(keywords)
        else:
            keywords_text = str(keywords)

        # State extraction
        state = extract_state(title, description, keywords_text)

        # Risk calculation
        risk_score, level = compute_risk(title, description)

        # Parse publication date
        published_at = parse_pubdate(item.get("pubDate"))

        # Save article
        News.objects.create(
            title=title,
            description=description,
            source=item.get("source_id", ""),
            published_at=published_at,
            content=content,
            url=item.get("link") or item.get("url") or "",
            country="India",
            state=state,
            risk_score=risk_score,
            alert_level=level,
        )

        created += 1

    return created, skipped, None