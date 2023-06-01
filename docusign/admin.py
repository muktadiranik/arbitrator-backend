from django.contrib import admin
from docusign.models import DocuSignEnvelope


@admin.register(DocuSignEnvelope)
class DisputeAdmin(admin.ModelAdmin):
    search_fields = ['id', 'envelope_id', 'dispute__code']
    list_display = ['envelope_id', 'dispute']
