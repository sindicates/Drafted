"""
Legal-Aid Triage MCP Server (Phase 1 – Dynamic)
================================================
Exposes two FastMCP tools that replace the old static JSON databases with
live external lookups:

  • get_statute_summary   – DuckDuckGo web search → OpenAI synthesis
  • search_legal_aid_orgs – DuckDuckGo web search → OpenAI synthesis

Environment variables required (place in .env or export in shell):
  OPENAI_API_KEY  – OpenAI API key for model calls
"""

import json
import os
import re
import textwrap
import time
from typing import Optional

from dotenv import load_dotenv
from ddgs import DDGS
import openai
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env.local"))
load_dotenv()  # also try plain .env at project root

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise EnvironmentError(
        "OPENAI_API_KEY is not set. Export it in your shell or add it to .env.local"
    )

_openai_client = openai.Client(api_key=OPENAI_API_KEY)

# Model fallback chain: try each in order until one succeeds
_OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-3.5-turbo",
]

mcp = FastMCP("legal-triage-mcp")

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ddgs_text(query: str, max_results: int = 6) -> list[dict]:
    """Run a DuckDuckGo text search and return a list of result dicts."""
    try:
        results = DDGS().text(query, max_results=max_results)
        return list(results) if results else []
    except Exception as exc:
        return [{"title": "Search error", "body": str(exc), "href": ""}]


def _openai_synthesize(system_prompt: str, user_content: str) -> str:
    """
    Call OpenAI and return the text response.
    Iterates through _OPENAI_MODELS with exponential backoff on rate limits.
    Raises RuntimeError only after all models are exhausted.
    """
    last_error: Exception | None = None
    for model in _OPENAI_MODELS:
        for attempt in range(3):  # up to 3 retries per model
            try:
                response = _openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=0.2,
                    max_tokens=1024,
                )
                return response.choices[0].message.content.strip()
            except Exception as exc:
                last_error = exc
                err_str = str(exc)
                if "429" in err_str or "Rate limit" in err_str:
                    # Rate limit hit – wait briefly then try next model
                    wait = 2 ** attempt
                    time.sleep(wait)
                    break  # move to next model immediately
                else:
                    raise  # propagate non-quota errors straight away
    # All models exhausted
    raise RuntimeError(
        f"All OpenAI models exhausted due to rate limits. Last error: {last_error}"
    )


def _extract_json(text: str) -> dict:
    """
    Best-effort extraction of a JSON object from an OpenAI response.
    Strips markdown fences if present, then parses.
    """
    # Remove ```json ... ``` fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Return the raw text wrapped in a field so callers always get a dict
        return {"raw_response": text}


# ---------------------------------------------------------------------------
# Tool 1: get_statute_summary
# ---------------------------------------------------------------------------

@mcp.tool()
def get_statute_summary(statute_name: str, citation: Optional[str] = None) -> dict:
    """
    Retrieve a plain-language summary, statute of limitations, and key notes
    for a specific law using a live web search synthesized by OpenAI.

    Args:
        statute_name: The name or keyword of the statute
                      (e.g. "California Labor Code § 1194", "Florida eviction law").
        citation:     Optional exact citation to include in the search query.
    """
    # Build a targeted search query
    search_query = statute_name
    if citation:
        search_query = f"{citation} {statute_name} plain language summary statute of limitations"
    else:
        search_query = f"{statute_name} legal statute plain language summary statute of limitations"

    snippets = _ddgs_text(search_query, max_results=6)

    # Combine results into a compact context block for OpenAI
    context_lines = []
    for i, r in enumerate(snippets, 1):
        title = r.get("title", "")
        body = r.get("body", "")
        href = r.get("href", "")
        context_lines.append(f"[{i}] {title}\n{body}\nSource: {href}")
    context_block = "\n\n".join(context_lines)

    system_prompt = textwrap.dedent("""
        You are a legal-information assistant. A user is asking about a specific statute.
        Using ONLY the web search results provided, produce a concise, plain-language
        explanation suitable for a non-lawyer. Return your answer as a single JSON object
        with EXACTLY these keys (no extras):
          {
            "statute_name": "<official or requested name>",
            "citation": "<official citation if found, otherwise the one provided>",
            "plain_language_summary": "<2-4 sentence plain English explanation>",
            "statute_of_limitations": "<SOL period, e.g. '3 years'>",
            "sol_notes": "<any SOL caveats or tolling rules>",
            "source_urls": ["<url1>", "<url2>"]
          }
        If you cannot determine a value from the search results, use "Unknown".
        Do NOT add commentary outside the JSON block.
    """).strip()

    user_content = (
        f"Statute requested: {statute_name}\n"
        + (f"Citation hint: {citation}\n" if citation else "")
        + f"\nWeb search results:\n{context_block}"
    )

    raw = _openai_synthesize(system_prompt, user_content)
    result = _extract_json(raw)

    # Guarantee required keys are present even if OpenAI skips one
    defaults = {
        "statute_name": statute_name,
        "citation": citation or "Citation unavailable",
        "plain_language_summary": result.get("raw_response", "Summary unavailable"),
        "statute_of_limitations": "Unknown",
        "sol_notes": "Please consult a licensed attorney for jurisdiction-specific deadlines.",
        "source_urls": [],
    }
    defaults.update(result)
    return defaults


# ---------------------------------------------------------------------------
# Tool 2: search_legal_aid_orgs
# ---------------------------------------------------------------------------

@mcp.tool()
def search_legal_aid_orgs(
    issue_type: str,
    sub_type: str,
    state: str,
    city: Optional[str] = None,
    zip_code: Optional[str] = None,
    urgency: str = "medium",
) -> dict:
    """
    Search for legal aid organizations based on issue type, location, and urgency
    using a live web search synthesized by OpenAI.

    Args:
        issue_type: The broad domain of the legal issue (e.g. "labor", "housing").
        sub_type:   The specific sub-category (e.g. "wage theft", "eviction").
        state:      Two-letter state code or full state name (e.g. "CA", "Florida").
        city:       Optional city name for more localised results.
        zip_code:   Optional zip code for hyper-local results.
        urgency:    Urgency level ("low", "medium", "high", "critical").
    """
    # Compose a targeted search
    location_parts = [state]
    if city:
        location_parts.insert(0, city)
    if zip_code:
        location_parts.insert(0, zip_code)
    location_str = " ".join(location_parts)

    urgency_qualifier = ""
    if urgency in ("high", "critical"):
        urgency_qualifier = " emergency same-day intake"

    search_query = (
        f"free legal aid {sub_type} {issue_type} attorney help "
        f"{location_str}{urgency_qualifier} nonprofit organization"
    )

    snippets = _ddgs_text(search_query, max_results=8)

    context_lines = []
    for i, r in enumerate(snippets, 1):
        title = r.get("title", "")
        body = r.get("body", "")
        href = r.get("href", "")
        context_lines.append(f"[{i}] {title}\n{body}\nSource: {href}")
    context_block = "\n\n".join(context_lines)

    system_prompt = textwrap.dedent("""
        You are a legal-aid resource specialist. Using ONLY the web search results
        provided, identify up to 5 real legal aid organizations that serve the
        requested location and could assist with the requested issue type.
        Note: General civil legal aid organizations typically assist with housing, labor, and consumer issues in their service area unless they explicitly list only other areas.

        Return a JSON object with EXACTLY this structure (no extra keys):
        {
          "results": [
            {
              "org_name": "<Organization name>",
              "address": "<Street address or 'See website'>",
              "phone": "<Phone number or 'See website'>",
              "website": "<URL>",
              "issue_types": ["<type1>", "<type2>"],
              "eligibility_notes": "<income limit or eligibility notes>",
              "intake_process": "<how to apply>",
              "capacity_signal": "<accepting / waitlist / unknown>",
              "urgency_capable": <true | false>
            }
          ]
        }

        Rules:
        - Only include organisations that clearly serve the requested state/city.
        - If fewer than 5 are found, return what you have (minimum 1).
        - Set urgency_capable to true only if the source explicitly mentions
          emergency, same-day, or urgent intake.
        - Do NOT invent organisations; use only what appears in the search results.
        - Do NOT add commentary outside the JSON block.
    """).strip()

    user_content = (
        f"Issue type: {issue_type} / {sub_type}\n"
        f"Location: {location_str}\n"
        f"Urgency: {urgency}\n"
        f"\nWeb search results:\n{context_block}"
    )

    raw = _openai_synthesize(system_prompt, user_content)
    result = _extract_json(raw)

    # Guarantee top-level structure
    if "results" not in result:
        result = {
            "results": [],
            "error": result.get("raw_response", "Could not parse OpenAI response"),
        }

    return {
        "results": result.get("results", []),
        "query": {
            "issue_type": issue_type,
            "sub_type": sub_type,
            "state": state,
            "city": city,
            "zip_code": zip_code,
            "urgency": urgency,
        },
    }


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
