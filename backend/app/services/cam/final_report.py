from __future__ import annotations

from pathlib import Path
from textwrap import wrap
from typing import Any


def _fmt_currency(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"INR {value:,.2f}"
    return str(value or "N/A")


def _fmt_percent(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value * 100:.2f}%"
    return str(value or "N/A")


def _build_triangulation_rows(
    financial_metrics: dict[str, Any],
    secondary_research: dict[str, Any],
) -> list[list[str]]:
    """Return rows for the metric triangulation table (header + data)."""

    def _pos(flag: bool | None) -> str:
        if flag is True:
            return "Positive"
        if flag is False:
            return "Negative"
        return "Inconclusive"

    def _num_check(val: Any, threshold: float, above: bool = True) -> bool | None:
        if not isinstance(val, (int, float)):
            return None
        return (val >= threshold) if above else (val < threshold)

    sentiment = str(secondary_research.get("market_sentiment") or "N/A")
    sector = str(secondary_research.get("sector_outlook") or "N/A")
    legal = str(secondary_research.get("legal_risk") or "N/A")
    promoter = str(secondary_research.get("promoter_background") or "N/A")

    rev_growth = financial_metrics.get("revenue_growth")
    de_ratio = financial_metrics.get("debt_equity_ratio")
    ebitda_margin = financial_metrics.get("ebitda_margin")
    dscr = financial_metrics.get("dscr")

    return [
        ["Metric", "Extracted Value", "External Signal", "Decision Impact"],
        ["Revenue Growth", _fmt_percent(rev_growth), f"Sector: {sector[:28]}", _pos(_num_check(rev_growth, 0.0))],
        ["Debt / Equity Ratio", str(de_ratio) if de_ratio is not None else "N/A", "Favorable if < 2.5x", _pos(_num_check(de_ratio, 2.5, above=False))],
        ["EBITDA Margin", _fmt_percent(ebitda_margin), "Benchmark ~15%", _pos(_num_check(ebitda_margin, 0.15))],
        ["DSCR", f"{dscr:.2f}" if isinstance(dscr, (int, float)) else "N/A", "Min threshold 1.2x", _pos(_num_check(dscr, 1.2))],
        ["Legal Risk", legal[:32], "Litigation signals from research", _pos(None if legal == "N/A" else legal.lower() not in ("high", "medium"))],
        ["Market Sentiment", sentiment[:32], "News & sector pulse", _pos(None if sentiment == "N/A" else sentiment.lower() not in ("negative", "bearish"))],
        ["Promoter Quality", promoter[:32], "Background check", _pos(None if promoter in ("N/A", "") else "adverse" not in promoter.lower())],
    ]


def _build_factor_weights(risk_decision: dict[str, Any]) -> list[list[str]]:
    """Return rows for the weighted factor analysis table (header + data)."""
    FACTORS = [
        ("Financial Health (Revenue, EBITDA, Margins)", 30),
        ("Leverage & Debt Coverage (D/E, DSCR)", 25),
        ("External Intelligence (Legal, Sentiment, Sector)", 20),
        ("Management & Promoter Quality", 15),
        ("Market Position & Growth", 10),
    ]

    risk_score = risk_decision.get("risk_score")
    confidence = risk_decision.get("confidence")

    score_frac = 0.5
    if isinstance(risk_score, str) and "/" in risk_score:
        try:
            num, den = risk_score.split("/", 1)
            score_frac = float(num.strip()) / float(den.strip())
        except (ValueError, ZeroDivisionError):
            pass
    elif isinstance(risk_score, (int, float)):
        score_frac = float(risk_score) / 100.0 if risk_score > 1 else float(risk_score)

    conf_pct = f"{round(float(confidence) * 100)}%" if isinstance(confidence, (int, float)) else "75%"

    rows: list[list[str]] = [["Factor", "Weight", "Est. Score (/10)", "Contribution"]]
    for factor, weight in FACTORS:
        est = round(score_frac * 10, 1)
        contrib = round(weight * score_frac, 1)
        rows.append([factor[:46], f"{weight}%", str(est), f"{contrib}%"])
    rows.append(["Model Overall Confidence", "\u2014", str(risk_score or "N/A"), conf_pct])
    return rows


def build_final_report_markdown(
    company_overview: dict[str, Any],
    loan_details: dict[str, Any],
    financial_metrics: dict[str, Any],
    risk_decision: dict[str, Any],
    secondary_research: dict[str, Any],
    swot_analysis: dict[str, Any],
) -> str:
    strengths = swot_analysis.get("strengths") or []
    weaknesses = swot_analysis.get("weaknesses") or []
    opportunities = swot_analysis.get("opportunities") or []
    threats = swot_analysis.get("threats") or []

    reasoning = risk_decision.get("reasoning") or []
    risk_signals = risk_decision.get("top_risk_factors") or []

    recent_news = secondary_research.get("recent_news") or []

    lines = [
        "# Intelli-Credit Final Investment / Credit Assessment Report",
        "",
        "## 1. Company Overview",
        f"- Company Name: {company_overview.get('company_name', 'N/A')}",
        f"- CIN: {company_overview.get('cin', 'N/A')}",
        f"- PAN: {company_overview.get('pan', 'N/A')}",
        f"- Sector: {company_overview.get('sector', 'N/A')}",
        f"- Annual Turnover: {_fmt_currency(company_overview.get('annual_turnover'))}",
        "",
        "## 2. Loan Details",
        f"- Loan Type: {loan_details.get('loan_type', 'N/A')}",
        f"- Loan Amount: {_fmt_currency(loan_details.get('loan_amount'))}",
        f"- Loan Tenure: {loan_details.get('loan_tenure', 'N/A')}",
        f"- Indicative Interest Rate: {loan_details.get('interest_rate', 'N/A')}",
        "",
        "## 3. Extracted Financial Metrics",
        f"- Revenue: {_fmt_currency(financial_metrics.get('revenue'))}",
        f"- EBITDA: {_fmt_currency(financial_metrics.get('ebitda'))}",
        f"- Debt: {_fmt_currency(financial_metrics.get('debt'))}",
        f"- Equity: {_fmt_currency(financial_metrics.get('equity'))}",
        f"- Debt-to-Equity Ratio: {financial_metrics.get('debt_equity_ratio', 'N/A')}",
        f"- EBITDA Margin: {_fmt_percent(financial_metrics.get('ebitda_margin'))}",
        f"- Revenue Growth: {_fmt_percent(financial_metrics.get('revenue_growth'))}",
        "",
        "## 4. Risk Score & Category",
        f"- Risk Score: {risk_decision.get('risk_score', 'N/A')}",
        f"- Risk Category: {risk_decision.get('risk_category', 'N/A')}",
        "",
        "## 5. Secondary Research Summary",
        f"- Market Sentiment: {secondary_research.get('market_sentiment', 'N/A')}",
        f"- Legal Risk: {secondary_research.get('legal_risk', 'N/A')}",
        f"- Sector Outlook: {secondary_research.get('sector_outlook', 'N/A')}",
        "- Recent News:",
    ]

    if recent_news:
        lines.extend([f"  - {item}" for item in recent_news[:5]])
    else:
        lines.append("  - N/A")

    lines.extend(
        [
            "",
            "## 6. SWOT Analysis",
            "### Strengths",
        ]
    )
    lines.extend([f"- {item}" for item in (strengths or ["No major strengths identified"])])

    lines.append("")
    lines.append("### Weaknesses")
    lines.extend([f"- {item}" for item in (weaknesses or ["No major weaknesses identified"])])

    lines.append("")
    lines.append("### Opportunities")
    lines.extend([f"- {item}" for item in (opportunities or ["No major opportunities identified"])])

    lines.append("")
    lines.append("### Threats")
    lines.extend([f"- {item}" for item in (threats or ["No major threats identified"])])

    lines.extend(
        [
            "",
            "## 7. Credit Recommendation",
            f"- Loan Decision: {risk_decision.get('loan_decision', 'N/A')}",
            f"- Decision Status: {risk_decision.get('decision_status', 'N/A')}",
            f"- Recommended Loan Limit: {risk_decision.get('loan_limit', 'N/A')}",
            f"- Recommended Interest Rate: {risk_decision.get('interest_rate', 'N/A')}",
            "- Reasoning:",
        ]
    )

    if reasoning:
        lines.extend([f"  - {item}" for item in reasoning])
    else:
        lines.append("  - N/A")

    lines.extend(
        [
            "",
            "## 8. Key Risk Signals",
        ]
    )
    if risk_signals:
        lines.extend([f"- {item}" for item in risk_signals])
    else:
        lines.append("- No major adverse signals")

    # Section 9: Metric triangulation table
    triangulation_rows = _build_triangulation_rows(financial_metrics, secondary_research)
    lines.extend(["", "## 9. Metric Triangulation \u2014 Extracted vs External Signal", ""])
    for i, row in enumerate(triangulation_rows):
        lines.append("| " + " | ".join(row) + " |")
        if i == 0:
            lines.append("|" + "|".join(["---"] * len(row)) + "|")

    # Section 10: AI explainability
    factor_rows = _build_factor_weights(risk_decision)
    lines.extend(["", "## 10. AI Explainability \u2014 Weighted Factor Analysis", ""])
    for i, row in enumerate(factor_rows):
        lines.append("| " + " | ".join(row) + " |")
        if i == 0:
            lines.append("|" + "|".join(["---"] * len(row)) + "|")

    primary_driver = (risk_decision.get("top_risk_factors") or ["N/A"])[0]
    conf_val = risk_decision.get("confidence", "N/A")
    lines.extend([
        "",
        f"- Primary risk driver: {primary_driver}",
        f"- Model confidence: {conf_val}",
        f"- AI decision: {risk_decision.get('loan_decision', 'N/A')}",
    ])

    return "\n".join(lines)


def _draw_pipe_table(
    pdf: Any,
    lines: list[str],
    x_margin: float,
    y: float,
    page_width: float,
    page_height: float,
) -> float:
    """Render pipe-table lines onto a ReportLab canvas. Returns updated y position."""
    rows: list[list[str]] = []
    for raw in lines:
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        if not cells or all(set(c) <= set("-: ") for c in cells):
            continue
        rows.append(cells)
    if not rows:
        return y

    col_count = max(len(r) for r in rows)
    rows = [r + [""] * (col_count - len(r)) for r in rows]
    avail_w = page_width - 2 * x_margin
    col_w = avail_w / col_count
    row_h = 16

    for ri, row in enumerate(rows):
        if y < 40 + row_h:
            pdf.showPage()
            y = page_height - 40
        if ri == 0:
            pdf.setFillColorRGB(0.14, 0.36, 0.73)
            pdf.rect(x_margin, y - 4, avail_w, row_h, fill=1, stroke=0)
            pdf.setFillColorRGB(1.0, 1.0, 1.0)
            pdf.setFont("Helvetica-Bold", 8)
        elif ri % 2 == 0:
            pdf.setFillColorRGB(0.93, 0.96, 1.0)
            pdf.setStrokeColorRGB(0.85, 0.90, 0.98)
            pdf.rect(x_margin, y - 4, avail_w, row_h, fill=1, stroke=1)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.setFont("Helvetica", 8)
        else:
            pdf.setFillColorRGB(1.0, 1.0, 1.0)
            pdf.setStrokeColorRGB(0.85, 0.90, 0.98)
            pdf.rect(x_margin, y - 4, avail_w, row_h, fill=1, stroke=1)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.setFont("Helvetica", 8)
        for ci, cell in enumerate(row):
            max_chars = max(6, int(col_w / 5.2))
            text = cell[:max_chars] + ("\u2026" if len(cell) > max_chars else "")
            pdf.drawString(x_margin + ci * col_w + 4, y, text)
        y -= row_h

    pdf.setFillColorRGB(0.1, 0.1, 0.1)
    pdf.setStrokeColorRGB(0.0, 0.0, 0.0)
    pdf.setFont("Helvetica", 10)
    return y - 4


def markdown_to_pdf(markdown_text: str, output_path: Path) -> None:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("PDF rendering requires reportlab. Install with: pip install reportlab") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    x_margin = 40
    y = height - 40
    line_height = 14
    max_chars = 110

    table_buffer: list[str] = []

    def ensure_space(needed: float = line_height) -> None:
        nonlocal y
        if y < 40 + needed:
            pdf.showPage()
            y = height - 40
            pdf.setFont("Helvetica", 10)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)

    def flush_table() -> None:
        nonlocal y
        if table_buffer:
            y = _draw_pipe_table(pdf, list(table_buffer), x_margin, y, width, height)
            table_buffer.clear()

    for raw_line in markdown_text.splitlines():
        stripped = raw_line.strip()

        if stripped.startswith("|"):
            table_buffer.append(stripped)
            continue

        flush_table()

        if stripped.startswith("# ") and not stripped.startswith("##"):
            ensure_space(22)
            pdf.setFont("Helvetica-Bold", 14)
            pdf.setFillColorRGB(0.08, 0.22, 0.58)
            for seg in wrap(stripped[2:], width=max_chars) or [""]:
                ensure_space()
                pdf.drawString(x_margin, y, seg)
                y -= 20
            pdf.setFont("Helvetica", 10)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            continue

        if stripped.startswith("## "):
            ensure_space(18)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.setFillColorRGB(0.14, 0.36, 0.73)
            for seg in wrap(stripped[3:], width=max_chars) or [""]:
                ensure_space()
                pdf.drawString(x_margin, y, seg)
                y -= 16
            pdf.setFont("Helvetica", 10)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            continue

        if stripped.startswith("### "):
            ensure_space(16)
            pdf.setFont("Helvetica-Bold", 10)
            pdf.setFillColorRGB(0.18, 0.40, 0.20)
            for seg in wrap(stripped[4:], width=max_chars) or [""]:
                ensure_space()
                pdf.drawString(x_margin, y, seg)
                y -= line_height
            pdf.setFont("Helvetica", 10)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            continue

        wrapped = wrap(raw_line, width=max_chars) if raw_line.strip() else [""]
        for seg in wrapped:
            ensure_space()
            pdf.drawString(x_margin, y, seg)
            y -= line_height

    flush_table()
    pdf.save()


def generate_final_report_pdf(
    output_path: Path,
    company_overview: dict[str, Any],
    loan_details: dict[str, Any],
    financial_metrics: dict[str, Any],
    risk_decision: dict[str, Any],
    secondary_research: dict[str, Any],
    swot_analysis: dict[str, Any],
) -> str:
    markdown = build_final_report_markdown(
        company_overview=company_overview,
        loan_details=loan_details,
        financial_metrics=financial_metrics,
        risk_decision=risk_decision,
        secondary_research=secondary_research,
        swot_analysis=swot_analysis,
    )
    markdown_to_pdf(markdown, output_path)
    return markdown
