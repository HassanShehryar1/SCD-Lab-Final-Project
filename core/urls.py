from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('jobs.urls')),
    path('insights/', include('insights.urls')),
    path('', lambda request: redirect('dashboard'), name='home'),
]
