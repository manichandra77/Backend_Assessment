from django.core.management.base import BaseCommand
from api.tasks import ingest_data_task

class Command(BaseCommand):
    help = 'Ingests data from Excel files into the database via a background task.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Queueing data ingestion task...'))
        ingest_data_task.delay()
        self.stdout.write(self.style.SUCCESS('Task has been queued.'))