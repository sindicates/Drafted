"""
tests/test_smoke.py
===================
Phase 1 smoke tests for the Legal-Aid Triage MCP server.

Exercises:
  1. get_statute_summary  – verifies required keys and non-empty summary
  2. search_legal_aid_orgs – verifies result list structure and non-empty return
  3. _extract_json helper – unit-tests the JSON fence-stripping utility
  4. _ddgs_text helper    – verifies the search wrapper returns a list of dicts

Run with:
    source .venv/bin/activate
    pytest tests/test_smoke.py -v
"""

import sys
import os

import pytest

# ---------------------------------------------------------------------------
# Path setup – makes `mcp_server` importable without installing the package
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load env so OPENAI_API_KEY is available before the module-level client init
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import mcp_server.server as srv


# ===========================================================================
# Helper / Unit tests  (no network / API calls)
# ===========================================================================

class TestExtractJson:
    """Unit-test the _extract_json helper independently of any API call."""

    def test_plain_json_object(self):
        raw = '{"key": "value", "num": 42}'
        result = srv._extract_json(raw)
        assert result == {"key": "value", "num": 42}

    def test_strips_markdown_json_fence(self):
        raw = '```json\n{"foo": "bar"}\n```'
        result = srv._extract_json(raw)
        assert result["foo"] == "bar"

    def test_strips_plain_markdown_fence(self):
        raw = '```\n{"hello": "world"}\n```'
        result = srv._extract_json(raw)
        assert result["hello"] == "world"

    def test_invalid_json_returns_raw_response(self):
        raw = "This is not JSON at all."
        result = srv._extract_json(raw)
        assert "raw_response" in result
        assert result["raw_response"] == raw


# ===========================================================================
# DuckDuckGo search helper  (live network, no OpenAI)
# ===========================================================================

class TestDdgsText:
    """Verify the DuckDuckGo search wrapper returns usable results."""

    def test_returns_list(self):
        results = srv._ddgs_text("California eviction law", max_results=3)
        assert isinstance(results, list)

    def test_results_are_dicts(self):
        results = srv._ddgs_text("minimum wage law", max_results=2)
        assert len(results) >= 1
        for r in results:
            assert isinstance(r, dict)

    def test_results_have_expected_keys(self):
        results = srv._ddgs_text("wage theft attorney", max_results=2)
        for r in results:
            # At least one of these should be present in each result dict
            assert any(k in r for k in ("title", "body", "href", "url", "link"))


# ===========================================================================
# MCP Tool 1: get_statute_summary  (live DuckDuckGo + OpenAI)
# ===========================================================================

class TestGetStatuteSummary:

    def test_required_keys_present(self):
        result = srv.get_statute_summary(
            statute_name="California Labor Code 1194",
            citation="Cal. Lab. Code § 1194",
        )
        required_keys = {
            "statute_name",
            "citation",
            "plain_language_summary",
            "statute_of_limitations",
            "sol_notes",
            "source_urls",
        }
        assert required_keys.issubset(result.keys()), (
            f"Missing keys: {required_keys - result.keys()}"
        )

    def test_statute_name_is_string(self):
        result = srv.get_statute_summary("Florida eviction law")
        assert isinstance(result["statute_name"], str)
        assert len(result["statute_name"]) > 0

    def test_plain_language_summary_is_non_empty(self):
        result = srv.get_statute_summary("New York Paid Family Leave Law")
        summary = result.get("plain_language_summary", "")
        assert isinstance(summary, str)
        assert len(summary) > 20, "Summary should be more than a placeholder"

    def test_source_urls_is_list(self):
        result = srv.get_statute_summary("Texas wrongful termination law")
        assert isinstance(result["source_urls"], list)

    def test_statute_of_limitations_field_exists(self):
        result = srv.get_statute_summary("FLSA minimum wage", "29 U.S.C. § 206")
        sol = result.get("statute_of_limitations", "")
        # Should be a non-empty string (could be "Unknown" but not absent)
        assert isinstance(sol, str) and len(sol) > 0


# ===========================================================================
# MCP Tool 2: search_legal_aid_orgs  (live DuckDuckGo + OpenAI)
# ===========================================================================

class TestSearchLegalAidOrgs:

    def test_returns_results_key(self):
        result = srv.search_legal_aid_orgs(
            issue_type="labor",
            sub_type="wage theft",
            state="CA",
            city="Los Angeles",
            urgency="high",
        )
        assert "results" in result, "Response must contain a 'results' key"

    def test_results_is_list(self):
        result = srv.search_legal_aid_orgs(
            issue_type="housing",
            sub_type="eviction",
            state="NY",
            urgency="medium",
        )
        assert isinstance(result["results"], list)

    def test_at_least_one_org_returned(self):
        result = srv.search_legal_aid_orgs(
            issue_type="labor",
            sub_type="wage theft",
            state="CA",
            city="Los Angeles",
            urgency="high",
        )
        orgs = result["results"]
        assert len(orgs) >= 1, "Expected at least one legal aid org to be found"

    def test_org_has_required_fields(self):
        result = srv.search_legal_aid_orgs(
            issue_type="housing",
            sub_type="eviction",
            state="CA",
            city="San Francisco",
            urgency="low",
        )
        required_org_keys = {"org_name", "website", "issue_types"}
        for org in result["results"]:
            assert required_org_keys.issubset(org.keys()), (
                f"Org missing keys: {required_org_keys - org.keys()} | org={org}"
            )

    def test_query_echo_in_response(self):
        result = srv.search_legal_aid_orgs(
            issue_type="labor",
            sub_type="discrimination",
            state="TX",
            urgency="low",
        )
        assert "query" in result
        q = result["query"]
        assert q["issue_type"] == "labor"
        assert q["state"] == "TX"

    def test_urgency_capable_is_bool(self):
        result = srv.search_legal_aid_orgs(
            issue_type="housing",
            sub_type="eviction",
            state="FL",
            urgency="critical",
        )
        for org in result["results"]:
            if "urgency_capable" in org:
                assert isinstance(org["urgency_capable"], bool), (
                    f"urgency_capable should be bool, got {type(org['urgency_capable'])}"
                )
