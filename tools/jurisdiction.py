from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Literal, List
from pydantic import BaseModel, Field

load_dotenv(".env.local")

PROMPTS_DIR = Path(__file__).parents[1] / "prompts"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def load_prompt() -> str:

    guardrails = open(PROMPTS_DIR / "guardrails.MD").read()
    jurisdiction_resolver = open(PROMPTS_DIR / "jurisdiction_resolver.MD").read()

    return guardrails + "\n\n" + jurisdiction_resolver


StatuteLevel = Literal["federal", "state", "local"]


class Jurisdiction(BaseModel):
    state: str
    city: str 
    county: str 
    federal_circuit: str
    state_court_system: str


class Statute(BaseModel):
    name: str
    citation: str
    level: StatuteLevel
    coverage_summary: str
    statute_of_limitations: str 
    sol_notes: str 
    relevant_agency: str
    agency_complaint_url: str 


class LocalOrdinance(BaseModel):
    name: str
    jurisdiction: str
    coverage_summary: str
    source_url: str 


class CourtInfo(BaseModel):
    relevant_court: str
    self_help_url: str 
    filing_fee_waiver: str 


class JurisdictionResolver(BaseModel):
    jurisdiction: Jurisdiction
    statutes: List[Statute]
    local_ordinances: List[LocalOrdinance]
    court_info: CourtInfo
    urgency_notes: str 


def resolve_jurisdiction(
    domain: str,
    sub_type: str,
    urgency: str,
    flags: List[str],
    keywords: List[str],
) -> dict:

    JURISDICTION_RESOLVER_PROMPT = load_prompt()

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": JURISDICTION_RESOLVER_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Domain: {domain}, Sub Type: {sub_type}, Urgency: {urgency}, "
                    f"Flags: {flags}, Keywords: {keywords}"
                ),
            },
        ],
        response_format=JurisdictionResolver,
    )

    parsed = response.choices[0].message.parsed

    return parsed.model_dump()
