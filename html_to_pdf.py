import sys
from pathlib import Path
from pypdf import PdfWriter
from xhtml2pdf import pisa


def convert_html(input_html, output_pdf_name):
    input_path = Path(input_html).resolve()
    output_path = Path(output_pdf_name).resolve()

    with open(input_path, "r", encoding="utf-8") as source_file:
        html_content = source_file.read()

    with open(output_path, "wb") as dest_file:
        status = pisa.CreatePDF(html_content, dest=dest_file)

    if status.err:
        raise RuntimeError(f"xhtml2pdf conversion failed for '{input_html}'")

    print(f"Converted '{input_html}' → '{output_pdf_name}'")
    return output_path

# converts each html file to a pdf and merges them into a single final pdf
def create_final_pdf(final_pdf_name, HTML_FILES):
    missing = [f for f in HTML_FILES if not Path(f).exists()]
    if missing:
        sys.exit(f"Missing HTML files: {missing}")

    pdf_paths = []
    for html in HTML_FILES:
        pdf_name = Path(html).with_suffix(".pdf").name
        pdf_paths.append(convert_html(html, pdf_name))

    writer = PdfWriter()

    for pdf in pdf_paths:
        if pdf is None or not pdf.exists():
            raise RuntimeError(f"Missing PDF during merge: {pdf}")
        writer.append(str(pdf))

    final_path = Path(final_pdf_name).resolve()
    with open(final_path, "wb") as f:
        writer.write(f)

    # Delete temp PDFs
    for pdf in pdf_paths:
        pdf.unlink()

    print(f"\nFinal combined PDF created:")
    print(final_path.resolve())
