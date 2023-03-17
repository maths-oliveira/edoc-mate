import pytesseract
from pdf2image import convert_from_path
import PyPDF2
import io


def convert_pdf_to_searchable_pdf(input_path, output_path):
    images = convert_from_path(input_path)
    convert_images_to_searchable_pdf(images, output_path)


def convert_images_to_searchable_pdf(images, output_path):
    pdf_writer = PyPDF2.PdfFileWriter()
    for image in images:
        page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
        pdf = PyPDF2.PdfReader(io.BytesIO(page))
        pdf_writer.add_page(pdf.pages[0])
    with open(output_path, "wb") as f:
        pdf_writer.write(f)
