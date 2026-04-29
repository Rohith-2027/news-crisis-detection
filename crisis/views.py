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
    qs = News.objects.all()

    country = request.GET.get("country", "India")
    state = request.GET.get("state", "")
    alert = request.GET.get("alert", "")
    q = request.GET.get("q", "").strip()

    if country and country != "India":
        qs = qs.filter(country__iexact=country)

    # If state empty or "All" -> show all news for India

    if state and state not in ("", "All"):
        qs = qs.filter(
            Q(state__iexact=state) |
            Q(title__icontains=state) |
            Q(description__icontains=state)
        )

    if alert and alert in ("LOW", "MEDIUM", "HIGH"):
        qs = qs.filter(alert_level=alert)

    # ✅ Fixed search
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    # 🔥 Show only recent news (last 30 mins) by default
    if not (state not in ("", "All") or alert or q):
        time_threshold = timezone.now() - timedelta(minutes=30)
        qs = qs.filter(created_at__gte=time_threshold)

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "states": ["All"] + INDIAN_STATES + ["National"],
        "selected_country": country,
        "selected_state": state or "All",
        "selected_alert": alert or "",
        "query": q,
        "total": qs.count(),
    }
    return render(request, "dashboard.html", context)


def fetch_news_view(request):
    created, skipped, err = fetch_and_store(country="in")
    if err:
        messages.error(request, err)
    else:
        messages.success(request, f"Fetched: {created} new, {skipped} skipped/duplicate.")
    return redirect("dashboard")