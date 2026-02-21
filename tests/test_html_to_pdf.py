"""Tests for html_to_pdf functions.

pdfkit.from_file and PdfWriter are mocked so no real PDF conversion is needed.
"""
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
import html_to_pdf


# ---------------------------------------------------------------------------
# convert_html
# ---------------------------------------------------------------------------

class TestConvertHtml:
    def test_calls_pdfkit_from_file(self, tmp_path):
        html_file = tmp_path / "page.html"
        html_file.write_text("<html></html>")
        pdf_out = tmp_path / "page.pdf"

        with patch("html_to_pdf.pdfkit.from_file") as mock_from_file, \
             patch("html_to_pdf._wkhtmltopdf_config", return_value=MagicMock()):
            html_to_pdf.convert_html(str(html_file), str(pdf_out))

        mock_from_file.assert_called_once()
        args, _ = mock_from_file.call_args
        assert args[0] == str(html_file.resolve())
        assert args[1] == str(pdf_out.resolve())

    def test_returns_resolved_output_path(self, tmp_path):
        html_file = tmp_path / "page.html"
        html_file.write_text("<html></html>")
        pdf_out = tmp_path / "page.pdf"

        with patch("html_to_pdf.pdfkit.from_file"), \
             patch("html_to_pdf._wkhtmltopdf_config", return_value=MagicMock()):
            result = html_to_pdf.convert_html(str(html_file), str(pdf_out))

        assert result == pdf_out.resolve()


# ---------------------------------------------------------------------------
# create_final_pdf
# ---------------------------------------------------------------------------

class TestCreateFinalPdf:
    def _make_html_files(self, tmp_path, count=2):
        paths = []
        for i in range(1, count + 1):
            p = tmp_path / f"output_page{i}.html"
            p.write_text(f"<html>page{i}</html>")
            paths.append(str(p))
        return paths

    def test_exits_when_html_file_missing(self, tmp_path):
        with pytest.raises(SystemExit):
            html_to_pdf.create_final_pdf("out.pdf", [str(tmp_path / "missing.html")])

    def test_calls_convert_html_for_each_html_file(self, tmp_path):
        html_files = self._make_html_files(tmp_path, count=2)

        fake_pdfs = [tmp_path / f"page{i}.pdf" for i in range(1, 3)]
        for p in fake_pdfs:
            p.write_bytes(b"%PDF-stub")

        mock_writer = MagicMock()
        # Make the context manager work for the final open() call
        mock_writer.__enter__ = MagicMock(return_value=mock_writer)
        mock_writer.__exit__ = MagicMock(return_value=False)

        convert_calls = iter(fake_pdfs)

        with patch("html_to_pdf.convert_html", side_effect=lambda h, p: next(convert_calls)) as mock_convert, \
             patch("html_to_pdf.PdfWriter", return_value=mock_writer), \
             patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock(return_value=False)))):
            html_to_pdf.create_final_pdf(str(tmp_path / "final.pdf"), html_files)

        assert mock_convert.call_count == 2

    def test_pdf_writer_append_called_for_each_pdf(self, tmp_path):
        html_files = self._make_html_files(tmp_path, count=2)
        fake_pdfs = [tmp_path / f"page{i}.pdf" for i in range(1, 3)]
        for p in fake_pdfs:
            p.write_bytes(b"%PDF-stub")

        mock_writer = MagicMock()
        convert_iter = iter(fake_pdfs)

        with patch("html_to_pdf.convert_html", side_effect=lambda h, p: next(convert_iter)), \
             patch("html_to_pdf.PdfWriter", return_value=mock_writer), \
             patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock(return_value=False)))):
            html_to_pdf.create_final_pdf(str(tmp_path / "final.pdf"), html_files)

        assert mock_writer.append.call_count == 2
