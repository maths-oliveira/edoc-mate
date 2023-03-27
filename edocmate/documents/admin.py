from django.utils.html import format_html
from .models import Document, Dossier, Person, Category, TType, Other
import pytesseract
import PyPDF2
import pypdfium2 as pdfium
from PIL import Image
import io
from django.http import HttpResponse
from PyPDF2 import PdfWriter
from pypdf import PdfReader
from django.contrib import admin
from django import forms
from .models import Document

class DocumentAdminForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = '__all__'

    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))



class DocumentAdmin(admin.ModelAdmin):
    list_display = ('file_preview', 'name', 'person', 'category', 'ttype', 'other')
    readonly_fields = ('file_preview',)
    list_filter = ('person', 'category', 'ttype')
    search_fields = ['name', 'person__name__icontains', 'category__name__icontains', 'ttype__name__icontains', 'other__name__icontains']

    form = DocumentAdminForm

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
        uploaded_files = request.FILES.getlist('file')

        pdf_writer = PyPDF2.PdfWriter()
        for uploaded_file in uploaded_files:

            images = []
            if uploaded_file.name.endswith('.pdf'):
                pdf = pdfium.PdfDocument(uploaded_file.read())
                pdf.init_forms()

                for page in pdf:
                    bitmap = page.render(scale=5, rotation=0, draw_annots=True)
                    pil_image = bitmap.to_pil()
                    images.append(pil_image)
            else:
                images = [Image.open(uploaded_file)]

            for image in images:
                config = "--oem 1 --psm 6 -l eng+fra+por"
                page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf', config=config)
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(page))
                pdf_writer.add_page(pdf_reader.pages[0])
        output_file = io.BytesIO()
        pdf_writer.write(output_file)

        obj.file.save('.'.join(uploaded_file.name.split('.')[:-1]) + '.pdf', output_file)
        super().save_model(request, obj, form, change)

    def get_person(self, obj):
        return obj.person.name if obj.person else '-'
    get_person.short_description = 'Person'

    def get_category(self, obj):
        return obj.category.name if obj.category else '-'
    get_category.short_description = 'Category'

    def get_type(self, obj):
        return obj.ttype.name if obj.ttype else '-'
    get_type.short_description = 'Type'

    def get_other(self, obj):
        return obj.other.name if obj.other else '-'
    get_type.short_description = 'Other'


def download_dossier_pdf(modeladmin, request, queryset):
    pdf_writer = PdfWriter()

    for dossier in queryset:
        documents = Document.objects.filter(dossiers=dossier)
        for document in documents:
            pdf_reader = PdfReader(document.file)
            for page in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page])

    output_buffer = io.BytesIO()
    pdf_writer.write(output_buffer)

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
admin.site.register(Person)
admin.site.register(Category)
admin.site.register(TType)
admin.site.register(Other)
