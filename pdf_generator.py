
"""
pdf_generator.py

Robust HTML -> PDF generator module for Streamlit / Flask apps.

Features:
- Prefer WeasyPrint (best CSS fidelity) if available.
- Fallback to xhtml2pdf if WeasyPrint is not installed.
- If HTML conversion fails, falls back to a simple ReportLab PDF generator (plain text).
- Writes debug outputs:
  - wsm_debug.html   -> the final HTML that was passed to the converter
  - wsm_pisa_log.txt -> xhtml2pdf log (when used)
- Provides:
    - convert_html_to_pdf(source_html) -> bytes | None
    - generate_pdf(template_name=None, project_data=None, html_string=None) -> bytes | None
    - generate_plain_pdf(project_data) -> bytes (ReportLab text fallback)
- Safe to drop into your existing project and call from Streamlit.

Notes:
- WeasyPrint requires system libraries (cairo, pango, gdk-pixbuf). If you can install them, WeasyPrint will produce PDF output closest to a browser rendering.
- If you can't install system libraries, xhtml2pdf is a pure-Python fallback but has limited CSS support.
- If neither HTML engine is available, ReportLab creates a simple, readable PDF as a last resort.
"""

import io
import os
import traceback
from datetime import datetime
from typing import Optional, Any

# Try optional libraries
try:
    from weasyprint import HTML  # type: ignore
    HAVE_WEASY = True
except Exception:
    HAVE_WEASY = False

try:
    from xhtml2pdf import pisa  # type: ignore
    HAVE_XHTML2PDF = True
except Exception:
    HAVE_XHTML2PDF = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    HAVE_REPORTLAB = True
except Exception:
    HAVE_REPORTLAB = False


def _write_debug_html(source_html: str) -> str:
    """Write debug HTML file so you can open it in a browser and inspect rendering."""
    try:
        debug_path = os.path.abspath("wsm_debug.html")
        with open(debug_path, "w", encoding="utf-8") as fh:
            fh.write(source_html)
        return debug_path
    except Exception:
        return ""


def _write_pisa_log(pisa_status) -> str:
    """Write pisa log (if present) to a debug file."""
    try:
        log_text = getattr(pisa_status, "log", "")
        log_path = os.path.abspath("wsm_pisa_log.txt")
        with open(log_path, "w", encoding="utf-8") as lf:
            lf.write(log_text)
        return log_path
    except Exception:
        return ""


def convert_html_to_pdf(source_html: str) -> Optional[bytes]:
    """
    Convert HTML to PDF bytes.
    - Tries WeasyPrint first (if available).
    - Falls back to xhtml2pdf (pisa) if WeasyPrint missing.
    - Writes debug HTML and pisa log for inspection.
    Returns PDF bytes on success, or None on failure.
    """
    # Always write debug HTML (helps to inspect what was actually rendered)
    debug_html_path = _write_debug_html(source_html)
    if debug_html_path:
        print(f"[pdf_generator] Wrote debug HTML to: {debug_html_path}")

    # OPTION 1: WeasyPrint (recommended if available)
    if HAVE_WEASY:
        try:
            print("[pdf_generator] Trying WeasyPrint for conversion...")
            pdf_bytes = HTML(string=source_html).write_pdf()
            if pdf_bytes:
                print("[pdf_generator] WeasyPrint succeeded.")
                return pdf_bytes
            else:
                print("[pdf_generator] WeasyPrint returned empty result.")
        except Exception as e:
            print(f"[pdf_generator] WeasyPrint exception: {e}")
            print(traceback.format_exc())

    # OPTION 2: xhtml2pdf (pisa)
    if HAVE_XHTML2PDF:
        try:
            print("[pdf_generator] Trying xhtml2pdf (pisa) for conversion...")
            result_file = io.BytesIO()
            # Feed bytes to CreatePDF for better compatibility
            src = io.BytesIO(source_html.encode("utf-8"))
            pisa_status = pisa.CreatePDF(src, dest=result_file, encoding="utf-8")

            # write pisa log for debugging
            log_path = _write_pisa_log(pisa_status)
            if log_path:
                print(f"[pdf_generator] pisa log written to: {log_path}")

            if not getattr(pisa_status, "err", 1):
                result_file.seek(0)
                print("[pdf_generator] xhtml2pdf succeeded.")
                return result_file.read()
            else:
                print("[pdf_generator] xhtml2pdf reported an error. See log for details.")
                # fallthrough to fallback
        except Exception as e:
            print(f"[pdf_generator] xhtml2pdf exception: {e}")
            print(traceback.format_exc())

    # If conversion failed or no engines available, return None
    print("[pdf_generator] HTML -> PDF conversion failed with available engines.")
    return None


def generate_plain_pdf(project_data: Any) -> bytes:
    """
    Generate a simple text-based PDF as a fallback using ReportLab.
    The function will attempt to create a readable PDF containing project_data keys/values.
    """
    if not HAVE_REPORTLAB:
        raise RuntimeError("ReportLab is not installed; cannot create a plain PDF fallback. "
                           "Install reportlab with `pip install reportlab` or enable HTML engines.")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin = 50
    y = height - margin
    line_height = 14

    # Draw header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Project WSM (Plain PDF - Fallback)")
    y -= 30

    c.setFont("Helvetica", 10)
    # If project_data is dict-like, print each key/value on its own line
    if isinstance(project_data, dict):
        for k, v in project_data.items():
            # Convert value to single-line string (truncate if very long)
            val = str(v)
            # wrap long lines naively
            max_chars = 120
            if len(val) > max_chars:
                val = val[:max_chars] + " ..."

            line = f"{k}: {val}"
            # if running out of space, create new page
            if y < margin + line_height:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 10)
            c.drawString(margin, y, line)
            y -= line_height
    else:
        # just dump repr of project_data
        for chunk in str(project_data).splitlines():
            if y < margin + line_height:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 10)
            c.drawString(margin, y, chunk)
            y -= line_height

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_pdf(template_name: Optional[str] = None,
                 project_data: Optional[dict] = None,
                 html_string: Optional[str] = None) -> bytes:
    """
    High-level helper to generate a PDF.
    - If html_string is provided, it will be used directly.
    - Otherwise, if template_name is provided, this function will try to import
      template_manager.get_template_content(template_name, project_data)
      to render HTML, then convert it.
    - If HTML conversion fails, it falls back to generate_plain_pdf(project_data).
    Returns PDF bytes (always) or raises an error if all attempts fail.
    """
    html = None

    if html_string:
        html = html_string
    elif template_name:
        # Try to import template_manager from the project
        try:
            import template_manager  # type: ignore
            # template_manager should expose get_template_content(template_name, project_data)
            html = template_manager.get_template_content(template_name, project_data or {})
        except Exception as e:
            print(f"[pdf_generator] Could not render template via template_manager: {e}")
            print(traceback.format_exc())
            html = None

    # If we have HTML, attempt conversion
    if html:
        pdf_bytes = convert_html_to_pdf(html)
        if pdf_bytes:
            return pdf_bytes
        else:
            print("[pdf_generator] HTML conversion returned None; falling back to plain PDF.")

    # Fallback: attempt ReportLab plain PDF
    try:
        return generate_plain_pdf(project_data or {})
    except Exception as e:
        print(f"[pdf_generator] Plain PDF generation failed: {e}")
        print(traceback.format_exc())
        raise RuntimeError("All PDF generation methods failed.") from e


# If this module is executed directly, run a small self-test that writes a PDF to disk
if __name__ == "__main__":
    sample_html = """
    <html>
      <head><meta charset="utf-8"><title>Test PDF</title></head>
      <body><h1>PDF Generator Test</h1><p>Generated at: {}</p></body>
    </html>
    """.format(datetime.now().isoformat())

    print("Running standalone test...")
    pdf_bytes = generate_pdf(html_string=sample_html, project_data={"example": "data"})
    out_path = os.path.abspath("test_output.pdf")
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"Wrote test PDF to: {out_path}")
