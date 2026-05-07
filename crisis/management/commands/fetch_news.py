from django.core.management.base import BaseCommand
from crisis.services import fetch_and_store


class Command(BaseCommand):
    help = "Fetch latest news from NewsData.io (country=IN), score crisis risk, and store."

    def add_arguments(self, parser):
        parser.add_argument("--country", default="in", help="NewsData.io country code (default: in)")
        parser.add_argument("--query", default=None, help="Search query (e.g., 'election', 'West Bengal election')")
        parser.add_argument("--state", default=None, help="Indian state (fetches election/politics for that state)")
        parser.add_argument("--all", action="store_true", help="Fetch all trending news (crisis, disaster, election, politics)")

    def handle(self, *args, **opts):
        created, skipped, err = fetch_and_store(
            country=opts["country"], 
            query=opts.get("query"),
            state=opts.get("state"),
            fetch_all=opts.get("all", True)
        )
        if err:
            self.stderr.write(self.style.ERROR(err))
            return
        self.stdout.write(self.style.SUCCESS(
            f"Done. Created={created}, Skipped/Duplicate={skipped}"
        ))
