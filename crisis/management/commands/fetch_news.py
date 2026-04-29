from django.core.management.base import BaseCommand
from crisis.services import fetch_and_store


class Command(BaseCommand):
    help = "Fetch latest news from NewsData.io (country=IN), score crisis risk, and store."

    def add_arguments(self, parser):
        parser.add_argument("--country", default="in", help="NewsData.io country code (default: in)")

    def handle(self, *args, **opts):
        created, skipped, err = fetch_and_store(country=opts["country"])
        if err:
            self.stderr.write(self.style.ERROR(err))
            return
        self.stdout.write(self.style.SUCCESS(
            f"Done. Created={created}, Skipped/Duplicate={skipped}"
        ))
