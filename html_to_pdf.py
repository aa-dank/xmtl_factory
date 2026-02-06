import sys, subprocess
from pathlib import Path
from pypdf import PdfWriter

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
HTML_FILES = [
    "output_page1.html",
    "output_page2.html",
    "output_page3.html",
]

'''from weasyprint import HTML
def convert(input_file, output_file):
    HTML(input_file).write_pdf(output_file)
    print(f"Converted '{input_file}' to '{output_file}'")
'''

def convert_edge(input_html, output_pdf_name):
    input_path = Path(input_html).resolve()
    output_dir = Path(output_pdf_name).resolve() #seperate folder for output pdf files

    subprocess.run([
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={output_dir}",
        f"file:///{input_path.as_posix()}"
    ], check=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL)

    print(f"Converted '{input_html}' → '{output_pdf_name}'")
    return output_dir

def main(final_pdf_name):
    missing = [f for f in HTML_FILES if not Path(f).exists()]
    if missing:
        sys.exit(f"Missing HTML files: {missing}")

    pdf_paths = []
    for html in HTML_FILES:
        pdf_name = Path(html).with_suffix(".pdf").name
        pdf_paths.append(convert_edge(html, pdf_name))

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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python html_to_pdf.py <output.pdf>")
        sys.exit(1)

    main(sys.argv[1])
