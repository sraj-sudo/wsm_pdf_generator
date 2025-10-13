"""
pdf_generator_xhtml2pdf.py

Lightweight PDF generator using xhtml2pdf (pisa).
Designed for simple HTML templates (no heavy CSS/JS).
Drop this file into your project, replace existing pdf generation calls,
and call generate_pdf(...) to obtain PDF bytes.

Requirements:
    pip install xhtml2pdf

Functions:
- convert_html_to_pdf(html: str) -> Optional[bytes]
- generate_plain_pdf(project_data: dict) -> bytes  (ReportLab fallback if available)
- generate_pdf(template_name=None, project_data=None, html_string=None) -> bytes
"""

import io
import os
import traceback
from typing import Optional, Any

# Try to import xhtml2pdf (pisa). If missing, instruct the user.
try:
    from xhtml2pdf import pisa  # type: ignore
    HAVE_XHTML2PDF = True
except Exception:
    pisa = None  # type: ignore
    HAVE_XHTML2PDF = False

# Optional ReportLab fallback for very basic PDFs (not required but helpful)
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    HAVE_REPORTLAB = True
except Exception:
    HAVE_REPORTLAB = False


def _write_debug_html(source_html: str) -> str:
    """Write debug HTML for inspection; returns the path (or empty string)."""
    try:
        path = os.path.abspath("wsm_debug.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(source_html)
        return path
    except Exception:
        return ""


def convert_html_to_pdf(source_html: str) -> Optional[bytes]:
    """
    Convert HTML to PDF using xhtml2pdf (pisa).
    Returns PDF bytes on success, or None on failure.
    """
    if not HAVE_XHTML2PDF:
        raise RuntimeError("xhtml2pdf (pisa) is not installed. Install with: pip install xhtml2pdf")

    # Write debug HTML for inspection (helps debugging templates)
    dbg = _write_debug_html(source_html)
    if dbg:
        print(f"[pdf_generator] Debug HTML written to: {dbg}")

    try:
        result = io.BytesIO()
        src = io.BytesIO(source_html.encode("utf-8"))
        pisa_status = pisa.CreatePDF(src, dest=result, encoding="utf-8")

        # Optionally write pisa log
        try:
            log_text = getattr(pisa_status, "log", "")
            log_path = os.path.abspath("wsm_pisa_log.txt")
            with open(log_path, "w", encoding="utf-8") as lf:
                lf.write(log_text)
            print(f"[pdf_generator] pisa log written to: {log_path}")
        except Exception:
            pass

        if not getattr(pisa_status, "err", 1):
            result.seek(0)
            return result.read()
        else:
            print("[pdf_generator] xhtml2pdf reported errors. See wsm_pisa_log.txt for details.")
            return None
    except Exception as e:
        print(f"[pdf_generator] Exception during xhtml2pdf conversion: {e}")
        print(traceback.format_exc())
        return None


def generate_plain_pdf(project_data: Any) -> bytes:
    """
    Simple plain-text PDF fallback using ReportLab (if available).
    If ReportLab is not installed, this will raise an error.
    """
    if not HAVE_REPORTLAB:
        raise RuntimeError("ReportLab is not installed. Install with: pip install reportlab")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin
    line_height = 14

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Plain PDF Fallback")
    y -= 30
    c.setFont("Helvetica", 10)

    if isinstance(project_data, dict):
        for k, v in project_data.items():
            text = f"{k}: {v}"
            # naive wrapping
            if len(text) > 120:
                text = text[:120] + " ..."
            if y < margin + line_height:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 10)
            c.drawString(margin, y, text)
            y -= line_height
    else:
        for line in str(project_data).splitlines():
            if y < margin + line_height:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, line)
            y -= line_height

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_pdf(template_name: Optional[str] = None,
                 project_data: Optional[dict] = None,
                 html_string: Optional[str] = None) -> bytes:
    """
    Generate a PDF. Priority:
      1. If html_string provided -> convert it.
      2. Else if template_name provided -> try to render using template_manager.get_template_content
      3. If conversion fails -> fallback to plain PDF (ReportLab) if available.
    Returns PDF bytes or raises RuntimeError if all methods fail.
    """
    html = None

    if html_string:
        html = html_string
    elif template_name:
        try:
            import template_manager  # type: ignore
            html = template_manager.get_template_content(template_name, project_data or {})
        except Exception as e:
            print(f"[pdf_generator] Could not render template {template_name}: {e}")
            print(traceback.format_exc())
            html = None

    if html:
        pdf = convert_html_to_pdf(html)
        if pdf:
            return pdf
        else:
            print("[pdf_generator] HTML conversion failed; falling back to plain PDF if available.")

    # Fallback
    try:
        return generate_plain_pdf(project_data or {})
    except Exception as e:
        print(f"[pdf_generator] Plain PDF generation failed: {e}")
        print(traceback.format_exc())
        raise RuntimeError("All PDF generation attempts failed.") from e


if __name__ == "__main__":
    # Small test - writes test_output.pdf using a tiny HTML sample
    sample_html = """
    <html>
      <head><meta charset="utf-8"><title>Test</title></head>
      <body>
        <h1>Test PDF (xhtml2pdf)</h1>
        <p>Generated for testing.</p>
      </body>
    </html>
    """
    try:
        pdf_bytes = generate_pdf(html_string=sample_html)
        out = os.path.abspath("test_output_xhtml2pdf.pdf")
        with open(out, "wb") as f:
            f.write(pdf_bytes)
        print(f"Wrote test PDF to: {out}")
    except Exception as e:
        print("Test failed:", e)
