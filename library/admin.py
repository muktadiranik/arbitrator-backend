from django.contrib import admin
from .models import ChecklistCategory, Clause, Checklist, LibraryChecklistItem, Folder, File, Document, ClauseCategory, \
    TermsheetChecklistItem

# Register your models here.
admin.site.register(ChecklistCategory)
admin.site.register(ClauseCategory)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'extension', 'size', 'folder']


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_filter = ['relation', 'type']
    list_display = ['arbitrator', 'name', 'relation', 'parent', 'type']
    search_fields = ['id', 'name', 'arbitrator__id']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['id', 'dispute__code']
    list_display = ['dispute', 'created_at', 'updated_at']


@admin.register(LibraryChecklistItem)
class LibraryChecklistItemAdmin(admin.ModelAdmin):
    search_fields = ['id', 'checklist__name']
    list_display = ['checklist', 'text']


@admin.register(TermsheetChecklistItem)
class TermsheetChecklistItemAdmin(admin.ModelAdmin):
    search_fields = ['id', 'checklist__name']
    list_display = ['checklist', 'text', 'initials', 'due_date']


@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    list_filter = ['type']
    search_fields = ['id', 'arbitrator__id', 'title']
    list_display = ['title', 'category', 'type', 'arbitrator']


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_filter = ['type']
    search_fields = ['id', 'arbitrator__id', 'name', 'firm__name']
    list_display = ['name', 'type', 'firm', 'arbitrator']
