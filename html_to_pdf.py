import os
import shutil
import subprocess
import sys
from pathlib import Path

from pypdf import PdfWriter


def _edge_paths_from_registry():
    if not sys.platform.startswith("win"):
        return []

    try:
        import winreg
    except ImportError:
        return []

    subkeys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
    ]
    hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]

    found_paths = []
    for hive in hives:
        for subkey in subkeys:
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    value, _ = winreg.QueryValueEx(key, None)
                    if value:
                        found_paths.append(Path(value))
            except OSError:
                continue
    return found_paths


def discover_edge_path():
    env_path = os.environ.get("EDGE_PATH")
    candidates = []
    if env_path:
        candidates.append(Path(env_path))

    which_path = shutil.which("msedge") or shutil.which("msedge.exe")
    if which_path:
        candidates.append(Path(which_path))

    candidates.extend(_edge_paths_from_registry())

    candidates.extend(
        [
            Path(os.environ.get("ProgramFiles(x86)", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            Path(os.environ.get("ProgramFiles", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        ]
    )

    seen = set()
    for candidate in candidates:
        if not candidate:
            continue
        resolved = candidate.expanduser().resolve(strict=False)
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file():
            return resolved

    raise RuntimeError(
        "Microsoft Edge executable was not detected. "
        "Set EDGE_PATH or install Edge in a standard location."
    )


def convert_html(input_html, output_pdf_name, edge_path):
    input_path = Path(input_html).resolve()
    output_path = Path(output_pdf_name).resolve()

    if not input_path.exists():
        raise RuntimeError(f"Missing HTML input file: {input_html}")

    try:
        subprocess.run(
            [
                str(edge_path),
                "--headless=new",
                "--disable-gpu",
                "--allow-file-access-from-files",
                "--print-to-pdf-no-header",
                f"--print-to-pdf={output_path}",
                input_path.as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Edge PDF conversion timed out for '{input_html}'") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Edge PDF conversion failed for '{input_html}'") from exc

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError(f"Edge did not produce a valid PDF for '{input_html}'")

    print(f"Converted '{input_html}' → '{output_pdf_name}'")
    return output_path

# converts each html file to a pdf and merges them into a single final pdf
def create_final_pdf(final_pdf_name, HTML_FILES):
    edge_path = discover_edge_path()

    missing = [f for f in HTML_FILES if not Path(f).exists()]
    if missing:
        sys.exit(f"Missing HTML files: {missing}")

    pdf_paths = []
    for html in HTML_FILES:
        pdf_name = Path(html).with_suffix(".pdf").name
        pdf_paths.append(convert_html(html, pdf_name, edge_path))

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

    print(f"\nFinal combined PDF created:", end=" ")
    print(final_path.resolve())
