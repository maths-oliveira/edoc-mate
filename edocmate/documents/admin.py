from django.utils.html import format_html
from .models import Document, DocumentLabel, Label, Dossier
from django.contrib import admin
from pdf2image import convert_from_bytes
import io
import pytesseract
import PyPDF2
from PIL import Image


class LabelInline(admin.TabularInline):
    model = Document.labels.through

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_label', 'file_preview', 'date_created', 'date_modified')
    readonly_fields = ('file_preview',)
    inlines = [LabelInline]
    def get_label(self, obj):
        rels = obj.documentlabel_set.all()
        return ", ".join([f"{rel.label.name}: {rel.value}" for rel in rels])

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
        # process the pdf file only if it's a new upload
        # get the uploaded file
        uploaded_file = form.cleaned_data['file']

        if uploaded_file.name.endswith('.pdf'):
            images = convert_from_bytes(uploaded_file.read())
        else:
            images = [Image.open(uploaded_file)]

        # convert the pdf file to searchable pdf
        pdf_writer = PyPDF2.PdfWriter()
        for image in images:
            page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(page))
            pdf_writer.add_page(pdf_reader.pages[0])
        # save the searchable pdf to the pdf_file field
        output_file = io.BytesIO()
        pdf_writer.write(output_file)

        obj.file.save('.'.join(uploaded_file.name.split('.')[:-1]) + '.pdf', output_file)
        super().save_model(request, obj, form, change)

class DocumentLabelAdmin(admin.ModelAdmin):
    model = DocumentLabel

admin.site.register(Document, DocumentAdmin)
admin.site.register(Label)
admin.site.register(Dossier)
