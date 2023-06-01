from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SectionTitle)
admin.site.register(TermsheetTitle)
admin.site.register(DigitalSignature)


@admin.register(TermSheet)
class TermSheetAdmin(admin.ModelAdmin):
    search_fields = ['id', 'dispute__code', 'title']
    list_display = ['dispute', 'title']


@admin.register(TermsheetSection)
class TermsheetSectionAdmin(admin.ModelAdmin):
    search_fields = ['id', 'termsheet__title', 'title']
    list_display = ['termsheet', 'title']
