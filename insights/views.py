from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .engine import generate_insights


@login_required
def insights_view(request):
    """View to display dynamic market insights generated from database postings."""
    insights = generate_insights()
    return render(request, 'insights/insights.html', {'insights': insights})
