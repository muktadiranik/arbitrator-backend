"""Arbitrator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

admin.site.site_header = 'Arbitration Admin'
admin.site.index_title = 'Admin Panel'

urlpatterns = [
                  path('site/admin-panel/', admin.site.urls),
                  path('auth/', include('core.urls')),
                  path('registration/', include('dj_rest_auth.registration.urls')),
                  path('litigation/', include('litigation.urls')),
                  path('library/', include('library.urls')),
                  path('notes/', include('notes.urls')),
                  path('noteboard/', include('noteboard.urls')),
                  path('timelog/', include('timelog.urls')),
                  path('term-sheet/', include('termsheet.urls')),
                  path('docusign/', include('docusign.urls')),
                  path('pricing/', include('pricing.urls')),
                  path('activity/', include('actstream.urls')),
                  path('careers/', include('careers.urls')),
                  path('notifications/', include('notifications.urls'))
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
