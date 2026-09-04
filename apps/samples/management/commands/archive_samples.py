from django.core.management.base import BaseCommand

from apps.samples.models import SamplePO


class Command(BaseCommand):
    """Run daily (via cron or Celery Beat in production) to auto-archive
    delivered samples 21 days after delivery, per the client's rule."""
    help = "Archive SamplePOs delivered 21+ days ago."

    def handle(self, *args, **options):
        count = 0
        for sample in SamplePO.objects.filter(status="delivered"):
            before = sample.status
            sample.archive_if_due()
            if sample.status != before:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Archived {count} sample PO(s)."))
