
from django.core.management.base import BaseCommand
from api.models import Scale, ScanWatchSummary, SleepmatSummary, ScanWatchIntraActivity, SleepmatIntraActivity 
from django.db.models import Count
from django.db import transaction

class Command(BaseCommand):

    help = 'Remove duplicate records from Author, Book, and Publisher models.'
    BATCH_SIZE = 2000

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to clean duplicates...')

        # Clean duplicates in each model
        self.clean_scale_duplicates()
        self.clean_scanwatch_summary_duplicates()
        self.clean_sleepmat_summary_duplicates()
        self.clean_scanwatch_intra_duplicates()
        self.clean_sleepmat_intra_duplicates()
        self.stdout.write(self.style.SUCCESS('Duplicates cleaned successfully!'))

    def clean_scale_duplicates(self):
        duplicates = (
            Scale.objects
            .values('user','date')
            .annotate(date_count=Count('id'))
            .filter(date_count__gt=1)
        )
        with transaction.atomic():
            for duplicate in duplicates:
                duplicate_scales = Scale.objects.filter(
                    user=duplicate['user'], 
                    date=duplicate['date']
                )
                duplicate_scales.exclude(pk=duplicate_scales.first().pk).delete()

    def clean_scanwatch_summary_duplicates(self):

        duplicates = (
            ScanWatchSummary.objects
            .values('user','date')
            .annotate(date_count=Count('id'))
            .filter(date_count__gt=1)
        )
        with transaction.atomic():
            for duplicate in duplicates:
                # Get all authors with this name
                duplicate_scanwatch = ScanWatchSummary.objects.filter(
                    user = duplicate['user'],
                    date = duplicate['date']
                )
                # Keep one, delete the rest
                duplicate_scanwatch.exclude(pk=duplicate_scanwatch.first().pk).delete()

    def clean_sleepmat_summary_duplicates(self):

        duplicates = (
            SleepmatSummary.objects
            .values('user','start_date')
            .annotate(start_date_count=Count('id'))
            .filter(start_date_count__gt=1)
        )
        with transaction.atomic():
            for duplicate in duplicates:
                # Get all authors with this name
                duplicate_sleepmat = SleepmatSummary.objects.filter(
                    user = duplicate['user'],
                    start_date = duplicate['start_date'])
                # Keep one, delete the rest
                duplicate_sleepmat.exclude(pk=duplicate_sleepmat.first().pk).delete()

    
    def clean_scanwatch_intra_duplicates(self):

        duplicates = (
            ScanWatchIntraActivity.objects
            .values('user','date_heart_rate')
            .annotate(date_hr_count=Count('id'))
            .filter(date_hr_count__gt=1)
        )

        for duplicate in duplicates.iterator(chunk_size = self.BATCH_SIZE):
            duplicate_scanwatch_intra = ScanWatchIntraActivity.objects.filter(
                user = duplicate['user'],
                date_heart_rate=duplicate['date_heart_rate']
                )
            with transaction.atomic():
                duplicate_scanwatch_intra.exclude(pk = duplicate_scanwatch_intra.first().pk).delete()


    def clean_sleepmat_intra_duplicates(self):

        duplicates = (
            SleepmatIntraActivity.objects
            .values('user','start_date')
            .annotate(start_date_count=Count('id'))
            .filter(start_date__gt=1)
        )

        for duplicate in duplicates.iterator(chunk_size = self.BATCH_SIZE):
            duplicate_sleepmat_intra = SleepmatIntraActivity.objects.filter(
                user = duplicate['user'],
                start_date=duplicate['date_heart_rate'])
            with transaction.atomic():
                duplicate_sleepmat_intra.exclude(pk=duplicate_sleepmat_intra.first().pk).delete()

