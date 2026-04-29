from django.db import models


class News(models.Model):
    ALERT_CHOICES = [
        ("LOW", "LOW"),
        ("MEDIUM", "MEDIUM"),
        ("HIGH", "HIGH"),
    ]

    title = models.CharField(max_length=500, unique=True)
    description = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=200, blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, default="India")
    state = models.CharField(max_length=100, default="National")
    risk_score = models.IntegerField(default=0)
    alert_level = models.CharField(max_length=10, choices=ALERT_CHOICES, default="LOW")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name_plural = "News"

    def __str__(self):
        return f"[{self.alert_level}] {self.title[:80]}"