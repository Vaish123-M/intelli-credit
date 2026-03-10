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

    return "\n".join(lines)


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

    for raw_line in markdown_text.splitlines():
        line = raw_line.replace("### ", "").replace("## ", "").replace("# ", "")
        wrapped = wrap(line, width=max_chars) if line else [""]
        for segment in wrapped:
            if y < 40:
                pdf.showPage()
                y = height - 40
            pdf.drawString(x_margin, y, segment)
            y -= line_height

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
