from django.contrib import admin

from notes.models import Note


# Register your models here.
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_filter = ['content_type']
    search_fields = ['id', 'title', 'author__first_name']
    list_display = ['title', 'author', 'created_at']
