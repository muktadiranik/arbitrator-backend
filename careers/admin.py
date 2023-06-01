from django.contrib import admin
from .models import JobDetail, JobApplication, Experience, Opening


# Register your models here.
@admin.register(JobDetail)
class JobDetailAdmin(admin.ModelAdmin):
    list_filter = ['type']
    search_fields = ['id']
    list_display = ['type', 'text']


@admin.register(Opening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_filter = ['position', 'employment_type']
    search_fields = ['id', 'title']
    list_display = ['title', 'position', 'employment_type', 'created_at']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_filter = ['opening']
    search_fields = ['id', 'first_name', 'last_name', 'email']
    list_display = ['first_name', 'last_name', 'email', 'get_opening_title']

    def get_opening_title(self, obj):
        return obj.opening.title if obj.opening else None

    get_opening_title.short_description = 'Opening Title'


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_filter = ['application']
    search_fields = ['company', 'job_title']
    list_display = ['application', 'job_title', 'company', 'start_date', 'end_date']
