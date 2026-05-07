from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from .models import News
from .services import fetch_and_store
from .utils import INDIAN_STATES


def dashboard(request):
    qs = News.objects.all().order_by("-published_at", "-created_at")

    country = request.GET.get("country", "India")
    state = request.GET.get("state", "All")
    alert = request.GET.get("alert", "")
    q = request.GET.get("q", "").strip()

    if country and country != "India":
        qs = qs.filter(country__iexact=country)

    # ✅ State filtering - show all states unless specific state selected
    if state and state not in ("", "All"):
        qs = qs.filter(
            Q(state__iexact=state) |
            Q(title__icontains=state) |
            Q(description__icontains=state) |
            Q(content__icontains=state)
        )

    if alert and alert in ("LOW", "MEDIUM", "HIGH"):
        qs = qs.filter(alert_level=alert)

    # ✅ Full search (title + description + content)
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(content__icontains=q)
        )

    # ✅ Show only recent news (last 2 hours) by default when no filters
    if not (state not in ("", "All") or alert or q):
        time_threshold = timezone.now() - timedelta(hours=2)
        qs = qs.filter(created_at__gte=time_threshold)

    # ✅ Categorize news by type for better display
    election_keywords = Q(title__icontains="election") | Q(title__icontains="politics") | \
                       Q(title__icontains="campaign") | Q(title__icontains="voting") | \
                       Q(title__icontains="candidate") | Q(title__icontains="parliament") | \
                       Q(description__icontains="election") | Q(description__icontains="politics")
    
    disaster_keywords = Q(title__icontains="flood") | Q(title__icontains="earthquake") | \
                       Q(title__icontains="cyclone") | Q(title__icontains="disaster") | \
                       Q(title__icontains="fire") | Q(title__icontains="landslide") | \
                       Q(title__icontains="storm") | Q(title__icontains="drought") | \
                       Q(description__icontains="flood") | Q(description__icontains="earthquake")
    
    violence_keywords = Q(title__icontains="violence") | Q(title__icontains="attack") | \
                       Q(title__icontains="conflict") | Q(title__icontains="protest") | \
                       Q(title__icontains="riot") | Q(title__icontains="shooting") | \
                       Q(description__icontains="violence") | Q(description__icontains="attack")
    
    election_news = qs.filter(election_keywords)
    disaster_news = qs.filter(disaster_keywords).exclude(election_keywords)
    violence_news = qs.filter(violence_keywords).exclude(election_keywords).exclude(disaster_keywords)
    other_news = qs.exclude(election_keywords).exclude(disaster_keywords).exclude(violence_keywords)

    # Paginate each category
    election_paginator = Paginator(election_news, 12)
    election_page_obj = election_paginator.get_page(request.GET.get("election_page", 1))
    
    disaster_paginator = Paginator(disaster_news, 12)
    disaster_page_obj = disaster_paginator.get_page(request.GET.get("disaster_page", 1))
    
    violence_paginator = Paginator(violence_news, 12)
    violence_page_obj = violence_paginator.get_page(request.GET.get("violence_page", 1))
    
    other_paginator = Paginator(other_news, 12)
    other_page_obj = other_paginator.get_page(request.GET.get("other_page", 1))

    context = {
        "election_page_obj": election_page_obj,
        "disaster_page_obj": disaster_page_obj,
        "violence_page_obj": violence_page_obj,
        "other_page_obj": other_page_obj,
        "states": ["All"] + INDIAN_STATES + ["National"],
        "selected_country": country,
        "selected_state": state or "All",
        "selected_alert": alert or "",
        "query": q,
        "total": qs.count(),
        "election_total": election_news.count(),
        "disaster_total": disaster_news.count(),
        "violence_total": violence_news.count(),
        "other_total": other_news.count(),
    }
    return render(request, "dashboard.html", context)


def fetch_news_view(request):
    # Allow fetching with specific query or state
    query = request.GET.get("query", None)
    state = request.GET.get("state", None)
    
    # Fetch all trending news by default
    created, skipped, err = fetch_and_store(country="in", query=query, state=state, fetch_all=True)
    if err:
        messages.error(request, err)
    else:
        fetch_type = f"for {state}" if state else (f"for '{query}'" if query else "")
        messages.success(request, f"Fetched {fetch_type}: {created} new, {skipped} skipped/duplicate.")
    return redirect("dashboard")