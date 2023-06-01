from django.contrib import admin
from .models import Lane, Note, ProposalRelation


@admin.register(Lane)
class LaneAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'is_proposal']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['dispute', 'lane', 'created_at']


@admin.register(ProposalRelation)
class ProposalRelationAdmin(admin.ModelAdmin):
    list_display = ['note', 'base_proposal', 'is_accepted']
