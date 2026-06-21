from django import forms
from .models import JobPosting


class JobSearchForm(forms.Form):
    """Search and filter form for job listings."""
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by job role, specialization, or industry...',
            'id': 'id_search_query'
        })
    )
    country = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_country'})
    )
    experience_level = forms.ChoiceField(
        required=False,
        choices=[('', 'All Experience Levels')] + JobPosting.EXPERIENCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_experience_level'})
    )
    work_mode = forms.ChoiceField(
        required=False,
        choices=[('', 'All Work Modes')] + JobPosting.WORK_MODE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_work_mode'})
    )
    company_size = forms.ChoiceField(
        required=False,
        choices=[('', 'All Company Sizes')] + JobPosting.COMPANY_SIZE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_company_size'})
    )
    min_salary = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Salary ($)',
            'id': 'id_min_salary'
        })
    )
    max_salary = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Salary ($)',
            'id': 'id_max_salary'
        })
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('-salary_usd', 'Salary: High to Low'),
            ('salary_usd', 'Salary: Low to High'),
            ('-year', 'Most Recent'),
            ('year', 'Oldest First'),
            ('-employee_satisfaction', 'Highest Satisfaction'),
            ('-career_growth_score', 'Best Career Growth'),
        ],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_sort_by'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        countries = JobPosting.objects.values_list('country', flat=True).distinct().order_by('country')
        country_choices = [('', 'All Countries')] + [(c, c) for c in countries]
        self.fields['country'].choices = country_choices


class JobPostingForm(forms.ModelForm):
    """Form for creating/editing job postings (CRUD)."""
    class Meta:
        model = JobPosting
        fields = [
            'job_role', 'ai_specialization', 'country', 'industry',
            'experience_level', 'experience_years', 'salary_usd', 'bonus_usd',
            'education_required', 'company_size', 'company_rating',
            'work_mode', 'weekly_hours', 'year', 'job_openings',
            'skill_demand_score', 'career_growth_score', 'work_life_balance_score',
            'employee_satisfaction'
        ]
        widgets = {
            'job_role': forms.TextInput(attrs={'class': 'form-control'}),
            'ai_specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_usd': forms.NumberInput(attrs={'class': 'form-control'}),
            'bonus_usd': forms.NumberInput(attrs={'class': 'form-control'}),
            'education_required': forms.TextInput(attrs={'class': 'form-control'}),
            'company_size': forms.Select(attrs={'class': 'form-select'}),
            'company_rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'work_mode': forms.Select(attrs={'class': 'form-select'}),
            'weekly_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'job_openings': forms.NumberInput(attrs={'class': 'form-control'}),
            'skill_demand_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'career_growth_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'work_life_balance_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'employee_satisfaction': forms.NumberInput(attrs={'class': 'form-control'}),
        }
