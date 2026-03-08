from __future__ import annotations


def format_cam_markdown(company_name: str, sections: dict[str, str], risk_decision: dict[str, object]) -> str:
    risk_score = risk_decision.get("risk_score", "N/A")
    risk_category = risk_decision.get("risk_category", "N/A")

    markdown = f"""# Credit Approval Memo

Company: {company_name}

## Character

{sections.get("character", "N/A")}

## Capacity

{sections.get("capacity", "N/A")}

## Capital

{sections.get("capital", "N/A")}

## Collateral

{sections.get("collateral", "N/A")}

## Conditions

{sections.get("conditions", "N/A")}

## AI Risk Summary

Risk Score: {risk_score}
Risk Category: {risk_category}
"""

    return markdown.strip() + "\n"
