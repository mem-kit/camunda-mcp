import os
from typing import Dict, Any
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Initialize FastMCP server
mcp = FastMCP("StateStreet CDD Service")


def _infer_scenario_for_customer(customer_id: str) -> str:
    """Infer 'positive' or 'negative' scenario from the customer_id string.

    Rules (case-insensitive):
    - if customer_id contains 'neg' or 'negative' -> 'negative'
    - if customer_id contains 'pos' or 'positive' -> 'positive'
    - otherwise -> 'positive'
    """
    if not customer_id:
        return "positive"
    s = customer_id.lower()
    if "neg" in s or "negative" in s:
        return "negative"
    if "pos" in s or "positive" in s:
        return "positive"
    return "positive"


@mcp.tool()
async def get_customer_profile(customer_id: str) -> Dict[str, Any]:
    """
    Get profile of the customer
    Simulated response returning profile data for the given customer_id.
    """
    # Simulate a customer profile with two scenario variants
    base = {
        "customer_id": customer_id,
        "name": "ACME Corp",
        "country": "US",
        "incorporation_date": "2010-07-16",
        "industry": "Financial Services",
        "contacts": [{"name": "Jane Doe", "role": "Compliance Officer", "email": "jane.doe@example.com"}]
    }

    scenario = _infer_scenario_for_customer(customer_id)
    if scenario == "negative":
        base.update({
            "status": "under_review",
            "risk_profile": "high",
            "notes": "Potential sanctions exposure and anomalous transactions detected"
        })
    else:
        base.update({"status": "active", "risk_profile": "low", "notes": "Customer in good standing"})

    # include a short set of next-steps depending on scenario
    # next_steps are structured: they can contain strings (human actions) or tool calls
    if scenario == "negative":
        base["next_steps"] = [
            "Collect additional KYC",
            "Enhanced monitoring",
            "Escalate to AML officer",
            {"tool": "get_risk_score", "params": {"customer_id": customer_id}},
            {"tool": "generate_compliance_report", "params": {"customer_id": customer_id}}
        ]
    else:
        base["next_steps"] = [
            "Standard monitoring",
            "Periodic review in 12 months",
            {"tool": "get_risk_score", "params": {"customer_id": customer_id}},
            {"tool": "generate_compliance_report", "params": {"customer_id": customer_id}}
        ]

    return base


@mcp.tool()
async def get_risk_score(customer_id: str) -> Dict[str, Any]:
    """
    Get risk score of the customer
    Simulated response returning a risk score.
    """
    # Simulate a composite risk score with sub-scores
    # default / moderate baseline
    baseline = {
        "customer_id": customer_id,
        "scale": "0-100",
        "factors": {
            "sanctions": 5,
            "geo_risk": 12,
            "industry_risk": 20,
            "transaction_pattern": 35
        }
    }

    scenario = _infer_scenario_for_customer(customer_id)
    if scenario == "negative":
        score = int(sum(baseline["factors"].values()) * 2.0)
        baseline.update({
            "score": min(100, score),
            "interpretation": "High risk",
            "recommendation": ["Immediate enhanced due diligence", "Transaction restrictions until cleared"],
            "next_steps": [
                "Freeze suspicious accounts",
                "Collect source-of-funds evidence",
                "Notify AML team",
                {"tool": "explain_risk", "params": {"customer_id": customer_id}},
                {"tool": "generate_compliance_report", "params": {"customer_id": customer_id}}
            ]
        })
    else:
        score = max(0, int(sum(baseline["factors"].values()) * 0.3))
        baseline.update({
            "score": score,
            "interpretation": "Low risk" if score < 30 else "Moderate risk",
            "recommendation": ["Standard monitoring"] if score < 30 else ["Enhanced monitoring"],
            "next_steps": [
                "Routine checks" if score < 30 else "Request a brief KYC update",
                {"tool": "explain_risk", "params": {"customer_id": customer_id}},
                {"tool": "generate_compliance_report", "params": {"customer_id": customer_id}}
            ]
        })

    return baseline


@mcp.tool()
async def explain_risk(customer_id: str) -> Dict[str, Any]:
    """
    Explain the risk of the customer
    """
    # Simulate an explanation of the key contributors to the risk score
    scenario = _infer_scenario_for_customer(customer_id)
    if scenario == "negative":
        return {
            "customer_id": customer_id,
            "explanation": (
                "High risk indicators: suspicious transaction patterns, exposure to higher-risk geographies, and possible name matches in screening results."
            ),
            "recommendation": [
                "Immediate enhanced due diligence",
                "Temporary transaction restrictions",
                "Collect and verify source-of-funds and beneficial ownership documentation"
            ],
            "next_steps": [
                "Escalate to AML officer",
                "Open investigation ticket",
                "Contact counterparty banks if required",
                {"tool": "generate_compliance_report", "params": {"customer_id": customer_id}}
            ]
        }

    # Positive / low-risk explanation
    return {
        "customer_id": customer_id,
        "explanation": "Low risk profile: strong KYC, low geolocation exposure, and normal transaction patterns.",
        "recommendation": ["Standard monitoring", "Annual re-check"],
        "next_steps": [
            "Continue normal monitoring",
            "Re-run scoring yearly",
            {"tool": "generate_compliance_report", "params": {"customer_id": customer_id}}
        ]
    }


@mcp.tool()
async def generate_compliance_report(customer_id: str) -> Dict[str, Any]:
    """
    Generate compliance report for the given customer
    """
    # Generate reports that differ by scenario
    report = {
        "customer_id": customer_id,
        "report_id": f"RPT-{customer_id}-001",
        "generated_at": "2025-11-29T12:00:00Z",
    }

    scenario = _infer_scenario_for_customer(customer_id)
    if scenario == "negative":
        report["summary"] = {
            "kyc_verified": False,
            "aml_checks_passed": False,
            "open_issues": [
                {"id": "ISS-01", "description": "Multiple high-value transfers to flagged jurisdictions"},
                {"id": "ISS-02", "description": "Possible mismatch in beneficial owner documentation"}
            ]
        }
        report["next_steps"] = [
            "Freeze account pending investigation",
            "Collect source-of-funds evidence",
            "Escalate to AML officer and file internal incident"
        ]
    else:
        report["summary"] = {
            "kyc_verified": True,
            "aml_checks_passed": True,
            "open_issues": []
        }
        report["next_steps"] = [
            "Archive check results",
            "Re-evaluate in 12 months"
        ]

    return report


if __name__ == "__main__":
    # Configure CORS middleware (same as OCR service)
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id"]  # for SSE support
        )
    ]

    # Run the MCP server in HTTP SSE mode on port 3000
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=3000,
        path="/mcp",
        middleware=middleware
    )
