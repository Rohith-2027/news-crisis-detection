"""
NewsData.io fetch + persistence service.
Called by both the management command and the /fetch-news view.
"""
import requests
from django.conf import settings
from .models import News
from .utils import extract_state, compute_risk, parse_pubdate


def fetch_and_store(country="in"):
    """
    Fetch latest news from NewsData.io for the given country and save new items.
    Returns (created_count, skipped_count, error_message_or_None).
    """
    if not settings.NEWSDATA_API_KEY:
        return 0, 0, "NEWSDATA_API_KEY is not set. Export it before fetching."

    params = {
        "apikey": settings.NEWSDATA_API_KEY,
        "country": country,
        "language": "en",
    }
    try:
        resp = requests.get(settings.NEWSDATA_URL, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return 0, 0, f"Request failed: {e}"

    results = data.get("results", []) or []
    created = skipped = 0

    for item in results:
        title = (item.get("title") or "").strip()
        if not title:
            skipped += 1
            continue

        # Skip duplicates by title (model has unique=True on title)
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

        state = extract_state(title, description, keywords_text)
        score, level = compute_risk(title, description)

        News.objects.create(
            title=title[:500],
            description=description,
            source=item.get("source_id") or "",
            published_at=parse_pubdate(item.get("pubDate")),
            content=content,
            country="India" if country.lower() == "in" else country.upper(),
            state=state,
            risk_score=score,
            alert_level=level,
        )
        created += 1

    return created, skipped, None