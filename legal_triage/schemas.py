"""
legal_triage/schemas.py
=======================
Pydantic schemas for the Legal-Aid Triage Agent pipeline.

These models define the structured data flowing between the sub-agents and
the MCP server tools so that every handoff has a typed, validated contract.
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Classification schema  (output of issue_classifier)
# ---------------------------------------------------------------------------

class ClassificationResult(BaseModel):
    """Structured output returned by the issue_classifier sub-agent."""

    primary_domain: str = Field(
        description=(
            "Top-level legal domain: housing, labor, discrimination, consumer, "
            "family, immigration, criminal, benefits, or other."
        )
    )
    sub_type: str = Field(
        description="Specific sub-category within the primary domain."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Classifier confidence score between 0.0 and 1.0.",
    )
    ambiguity_flags: list[str] = Field(
        default_factory=list,
        description="List of flags signalling missing or ambiguous information.",
    )
    urgency: str = Field(
        description="Urgency level: low, medium, high, or critical.",
    )
    secondary_domains: list[str] = Field(
        default_factory=list,
        description="Additional relevant legal domains.",
    )
    keywords_matched: list[str] = Field(
        default_factory=list,
        description="Key terms extracted from the user's description.",
    )


# ---------------------------------------------------------------------------
# Jurisdiction schema  (output of jurisdiction_resolver)
# ---------------------------------------------------------------------------

class JurisdictionInfo(BaseModel):
    """Structured jurisdiction metadata."""

    state: str
    city: Optional[str] = None
    county: Optional[str] = None
    federal_circuit: Optional[str] = None
    state_court_system: Optional[str] = None


class StatuteEntry(BaseModel):
    """A single statute or regulation record."""

    name: str
    citation: str
    level: str  # "federal" | "state" | "local"
    coverage_summary: str
    statute_of_limitations: Optional[str] = None
    sol_notes: Optional[str] = None
    relevant_agency: Optional[str] = None
    agency_complaint_url: Optional[str] = None


class LocalOrdinance(BaseModel):
    """A city- or county-level ordinance."""

    name: str
    jurisdiction: str
    coverage_summary: str
    source_url: Optional[str] = None


class CourtInfo(BaseModel):
    """Self-help court information for the resolved jurisdiction."""

    relevant_court: str
    self_help_url: Optional[str] = None
    filing_fee_waiver: Optional[str] = None


class JurisdictionResult(BaseModel):
    """Structured output returned by the jurisdiction_resolver sub-agent."""

    jurisdiction: JurisdictionInfo
    statutes: list[StatuteEntry] = Field(default_factory=list)
    local_ordinances: list[LocalOrdinance] = Field(default_factory=list)
    court_info: CourtInfo
    urgency_notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Legal Aid Org schema  (mirrors MCP tool output)
# ---------------------------------------------------------------------------

class LegalAidOrg(BaseModel):
    """One legal aid organisation record."""

    org_name: str
    address: str = "See website"
    phone: str = "See website"
    website: str = ""
    issue_types: list[str] = Field(default_factory=list)
    eligibility_notes: str = ""
    intake_process: str = ""
    capacity_signal: str = "unknown"
    urgency_capable: bool = False


# ---------------------------------------------------------------------------
# Intake context schema  (aggregated pipeline state -> intake drafter)
# ---------------------------------------------------------------------------

class TriageContext(BaseModel):
    """
    Full pipeline state passed to generate_intake_doc.
    Combines user input with all sub-agent and MCP tool results.
    """

    user_description: str = Field(
        description="The user's original free-text situation description."
    )
    classification: Optional[ClassificationResult] = None
    jurisdiction: Optional[JurisdictionResult] = None
    statute_summaries: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Raw statute summary dicts returned by get_statute_summary MCP tool.",
    )
    legal_aid_orgs: list[LegalAidOrg] = Field(
        default_factory=list,
        description="Ranked legal aid organisations for this user.",
    )
