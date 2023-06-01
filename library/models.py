import os

from django.core.validators import FileExtensionValidator
from django.db import models
from choices import LIBRARY_CHOICES, LIBRARY_FOLDER_CHOICES
from litigation.models import Dispute, Actor
from litigation.models import Arbitrator


class Firm(models.Model):
    name = models.CharField(max_length=28)

    def __str__(self):
        return f'{self.name}'


class ClauseCategory(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.name}'


class Clause(models.Model):
    arbitrator = models.ForeignKey(Arbitrator, related_name='clauses', on_delete=models.PROTECT)
    firm = models.ForeignKey(Firm, related_name='clauses', on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(ClauseCategory, related_name='clauses', on_delete=models.DO_NOTHING, null=True,
                                 blank=True)
    title = models.CharField(max_length=64)
    content = models.TextField()
    sequence = models.IntegerField()
    type = models.CharField(choices=LIBRARY_CHOICES, max_length=16, null=True, blank=True)

    class Meta:
        ordering = ('sequence',)
        permissions = [
            ('insert_clause', 'Can insert clause')
        ]

    def __str__(self):
        return f'{self.title}'


class ChecklistCategory(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.name}'


class Checklist(models.Model):
    category = models.ForeignKey(ChecklistCategory, related_name='checklist', on_delete=models.DO_NOTHING, null=True,
                                 blank=True)
    arbitrator = models.ForeignKey(Arbitrator, related_name='checklists', on_delete=models.PROTECT)
    firm = models.ForeignKey(Firm, related_name='checklists', on_delete=models.DO_NOTHING, null=True, blank=True)
    name = models.CharField(max_length=24)
    description = models.TextField()
    sequence = models.IntegerField()
    type = models.CharField(choices=LIBRARY_CHOICES, max_length=16, null=True, blank=True)

    class Meta:
        ordering = ('sequence',)

    def __str__(self):
        return f'{self.name}'


class LibraryChecklistItem(models.Model):
    checklist = models.ForeignKey(Checklist, related_name='items', on_delete=models.CASCADE)
    text = models.CharField(max_length=96)
    comments = models.CharField(max_length=300, null=True, blank=True)
    initials = models.CharField(max_length=48, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    sequence = models.IntegerField()

    class Meta:
        ordering = ('sequence',)

    def __str__(self):
        return f'{self.checklist}: {self.text}'


class TermsheetChecklistItem(models.Model):
    checklist = models.ForeignKey(Checklist, related_name='termsheet_items', on_delete=models.CASCADE)
    text = models.CharField(max_length=96)
    comments = models.CharField(max_length=300, null=True, blank=True)
    initials = models.CharField(max_length=48, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    sequence = models.IntegerField()
    checked = models.BooleanField(default=False)

    class Meta:
        ordering = ('sequence',)

    def __str__(self):
        return f'{self.checklist}: {self.text}'


class Folder(models.Model):
    creator = models.ForeignKey(Actor, related_name='creator_folders', on_delete=models.PROTECT, null=True, blank=True)
    arbitrator = models.ForeignKey(Arbitrator, related_name='folders', on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=24)
    relation = models.CharField(choices=LIBRARY_FOLDER_CHOICES, max_length=12)
    parent = models.ForeignKey('Folder', related_name='folders', on_delete=models.CASCADE, null=True, blank=True)
    firm = models.ForeignKey(Firm, on_delete=models.DO_NOTHING, null=True, blank=True)
    case = models.ForeignKey(Dispute, related_name='folders', on_delete=models.CASCADE, null=True, blank=True)
    sequence = models.IntegerField()
    type = models.CharField(choices=LIBRARY_CHOICES, max_length=16, null=True, blank=True)

    class Meta:
        ordering = ('sequence',)

    def __str__(self):
        return f'{self.name}'


class File(models.Model):
    folder = models.ForeignKey(Folder, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='library-files/',
                            validators=[FileExtensionValidator(
                                allowed_extensions=["pdf", "doc", "docx", "jpg", "png", "mp4"])])
    sequence = models.IntegerField()

    class Meta:
        permissions = [
            ('download_file', 'Can download file')
        ]

    @property
    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()

    @property
    def name(self):
        return self.file.name.split('/')[1]

    @property
    def size(self):
        return self.file.size


class Document(models.Model):
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
