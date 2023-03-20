from django.utils.html import format_html
from .models import Document, DocumentLabel, Label, Dossier
from django.contrib import admin
from pdf2image import convert_from_bytes
import pytesseract
import PyPDF2
from PIL import Image
import io
from django.http import HttpResponse
from PyPDF2 import PdfWriter, PdfReader

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




def download_dossier_pdf(modeladmin, request, queryset):
    # create a new PDF file
    pdf_writer = PdfWriter()

    # loop through all the documents in the selected dossiers
    for dossier in queryset:
        documents = Document.objects.filter(dossiers=dossier)
        for document in documents:
            # add the document file to the PDF file
            pdf_reader = PdfReader(document.file)
            for page in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page])

    output_buffer = io.BytesIO()
    pdf_writer.write(output_buffer)

    # create a response object with the PDF file as the content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dossier.pdf"'
    response.write(output_buffer.getvalue())

    return response

download_dossier_pdf.short_description = 'Download selected dossiers as PDF'


class DossierAdmin(admin.ModelAdmin):
    list_display = ('name',)
    actions = [download_dossier_pdf]

admin.site.register(Dossier, DossierAdmin)

admin.site.register(Document, DocumentAdmin)
admin.site.register(Label)
