from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return slug or "company"


def generate_cam_pdf(company_name: str, markdown_report: str, output_dir: Path) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"cam_report_{_safe_slug(company_name)}_{timestamp}.pdf"
    output_path = output_dir / file_name

    html = markdown2.markdown(markdown_report)
    lines = [line.strip() for line in html.split("\n") if line.strip()]

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("CAMH1", parent=styles["Heading1"], fontSize=18, spaceAfter=10)
    h2 = ParagraphStyle("CAMH2", parent=styles["Heading2"], fontSize=13, spaceBefore=8, spaceAfter=6)
    body = ParagraphStyle("CAMBody", parent=styles["BodyText"], fontSize=10, leading=14)

    story = []
    for line in lines:
        if line.startswith("<h1>") and line.endswith("</h1>"):
            story.append(Paragraph(line[4:-5], h1))
        elif line.startswith("<h2>") and line.endswith("</h2>"):
            story.append(Paragraph(line[4:-5], h2))
        else:
            text = re.sub(r"</?p>", "", line)
            text = re.sub(r"<br\s*/?>", "<br/>", text)
            story.append(Paragraph(text, body))
        story.append(Spacer(1, 6))

    doc = SimpleDocTemplate(str(output_path), pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    doc.build(story)

    return file_name
