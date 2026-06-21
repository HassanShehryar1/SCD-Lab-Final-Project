import csv
import json
import io
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Avg, Max, Min, Count, Q, Sum
from django.core.paginator import Paginator

from .models import JobPosting
from .forms import JobSearchForm, JobPostingForm

# ── ReportLab imports for PDF ──
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable


def _serialize_decimal(obj):
    """JSON serializer helper for Decimal types."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


@login_required
def dashboard_view(request):
    """Main dashboard with summary cards and chart data."""
    qs = JobPosting.objects.all()

    # ── Summary stats ──
    stats = qs.aggregate(
        total_jobs=Count('id'),
        avg_salary=Avg('salary_usd'),
        max_salary=Max('salary_usd'),
        min_salary=Min('salary_usd'),
        avg_satisfaction=Avg('employee_satisfaction'),
        total_openings=Sum('job_openings'),
    )

    # Top 10 hiring companies (by industry since no company_name field)
    top_industries = list(
        qs.values('industry')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    # ── Chart 1: Bar — Avg Salary by Job Role (Top 10) ──
    salary_by_role = list(
        qs.values('job_role')
        .annotate(avg_sal=Avg('salary_usd'))
        .order_by('-avg_sal')[:10]
    )
    chart1_labels = [r['job_role'] for r in salary_by_role]
    chart1_data = [float(r['avg_sal']) for r in salary_by_role]

    # ── Chart 2: Pie — Work Mode Distribution ──
    work_mode_dist = list(
        qs.values('work_mode')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    chart2_labels = [w['work_mode'] for w in work_mode_dist]
    chart2_data = [w['count'] for w in work_mode_dist]

    # ── Chart 3: Line — Jobs by Year (trend) ──
    jobs_by_year = list(
        qs.values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )
    chart3_labels = [str(j['year']) for j in jobs_by_year]
    chart3_data = [j['count'] for j in jobs_by_year]

    # ── Chart 4: Histogram — Salary Distribution (buckets) ──
    salary_ranges = [
        (0, 30000), (30000, 60000), (60000, 90000),
        (90000, 120000), (120000, 150000), (150000, 180000),
        (180000, 210000), (210000, 250000), (250000, 500000),
    ]
    chart4_labels = []
    chart4_data = []
    for low, high in salary_ranges:
        label = f"${low // 1000}k-${high // 1000}k"
        count = qs.filter(salary_usd__gte=low, salary_usd__lt=high).count()
        chart4_labels.append(label)
        chart4_data.append(count)

    # ── Chart 5: Scatter — Experience Years vs Salary ──
    scatter_data = list(
        qs.values('experience_years', 'salary_usd')
        .order_by('?')[:500]  # Sample 500 for performance
    )
    chart5_data = [
        {'x': s['experience_years'], 'y': float(s['salary_usd'])}
        for s in scatter_data
    ]

    # ── Top countries ──
    top_countries = list(
        qs.values('country')
        .annotate(count=Count('id'), avg_sal=Avg('salary_usd'))
        .order_by('-count')[:5]
    )

    context = {
        'stats': stats,
        'top_industries': top_industries,
        'top_countries': top_countries,
        # Chart data as JSON strings
        'chart1_labels': json.dumps(chart1_labels),
        'chart1_data': json.dumps(chart1_data),
        'chart2_labels': json.dumps(chart2_labels),
        'chart2_data': json.dumps(chart2_data),
        'chart3_labels': json.dumps(chart3_labels),
        'chart3_data': json.dumps(chart3_data),
        'chart4_labels': json.dumps(chart4_labels),
        'chart4_data': json.dumps(chart4_data),
        'chart5_data': json.dumps(chart5_data, default=_serialize_decimal),
    }
    return render(request, 'jobs/dashboard.html', context)


@login_required
def job_list_view(request):
    """Paginated, searchable, filterable job list."""
    form = JobSearchForm(request.GET)
    qs = JobPosting.objects.all()

    if form.is_valid():
        q = form.cleaned_data.get('q')
        country = form.cleaned_data.get('country')
        exp = form.cleaned_data.get('experience_level')
        mode = form.cleaned_data.get('work_mode')
        size = form.cleaned_data.get('company_size')
        min_sal = form.cleaned_data.get('min_salary')
        max_sal = form.cleaned_data.get('max_salary')
        sort = form.cleaned_data.get('sort_by')

        if q:
            qs = qs.filter(
                Q(job_role__icontains=q) |
                Q(ai_specialization__icontains=q) |
                Q(industry__icontains=q) |
                Q(country__icontains=q)
            )
        if country:
            qs = qs.filter(country=country)
        if exp:
            qs = qs.filter(experience_level=exp)
        if mode:
            qs = qs.filter(work_mode=mode)
        if size:
            qs = qs.filter(company_size=size)
        if min_sal:
            qs = qs.filter(salary_usd__gte=min_sal)
        if max_sal:
            qs = qs.filter(salary_usd__lte=max_sal)
        if sort:
            qs = qs.order_by(sort)

    # Aggregate stats for filtered results
    filtered_stats = qs.aggregate(
        count=Count('id'),
        avg_salary=Avg('salary_usd'),
        max_salary=Max('salary_usd'),
    )

    paginator = Paginator(qs, 25)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    context = {
        'form': form,
        'jobs': jobs,
        'filtered_stats': filtered_stats,
    }
    return render(request, 'jobs/job_list.html', context)


@login_required
def job_detail_view(request, pk):
    """Single job detail page."""
    job = get_object_or_404(JobPosting, pk=pk)
    return render(request, 'jobs/job_detail.html', {'job': job})


@login_required
def job_create_view(request):
    """Create a new job posting."""
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posting created successfully!')
            return redirect('job_list')
    else:
        form = JobPostingForm()
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Create Job Posting'})


@login_required
def job_update_view(request, pk):
    """Update an existing job posting."""
    job = get_object_or_404(JobPosting, pk=pk)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posting updated successfully!')
            return redirect('job_detail', pk=pk)
    else:
        form = JobPostingForm(instance=job)
    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Edit Job Posting'})


@login_required
def job_delete_view(request, pk):
    """Delete a job posting."""
    job = get_object_or_404(JobPosting, pk=pk)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job posting deleted successfully!')
        return redirect('job_list')
    return render(request, 'jobs/job_confirm_delete.html', {'job': job})


@login_required
def export_csv_view(request):
    """Export filtered jobs as CSV download."""
    qs = JobPosting.objects.all()

    # Apply same filters from GET params
    q = request.GET.get('q', '')
    country = request.GET.get('country', '')
    exp = request.GET.get('experience_level', '')
    mode = request.GET.get('work_mode', '')

    if q:
        qs = qs.filter(
            Q(job_role__icontains=q) | Q(ai_specialization__icontains=q) |
            Q(industry__icontains=q) | Q(country__icontains=q)
        )
    if country:
        qs = qs.filter(country=country)
    if exp:
        qs = qs.filter(experience_level=exp)
    if mode:
        qs = qs.filter(work_mode=mode)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tech_jobs_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Job Role', 'AI Specialization', 'Country', 'Industry',
        'Experience Level', 'Experience Years', 'Salary (USD)', 'Bonus (USD)',
        'Education', 'Company Size', 'Work Mode', 'Year',
        'Job Openings', 'Satisfaction Score'
    ])

    for job in qs[:5000]:  # Limit to 5000 for performance
        writer.writerow([
            job.job_role, job.ai_specialization, job.country, job.industry,
            job.experience_level, job.experience_years, job.salary_usd, job.bonus_usd,
            job.education_required, job.company_size, job.work_mode, job.year,
            job.job_openings, job.employee_satisfaction
        ])

    return response


@login_required
def export_pdf_view(request):
    """Generate a PDF summary report using ReportLab."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tech_jobs_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
                                  fontSize=22, textColor=colors.HexColor('#0ea5e9'),
                                  spaceAfter=20)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                    textColor=colors.HexColor('#38bdf8'), spaceAfter=10)
    body_style = styles['BodyText']

    # Title
    elements.append(Paragraph("Tech Job Market Analytics Report", title_style))
    elements.append(Paragraph(f"Generated for: {request.user.get_full_name() or request.user.username}", body_style))
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0ea5e9')))
    elements.append(Spacer(1, 20))

    # Summary stats
    qs = JobPosting.objects.all()
    stats = qs.aggregate(
        total=Count('id'),
        avg_sal=Avg('salary_usd'),
        max_sal=Max('salary_usd'),
        min_sal=Min('salary_usd'),
    )

    elements.append(Paragraph("Summary Statistics", heading_style))
    stats_data = [
        ['Metric', 'Value'],
        ['Total Job Postings', f"{stats['total']:,}"],
        ['Average Salary', f"${stats['avg_sal']:,.0f}" if stats['avg_sal'] else 'N/A'],
        ['Highest Salary', f"${stats['max_sal']:,.0f}" if stats['max_sal'] else 'N/A'],
        ['Lowest Salary', f"${stats['min_sal']:,.0f}" if stats['min_sal'] else 'N/A'],
    ]
    t = Table(stats_data, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.HexColor('#e2e8f0')]),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # Top 10 Industries
    elements.append(Paragraph("Top 10 Industries by Job Count", heading_style))
    top_ind = list(
        qs.values('industry')
        .annotate(count=Count('id'), avg_sal=Avg('salary_usd'))
        .order_by('-count')[:10]
    )
    ind_data = [['Industry', 'Job Count', 'Avg Salary']]
    for ind in top_ind:
        ind_data.append([
            ind['industry'],
            f"{ind['count']:,}",
            f"${ind['avg_sal']:,.0f}" if ind['avg_sal'] else 'N/A'
        ])
    t2 = Table(ind_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.HexColor('#e2e8f0')]),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 20))

    # Insights
    elements.append(Paragraph("Key Insights", heading_style))

    # Calculate insights
    from insights.engine import generate_insights
    insights = generate_insights()
    for insight in insights:
        elements.append(Paragraph(f"• {insight}", body_style))
    elements.append(Spacer(1, 10))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#64748b')))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Generated by Tech Job Market Analytics Dashboard — UMT Lahore SCD Lab Final Project", 
                               ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=colors.grey)))

    doc.build(elements)
    return response
