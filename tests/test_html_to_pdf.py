"""Tests for html_to_pdf functions.

Edge path discovery and subprocess-based conversion are mocked.
"""
from pathlib import Path
import subprocess
from unittest.mock import MagicMock, patch

import pytest
import html_to_pdf


# ---------------------------------------------------------------------------
# discover_edge_path
# ---------------------------------------------------------------------------

class TestDiscoverEdgePath:
    def test_uses_edge_path_env_when_valid(self, tmp_path, monkeypatch):
        edge_exe = tmp_path / "msedge.exe"
        edge_exe.write_text("edge")

        monkeypatch.setenv("EDGE_PATH", str(edge_exe))
        monkeypatch.setattr(html_to_pdf.shutil, "which", lambda *_: None)
        monkeypatch.setattr(html_to_pdf, "_edge_paths_from_registry", lambda: [])
        monkeypatch.setenv("ProgramFiles(x86)", str(tmp_path / "missing_pf86"))
        monkeypatch.setenv("ProgramFiles", str(tmp_path / "missing_pf"))
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "missing_local"))

        assert html_to_pdf.discover_edge_path() == edge_exe.resolve()

    def test_raises_when_edge_not_detected(self, tmp_path, monkeypatch):
        monkeypatch.delenv("EDGE_PATH", raising=False)
        monkeypatch.setattr(html_to_pdf.shutil, "which", lambda *_: None)
        monkeypatch.setattr(html_to_pdf, "_edge_paths_from_registry", lambda: [])
        monkeypatch.setenv("ProgramFiles(x86)", str(tmp_path / "missing_pf86"))
        monkeypatch.setenv("ProgramFiles", str(tmp_path / "missing_pf"))
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "missing_local"))

        with pytest.raises(RuntimeError, match="Edge executable was not detected"):
            html_to_pdf.discover_edge_path()


# ---------------------------------------------------------------------------
# convert_html
# ---------------------------------------------------------------------------

class TestConvertHtml:
    def test_calls_edge_subprocess(self, tmp_path):
        html_file = tmp_path / "page.html"
        html_file.write_text("<html></html>")
        pdf_out = tmp_path / "page.pdf"
        edge_exe = tmp_path / "msedge.exe"
        edge_exe.write_text("edge")

        def fake_run(*args, **kwargs):
            pdf_out.write_bytes(b"%PDF-1.7")

        with patch("html_to_pdf.subprocess.run", side_effect=fake_run) as mock_run:
            result = html_to_pdf.convert_html(str(html_file), str(pdf_out), edge_exe)

        assert result == pdf_out.resolve()
        command = mock_run.call_args.args[0]
        assert command[0] == str(edge_exe)

    def test_returns_resolved_output_path(self, tmp_path):
        html_file = tmp_path / "page.html"
        html_file.write_text("<html></html>")
        pdf_out = tmp_path / "page.pdf"
        edge_exe = tmp_path / "msedge.exe"
        edge_exe.write_text("edge")

        with patch("html_to_pdf.subprocess.run", side_effect=lambda *a, **k: pdf_out.write_bytes(b"%PDF-1.7")):
            result = html_to_pdf.convert_html(str(html_file), str(pdf_out), edge_exe)

        assert result == pdf_out.resolve()

    def test_raises_runtime_error_on_edge_failure(self, tmp_path):
        html_file = tmp_path / "page.html"
        html_file.write_text("<html></html>")
        edge_exe = tmp_path / "msedge.exe"
        edge_exe.write_text("edge")

        with patch("html_to_pdf.subprocess.run", side_effect=subprocess.CalledProcessError(1, "msedge")):
            with pytest.raises(RuntimeError, match="Edge PDF conversion failed"):
                html_to_pdf.convert_html(str(html_file), str(tmp_path / "out.pdf"), edge_exe)

    def test_raises_runtime_error_when_no_output_pdf_created(self, tmp_path):
        html_file = tmp_path / "page.html"
        html_file.write_text("<html></html>")
        edge_exe = tmp_path / "msedge.exe"
        edge_exe.write_text("edge")

        with patch("html_to_pdf.subprocess.run", return_value=None):
            with pytest.raises(RuntimeError, match="did not produce a valid PDF"):
                html_to_pdf.convert_html(str(html_file), str(tmp_path / "out.pdf"), edge_exe)


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
        with patch("html_to_pdf.discover_edge_path", return_value=tmp_path / "msedge.exe"):
            with pytest.raises(SystemExit):
                html_to_pdf.create_final_pdf("out.pdf", [str(tmp_path / "missing.html")])

    def test_fails_quickly_when_edge_is_not_detected(self, tmp_path):
        html_file = tmp_path / "output_page1.html"
        html_file.write_text("<html>page1</html>")

        with patch("html_to_pdf.discover_edge_path", side_effect=RuntimeError("Edge missing")), \
             patch("html_to_pdf.convert_html") as mock_convert:
            with pytest.raises(RuntimeError, match="Edge missing"):
                html_to_pdf.create_final_pdf(str(tmp_path / "final.pdf"), [str(html_file)])

        mock_convert.assert_not_called()

    def test_calls_convert_html_for_each_html_file(self, tmp_path):
        html_files = self._make_html_files(tmp_path, count=2)
        edge_exe = tmp_path / "msedge.exe"
        edge_exe.write_text("edge")

        fake_pdfs = [tmp_path / f"page{i}.pdf" for i in range(1, 3)]
        for p in fake_pdfs:
            p.write_bytes(b"%PDF-stub")

        mock_writer = MagicMock()

        convert_calls = iter(fake_pdfs)

        with patch("html_to_pdf.discover_edge_path", return_value=edge_exe), \
             patch("html_to_pdf.convert_html", side_effect=lambda h, p, e: next(convert_calls)) as mock_convert, \
             patch("html_to_pdf.PdfWriter", return_value=mock_writer):
            html_to_pdf.create_final_pdf(str(tmp_path / "final.pdf"), html_files)

        assert mock_convert.call_count == 2
        assert all(call_args.args[2] == edge_exe for call_args in mock_convert.call_args_list)

    def test_pdf_writer_append_called_for_each_pdf(self, tmp_path):
        html_files = self._make_html_files(tmp_path, count=2)
        edge_exe = tmp_path / "msedge.exe"
        edge_exe.write_text("edge")

        fake_pdfs = [tmp_path / f"page{i}.pdf" for i in range(1, 3)]
        for p in fake_pdfs:
            p.write_bytes(b"%PDF-stub")

        mock_writer = MagicMock()
        convert_iter = iter(fake_pdfs)

        with patch("html_to_pdf.discover_edge_path", return_value=edge_exe), \
             patch("html_to_pdf.convert_html", side_effect=lambda h, p, e: next(convert_iter)), \
             patch("html_to_pdf.PdfWriter", return_value=mock_writer):
            html_to_pdf.create_final_pdf(str(tmp_path / "final.pdf"), html_files)

        assert mock_writer.append.call_count == 2
