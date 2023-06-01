from django.contrib import admin

from timelog.models import DurationPackage, TimeLog


# Register your models here.
@admin.register(DurationPackage)
class DurationPackageAdmin(admin.ModelAdmin):
    pass


@admin.register(TimeLog)
class TimelogAdmin(admin.ModelAdmin):
    list_filter = ['type']
    search_fields = ['id', 'note', 'dispute', 'creator', 'participant']
    list_display = ['note', 'start_time', 'end_time', 'type', 'dispute', 'creator', 'participant']
