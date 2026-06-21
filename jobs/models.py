from django.db import models


class JobPosting(models.Model):
    """Model representing a tech/AI job posting from the dataset."""

    EXPERIENCE_CHOICES = [
        ('Entry', 'Entry Level'),
        ('Mid', 'Mid Level'),
        ('Senior', 'Senior Level'),
        ('Lead', 'Lead / Executive'),
    ]

    WORK_MODE_CHOICES = [
        ('Remote', 'Remote'),
        ('Onsite', 'On-site'),
        ('Hybrid', 'Hybrid'),
    ]

    COMPANY_SIZE_CHOICES = [
        ('Startup', 'Startup'),
        ('Small', 'Small'),
        ('Medium', 'Medium'),
        ('Large', 'Large'),
        ('Enterprise', 'Enterprise'),
    ]

    # Core job info
    job_role = models.CharField(max_length=150, db_index=True)
    ai_specialization = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, db_index=True)
    industry = models.CharField(max_length=100, blank=True, default='')

    # Experience
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, db_index=True)
    experience_years = models.IntegerField(default=0)

    # Compensation
    salary_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Education & company
    education_required = models.CharField(max_length=50, blank=True, default='')
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True, default='')
    company_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    # Work details
    work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES, db_index=True)
    weekly_hours = models.DecimalField(max_digits=4, decimal_places=1, default=40)
    year = models.IntegerField(default=2024, db_index=True)
    job_openings = models.IntegerField(default=1)

    # Scores and metrics
    skill_demand_score = models.IntegerField(default=0)
    automation_risk = models.IntegerField(default=0)
    job_security_score = models.IntegerField(default=0)
    career_growth_score = models.IntegerField(default=0)
    work_life_balance_score = models.IntegerField(default=0)
    employee_satisfaction = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-salary_usd']
        verbose_name_plural = 'Job Postings'

    def __str__(self):
        return f"{self.job_role} - {self.country} (${self.salary_usd:,.0f})"

    @property
    def total_compensation(self):
        return self.salary_usd + self.bonus_usd
