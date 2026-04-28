import io
import json
from html import escape

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def build_html_report(session: dict) -> str:
    metadata = session["dataset_metadata"]
    chart_config = session["chart_config"]
    chart_json = chart_config if isinstance(chart_config, str) else json.dumps(chart_config)
    return f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>{escape(session["title"])}</title>
        <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
        <style>
          body {{ font-family: Inter, Arial, sans-serif; margin: 40px; color: #172033; }}
          .card {{ border: 1px solid #dbeafe; border-radius: 18px; padding: 24px; margin-bottom: 20px; }}
          h1 {{ color: #1d4ed8; }}
        </style>
      </head>
      <body>
        <h1>{escape(session["title"])}</h1>
        <div class="card">
          <h2>Question</h2>
          <p>{escape(session["question"])}</p>
          <h2>Selected Visualization</h2>
          <p>{escape(session["chart_type"].title())}</p>
          <h2>Generated Insight</h2>
          <p>{escape(session["insight"])}</p>
        </div>
        <div class="card">
          <h2>Dataset Summary</h2>
          <p>Rows: {metadata.get("row_count", "n/a")} | Columns: {metadata.get("column_count", "n/a")}</p>
          <p>Columns: {escape(", ".join(metadata.get("column_names", [])))}</p>
        </div>
        <div id="chart" class="card"></div>
        <script>
          const figure = {chart_json};
          Plotly.newPlot('chart', figure.data, figure.layout, {{ responsive: true }});
        </script>
      </body>
    </html>
    """


def build_pdf_report(session: dict) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    text = pdf.beginText(48, 740)
    text.setFont("Helvetica-Bold", 16)
    text.textLine(session["title"])
    text.setFont("Helvetica", 10)
    text.textLine("")
    for label, value in [
        ("Question", session["question"]),
        ("Chart", session["chart_type"].title()),
        ("Insight", session["insight"]),
        ("Rows", str(session["dataset_metadata"].get("row_count", "n/a"))),
        ("Columns", ", ".join(session["dataset_metadata"].get("column_names", []))),
    ]:
        text.textLine(f"{label}: {value[:95]}")
    text.textLine("")
    text.textLine("Chart image export is a TODO for the MVP PDF; HTML export embeds the interactive chart.")
    pdf.drawText(text)
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
