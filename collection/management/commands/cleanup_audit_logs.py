from django.core.management.base import BaseCommand

from collection.services.audit_service import cleanup_old_audit_logs


class Command(BaseCommand):
    help = "Delete audit log records older than AUDIT_LOG_RETENTION_DAYS."

    def handle(self, *args, **options):
        deleted = cleanup_old_audit_logs()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} old audit log records."))

