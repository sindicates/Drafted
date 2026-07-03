from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from enum import Enum
from typing import Literal, List
from pydantic import BaseModel, Field

load_dotenv(".env.local")

PROMPTS_DIR = Path(__file__).parents[1] / "prompts"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def load_prompt() -> str:

    guardrails = open(PROMPTS_DIR / "guardrails.MD").read()
    classifier = open(PROMPTS_DIR / "classifier.MD").read()

    return guardrails + "\n\n" + classifier

class PrimaryDomain(str, Enum):
    HOUSING = "housing"
    LABOR = "labor"
    DISCRIMINATION = "discrimination"
    CONSUMER = "consumer"
    FAMILY = "family"
    IMMIGRATION = "immigration"
    CRIMINAL = "criminal"
    BENEFITS = "benefits"
    OTHER = "other"

class Urgency(str, Enum):
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

AmbiguityFlag = Literal[
    "multiple_domains",
    "jurisdiction_unclear",
    "timeline_unclear",
    "documents_unspecified",
    "income_unknown",
    "immigration_sensitive",
    ]

class LegalIssueClassifier(BaseModel):

    primary_domain: PrimaryDomain
    sub_type: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    urgency: Urgency
    ambiguity_flags: List[AmbiguityFlag] = []
    secondary_domains: List[str] = []
    keywords_matched: List[str] = []
        

def classify_legal_issue(user_input: str) -> dict:

    SYSTEM_PROMPT = load_prompt()
        
    response = client.beta.chat.completions.parse(

        model = "gpt-4o-mini",

        messages = [

            { "role": "system", "content": SYSTEM_PROMPT },
            { "role": "user", "content": user_input }

        ],

        response_format = LegalIssueClassifier,



    )

    parsed = response.choices[0].message.parsed


    return parsed.model_dump()
