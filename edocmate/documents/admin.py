import os
from django.conf import settings
from django.contrib import admin
from django.core.files.base import ContentFile
from django.utils.html import format_html
from pdf2image import convert_from_path
import PyPDF2
import pytesseract
import io
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

    def save_model(self, request, obj, form, change):
        # Call the parent save_model method to save the original file
        super().save_model(request, obj, form, change)

        if obj.file.name.endswith('.pdf'):
            images = convert_from_path(obj.file.path)
            searchable_pdf = io.BytesIO()
            pdf_writer = PyPDF2.PdfWriter()
            for image in images:
                page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
                pdf = PyPDF2.PdfReader(io.BytesIO(page))
                pdf_writer.add_page(pdf.pages[0])
            pdf_writer.write(searchable_pdf)
            searchable_pdf.seek(0)

            obj.file.save(obj.file.name, ContentFile(searchable_pdf.read()), save=True)


admin.site.register(Document, DocumentAdmin)
admin.site.register(Tag)
