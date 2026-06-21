"""
Management command to import the Kaggle Global AI Jobs dataset into the database.
Usage: python manage.py import_jobs
"""
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from jobs.models import JobPosting


class Command(BaseCommand):
    help = 'Import Global AI Jobs dataset from CSV into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of rows to import (default: all)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing',
        )

    def handle(self, *args, **options):
        csv_path = settings.DATASET_PATH
        limit = options['limit']
        clear = options['clear']

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f'Dataset not found at: {csv_path}'))
            return

        if clear:
            deleted_count = JobPosting.objects.count()
            JobPosting.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {deleted_count} existing records.'))

        self.stdout.write(self.style.NOTICE(f'Reading CSV from: {csv_path}'))
        df = pd.read_csv(csv_path)

        if limit:
            df = df.head(limit)

        self.stdout.write(self.style.NOTICE(f'Processing {len(df)} rows...'))

        jobs_to_create = []
        for _, row in df.iterrows():
            try:
                job = JobPosting(
                    job_role=str(row.get('job_role', '')).strip(),
                    ai_specialization=str(row.get('ai_specialization', '')).strip(),
                    country=str(row.get('country', '')).strip(),
                    industry=str(row.get('industry', '')).strip(),
                    experience_level=str(row.get('experience_level', 'Entry')).strip(),
                    experience_years=int(row.get('experience_years', 0)),
                    salary_usd=float(row.get('salary_usd', 0)),
                    bonus_usd=float(row.get('bonus_usd', 0)),
                    education_required=str(row.get('education_required', '')).strip(),
                    company_size=str(row.get('company_size', '')).strip(),
                    company_rating=float(row.get('company_rating', 0)),
                    work_mode=str(row.get('work_mode', 'Onsite')).strip(),
                    weekly_hours=float(row.get('weekly_hours', 40)),
                    year=int(row.get('year', 2024)),
                    job_openings=int(row.get('job_openings', 1)),
                    skill_demand_score=int(row.get('skill_demand_score', 0)),
                    automation_risk=int(row.get('automation_risk', 0)),
                    job_security_score=int(row.get('job_security_score', 0)),
                    career_growth_score=int(row.get('career_growth_score', 0)),
                    work_life_balance_score=int(row.get('work_life_balance_score', 0)),
                    employee_satisfaction=int(row.get('employee_satisfaction', 0)),
                )
                jobs_to_create.append(job)
            except Exception as e:
                self.stderr.write(self.style.WARNING(f'Skipping row {_}: {e}'))

        # Bulk create in batches of 5000
        batch_size = 5000
        total_created = 0
        for i in range(0, len(jobs_to_create), batch_size):
            batch = jobs_to_create[i:i + batch_size]
            JobPosting.objects.bulk_create(batch)
            total_created += len(batch)
            self.stdout.write(self.style.NOTICE(f'  Imported {total_created}/{len(jobs_to_create)} records...'))

        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully imported {total_created} job postings!'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Total records in database: {JobPosting.objects.count()}'
        ))
