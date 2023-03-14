from django.contrib import admin
from django.utils.html import format_html
from .models import Document, Tag

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'file_preview', 'tags_list', 'date_created', 'date_modified')
    readonly_fields = ('file_preview',)

    def tags_list(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())

    tags_list.short_description = 'Tags'
    def file_preview(self, obj):
        if obj.file:
            if obj.file.name.endswith('.pdf'):
                return format_html('<embed src="{}#view=FitH" width="300" height="200" type="application/pdf"/>',
                                   obj.file.url)
            elif obj.file.name.endswith('.jpg') or obj.file.name.endswith('.jpeg') or obj.file.name.endswith('.png'):
                return format_html('<img src="{}" width="300" height="200" />', obj.file.url)
        return '-'

    file_preview.short_description = 'File Preview'



admin.site.register(Document, DocumentAdmin)
admin.site.register(Tag)
