import sys
import platform
from pathlib import Path
from pypdf import PdfWriter
import pdfkit


def resource_path(relative: str) -> Path:
    """Resolve a path relative to the app's resource directory.

    When running as a PyInstaller one-file executable, resources are extracted
    to a temporary directory stored in sys._MEIPASS. When running from source,
    resources are found relative to this file's directory.
    """
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
    return base / relative


def _wkhtmltopdf_config() -> pdfkit.configuration:
    """Return a pdfkit configuration pointing at the bundled wkhtmltopdf binary.

    Looks for a binary bundled alongside the app first (PyInstaller case), then
    falls back to whatever is on PATH (development / system install).
    """
    binary_name = 'wkhtmltopdf.exe' if platform.system() == 'Windows' else 'wkhtmltopdf'
    bundled = resource_path(binary_name)
    if bundled.exists():
        return pdfkit.configuration(wkhtmltopdf=str(bundled))
    # Fall back to system PATH — pdfkit will raise a clear error if missing
    return pdfkit.configuration()


_PDFKIT_OPTIONS = {
    'enable-local-file-access': None,   # allow file:// URIs in the HTML
    'quiet': '',                         # suppress wkhtmltopdf's verbose output
    'print-media-type': None,            # honour @media print CSS rules
}


def convert_html(input_html, output_pdf_name):
    input_path = Path(input_html).resolve()
    output_path = Path(output_pdf_name).resolve()

    pdfkit.from_file(
        str(input_path),
        str(output_path),
        configuration=_wkhtmltopdf_config(),
        options=_PDFKIT_OPTIONS,
    )

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
