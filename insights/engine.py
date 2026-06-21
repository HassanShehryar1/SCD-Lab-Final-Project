"""
Insight Generation Engine — uses Django ORM to compute dynamic insights
about the tech job market dataset.
"""
from django.db.models import Avg, Count, Max, Min, Q
from jobs.models import JobPosting


def generate_insights():
    """Generate a list of human-readable insight strings from the dataset."""
    insights = []
    qs = JobPosting.objects.all()
    total = qs.count()

    if total == 0:
        return ["No data available. Please import the dataset first."]

    # ── 1. Most in-demand role ──
    top_role = (
        qs.values('job_role')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    if top_role:
        pct = (top_role['count'] / total) * 100
        insights.append(
            f"🔥 <strong>{top_role['job_role']}</strong> is the most in-demand role, "
            f"appearing in {pct:.1f}% of all job postings ({top_role['count']:,} jobs)."
        )

    # ── 2. Remote vs On-site salary comparison ──
    remote_avg = qs.filter(work_mode='Remote').aggregate(avg=Avg('salary_usd'))['avg']
    onsite_avg = qs.filter(work_mode='Onsite').aggregate(avg=Avg('salary_usd'))['avg']
    if remote_avg and onsite_avg:
        diff_pct = ((remote_avg - onsite_avg) / onsite_avg) * 100
        if diff_pct > 0:
            insights.append(
                f"🏠 Remote jobs offer a <strong>{diff_pct:.1f}% higher</strong> average salary "
                f"(${remote_avg:,.0f}) compared to on-site roles (${onsite_avg:,.0f})."
            )
        else:
            insights.append(
                f"🏢 On-site jobs offer a <strong>{abs(diff_pct):.1f}% higher</strong> average salary "
                f"(${onsite_avg:,.0f}) compared to remote roles (${remote_avg:,.0f})."
            )

    # ── 3. Highest paying specialization ──
    top_spec = (
        qs.values('ai_specialization')
        .annotate(avg_sal=Avg('salary_usd'))
        .order_by('-avg_sal')
        .first()
    )
    if top_spec:
        insights.append(
            f"💰 The highest average salary is found in <strong>{top_spec['ai_specialization']}</strong> "
            f"specialization at ${top_spec['avg_sal']:,.0f}."
        )

    # ── 4. Best country for salary ──
    top_country = (
        qs.values('country')
        .annotate(avg_sal=Avg('salary_usd'))
        .order_by('-avg_sal')
        .first()
    )
    if top_country:
        insights.append(
            f"🌍 <strong>{top_country['country']}</strong> offers the highest average salary "
            f"at ${top_country['avg_sal']:,.0f} for tech/AI jobs."
        )

    # ── 5. Experience impact ──
    entry_avg = qs.filter(experience_level='Entry').aggregate(avg=Avg('salary_usd'))['avg']
    senior_avg = qs.filter(experience_level='Senior').aggregate(avg=Avg('salary_usd'))['avg']
    if entry_avg and senior_avg:
        multiplier = senior_avg / entry_avg
        insights.append(
            f"📈 Senior-level professionals earn <strong>{multiplier:.1f}x more</strong> than entry-level "
            f"(${senior_avg:,.0f} vs ${entry_avg:,.0f})."
        )

    # ── 6. Most popular industry ──
    top_industry = (
        qs.values('industry')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    if top_industry:
        ind_pct = (top_industry['count'] / total) * 100
        insights.append(
            f"🏭 The <strong>{top_industry['industry']}</strong> industry leads with "
            f"{ind_pct:.1f}% of all job postings."
        )

    # ── 7. Work-life balance insight ──
    best_wlb = (
        qs.values('work_mode')
        .annotate(avg_wlb=Avg('work_life_balance_score'))
        .order_by('-avg_wlb')
        .first()
    )
    if best_wlb:
        insights.append(
            f"⚖️ <strong>{best_wlb['work_mode']}</strong> jobs have the best work-life balance score "
            f"averaging {best_wlb['avg_wlb']:.1f}/100."
        )

    # ── 8. Company size vs salary ──
    enterprise_avg = qs.filter(company_size='Enterprise').aggregate(avg=Avg('salary_usd'))['avg']
    startup_avg = qs.filter(company_size='Startup').aggregate(avg=Avg('salary_usd'))['avg']
    if enterprise_avg and startup_avg:
        insights.append(
            f"🏢 Enterprise companies pay <strong>${enterprise_avg:,.0f}</strong> on average vs "
            f"<strong>${startup_avg:,.0f}</strong> at startups — a ${enterprise_avg - startup_avg:,.0f} difference."
        )

    # ── 9. Year-over-year growth ──
    years = list(
        qs.values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )
    if len(years) >= 2:
        latest = years[-1]
        prev = years[-2]
        if prev['count'] > 0:
            growth = ((latest['count'] - prev['count']) / prev['count']) * 100
            direction = "increased" if growth > 0 else "decreased"
            insights.append(
                f"📊 Job postings {direction} by <strong>{abs(growth):.1f}%</strong> "
                f"from {prev['year']} ({prev['count']:,} jobs) to {latest['year']} ({latest['count']:,} jobs)."
            )

    # ── 10. Satisfaction sweet spot ──
    top_sat = (
        qs.values('job_role')
        .annotate(avg_sat=Avg('employee_satisfaction'))
        .order_by('-avg_sat')
        .first()
    )
    if top_sat:
        insights.append(
            f"😊 <strong>{top_sat['job_role']}</strong> professionals report the highest satisfaction "
            f"score of {top_sat['avg_sat']:.1f}/100."
        )

    return insights
