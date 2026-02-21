# PyInstaller Bundling Research — xmtl-factory

**Date:** 2026-02-20  
**Context:** Evaluating options for distributing xmtl-factory as a self-contained executable for both Windows and macOS, replacing the non-cooperative `xhtml2pdf` HTML-to-PDF backend.

---

## Problem: xhtml2pdf is not cooperating

`xhtml2pdf` (via `pisa.CreatePDF`) was the original HTML-to-PDF converter. It has known issues:

- Limited CSS support (no flexbox, no grid, dated rendering engine)
- Brittle resource resolution — relative `src` and `href` paths break when the working directory is not the project root, which is guaranteed to happen inside a PyInstaller `_MEIPASS` temp directory
- Poor PyInstaller compatibility: its internal resource loading uses paths that don't survive freezing without custom hooks

---

## Library Alternatives Researched

### 1. pdfkit + wkhtmltopdf ✅ (chosen)

| Property | Detail |
|---|---|
| Approach | Python wrapper around `wkhtmltopdf` — a standalone C++ binary |
| CSS support | Full WebKit rendering engine (same engine as old Safari) |
| PyInstaller | Excellent — bundle `wkhtmltopdf.exe` / `wkhtmltopdf` as a binary data file |
| Maintenance | `wkhtmltopdf` archived in 2023 but binaries are stable; `pdfkit` wrapper still maintained |
| Bundle size impact | ~15 MB for the binary |
| Windows | Yes — official `.exe` installer at wkhtmltopdf.org |
| macOS | Yes — `brew install wkhtmltopdf` |

**Why chosen:** The cleanest PyInstaller story. The binary can be dropped in the project root and bundled as a PyInstaller `binaries` entry. No system DLL dependencies, no GTK runtime, no browser engine download step.

---

### 2. WeasyPrint ❌ (not chosen)

| Property | Detail |
|---|---|
| Approach | Pure-Python CSS layout engine using Pango/Cairo for rendering |
| CSS support | Excellent — best Paged Media / `@page` CSS support of any Python option |
| PyInstaller | Painful on Windows — requires GTK runtime DLLs (Pango, Cairo, GDK) which must be located and bundled manually via MSYS2 |
| Maintenance | Actively maintained (v68 released Feb 2026) |

**Why not chosen:** The Windows GTK dependency chain is a significant bundling burden. Good macOS story via Homebrew, but the Windows path is complex enough to be a support problem.

---

### 3. Playwright (Chromium) ❌ (not chosen for now)

| Property | Detail |
|---|---|
| Approach | Full Chromium browser automation; `page.pdf()` produces pixel-perfect output |
| CSS support | Perfect — actual Chrome rendering |
| PyInstaller | Possible but complex; Chromium must be pre-installed or bundled separately |
| Bundle size impact | ~150–300 MB for Chromium |
| Maintenance | Actively maintained by Microsoft |

**Why not chosen:** Bundle size is prohibitive for a CLI tool. Also requires `playwright install chromium` as a separate step, complicating distribution. Best choice if CSS fidelity becomes a priority later.

---

## PyInstaller Compatibility Issues Found in Codebase

When a PyInstaller one-file executable runs, Python files are extracted to a temporary directory (`sys._MEIPASS`). The process working directory (`cwd`) is *not* `_MEIPASS` — it is wherever the user ran the executable from. This breaks any code that uses bare relative paths to find bundled assets.

### Issues identified and fixed:

#### 1. `custom_fill.py` — `FileSystemLoader` used a bare relative path
```python
# Before (breaks when frozen):
env = Environment(loader=FileSystemLoader('templates'))

# After:
env = Environment(loader=FileSystemLoader(str(resource_path('templates'))))
```

#### 2. `custom_fill.py` — Template `render()` calls used relative `src`/`href` in HTML
`wkhtmltopdf` reads the rendered HTML from a temp file and resolves relative URLs against it — not against `_MEIPASS`. A `file://` URI base is injected as a Jinja2 variable so templates can build absolute URIs.

```python
resource_dir = resource_path('.').as_uri()  # e.g. file:///tmp/_MEIxxxxxx
template_1.render(**dictionary, resource_dir=resource_dir)
```

Templates updated accordingly:
```html
<!-- Before -->
<link rel="stylesheet" href="styles.css">
<img src="images/UCSC Emblem.png" ...>

<!-- After -->
<link rel="stylesheet" href="{{ resource_dir }}/styles.css">
<img src="{{ resource_dir }}/images/UCSC Emblem.png" ...>
```

#### 3. `submittal_cli.py` — `xmtl_templates.yaml` opened with a bare filename
```python
# Before:
build = XmtlBuild.from_yaml("xmtl_templates.yaml", default_key)

# After:
build = XmtlBuild.from_yaml(resource_path("xmtl_templates.yaml"), default_key)
```

### `resource_path()` helper (added to all three modules)
```python
def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
    return base / relative
```
- In frozen mode: resolves against `sys._MEIPASS` (the extraction temp dir)
- In dev mode: resolves against the directory containing the source file

---

## Files Changed

| File | Change |
|---|---|
| `html_to_pdf.py` | Replaced `xhtml2pdf`/`pisa` with `pdfkit`; added `resource_path()` and `_wkhtmltopdf_config()` |
| `custom_fill.py` | Added `resource_path()`; fixed `FileSystemLoader`; inject `resource_dir` into templates |
| `submittal_cli.py` | Added `resource_path()`; fixed yaml path lookup |
| `templates/Page1.HTML` | `styles.css` and image `src` now use `{{ resource_dir }}/...` |
| `templates/Page2.HTML` | Same |
| `templates/Page3.HTML` | Same |
| `pyproject.toml` | Replaced `xhtml2pdf>=0.2.16` with `pdfkit>=1.0.0` |
| `xmtl_factory.spec` | New PyInstaller spec file |
| `tests/test_html_to_pdf.py` | Updated mocks from `pisa.CreatePDF` to `pdfkit.from_file` |

---

## Build Instructions

### Prerequisites (per platform)

**Windows:**
```
# Download wkhtmltopdf.exe installer from https://wkhtmltopdf.org/downloads.html
# After install, copy the binary to the project root:
copy "C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe" .
```

**macOS:**
```bash
brew install wkhtmltopdf
cp $(which wkhtmltopdf) .
```

### Build
```bash
pip install pdfkit pyinstaller
pyinstaller xmtl_factory.spec
# Output: dist/xmtl-factory  (or dist/xmtl-factory.exe on Windows)
```

> **Note:** PyInstaller cannot cross-compile. Run on Windows to produce a `.exe`; run on macOS to produce a macOS binary. GitHub Actions can automate both via a matrix build.

---

## Open Questions / Future Work

- [ ] Validate that wkhtmltopdf renders the checkboxes and CSS layout correctly (WebKit vs. the old xhtml2pdf renderer may produce different output)
- [ ] Consider a GitHub Actions CI workflow with Windows + macOS runners to automate builds and attach artifacts to releases
- [ ] Evaluate whether `--onefile` vs `--onedir` is preferable (onefile is simpler to distribute; onedir starts faster)
- [ ] wkhtmltopdf is archived upstream — monitor if a maintained fork becomes the standard
