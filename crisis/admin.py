from django.contrib import admin
from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "state", "alert_level", "risk_score", "published_at")
    list_filter = ("alert_level", "state", "country")
    search_fields = ("title", "description", "content")
