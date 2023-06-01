from django.contrib import admin

from core.forms import CustomAdminAuthenticationForm

# Register your models here.

admin.site.login_form = CustomAdminAuthenticationForm
