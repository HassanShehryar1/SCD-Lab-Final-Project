from django.contrib import admin
from .models import JobPosting


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['job_role', 'country', 'experience_level', 'salary_usd', 'work_mode', 'year', 'industry']
    list_filter = ['experience_level', 'work_mode', 'country', 'year', 'company_size']
    search_fields = ['job_role', 'country', 'ai_specialization', 'industry']
    list_per_page = 50
    ordering = ['-salary_usd']
