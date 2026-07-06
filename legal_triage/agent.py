"""
legal_triage/agent.py
=====================
Phase 2: ADK Agent Port
-----------------------
Defines the multi-agent Legal-Aid Triage system using the Google ADK framework.

Architecture
------------
                        ┌──────────────────────────────┐
                        │   triage_orchestrator (root)  │
                        │   LlmAgent — gemini-2.0-flash │
                        │   Tools: generate_intake_doc  │
                        │   Sub-agents ──────────────── │
                        │    • issue_classifier          │
                        │    • jurisdiction_resolver     │
                        │   MCP Tools (via McpToolset): │
                        │    • get_statute_summary       │
                        │    • search_legal_aid_orgs     │
                        └──────────────────────────────┘

The orchestrator:
  1. Delegates classification to issue_classifier (LlmAgent, task mode).
  2. Delegates jurisdiction resolution to jurisdiction_resolver (LlmAgent, task mode).
  3. Calls get_statute_summary (MCP) for each statute returned.
  4. Calls search_legal_aid_orgs (MCP) to find relevant organisations.
  5. Calls generate_intake_doc (local function tool) to produce the final document.

Environment variables:
  OPENAI_API_KEY  — Not used by the ADK agents (they use Gemini by default).
  GOOGLE_API_KEY  — AI Studio Gemini key (or GEMINI_API_KEY as alias).
  Alternatively, set GOOGLE_GENAI_USE_VERTEXAI=True for Vertex AI.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from mcp import StdioServerParameters
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams

from legal_triage.intake import generate_intake_doc
from legal_triage.prompt_loader import build_system_prompt, load_prompt

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(dotenv_path=os.path.join(_PROJECT_ROOT, ".env.local"))
load_dotenv(dotenv_path=os.path.join(_PROJECT_ROOT, "legal_triage", ".env"))
load_dotenv()

# ---------------------------------------------------------------------------
# MCP Toolset — connects to the local FastMCP stdio server
# ---------------------------------------------------------------------------

_MCP_SERVER_PATH = os.path.join(_PROJECT_ROOT, "mcp_server", "server.py")
_PYTHON_EXECUTABLE = sys.executable  # Use the same venv Python as the runner

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=_PYTHON_EXECUTABLE,
            args=[_MCP_SERVER_PATH],
            env={
                # Forward the current environment so OPENAI_API_KEY is available
                **os.environ,
            },
        ),
    ),
    # Only expose the two tools this agent needs
    tool_filter=["get_statute_summary", "search_legal_aid_orgs"],
)

# ---------------------------------------------------------------------------
# Sub-agent: issue_classifier
# ---------------------------------------------------------------------------
# Receives the user's raw description and returns a ClassificationResult JSON.
# Uses "task" mode so the orchestrator gets a typed result via finish_task.

issue_classifier = Agent(
    name="issue_classifier",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description=(
        "Classifies a free-text legal situation description into a structured "
        "JSON object containing primary_domain, sub_type, confidence, "
        "ambiguity_flags, urgency, secondary_domains, and keywords_matched."
    ),
    instruction=build_system_prompt("classifier.MD"),
    # task mode: orchestrator gets a finish_task tool; classifier calls it
    # when done instead of returning a conversational reply.
    mode="task",
    output_key="classification_result",
)

# ---------------------------------------------------------------------------
# Sub-agent: jurisdiction_resolver
# ---------------------------------------------------------------------------
# Receives issue type + location and returns a JurisdictionResult JSON
# with statutes, local ordinances, and court info.

jurisdiction_resolver = Agent(
    name="jurisdiction_resolver",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description=(
        "Resolves the governing bodies of law (federal statutes, state statutes, "
        "local ordinances) and court information for a given legal issue type "
        "and jurisdiction (state, city). Returns a structured JSON object."
    ),
    instruction=build_system_prompt("jurisdiction_resolver.MD"),
    mode="task",
    output_key="jurisdiction_result",
)

# ---------------------------------------------------------------------------
# Root agent: triage_orchestrator
# ---------------------------------------------------------------------------

_ORCHESTRATOR_INSTRUCTION = build_system_prompt("triage_agent.MD")

root_agent = Agent(
    name="triage_orchestrator",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description=(
        "Legal-Aid Triage Orchestrator. Runs a structured five-step pipeline: "
        "classify the issue, resolve the jurisdiction, look up relevant statutes "
        "via MCP, find legal aid organisations via MCP, and draft the intake summary."
    ),
    instruction=_ORCHESTRATOR_INSTRUCTION,
    sub_agents=[issue_classifier, jurisdiction_resolver],
    tools=[
        # MCP tools: get_statute_summary, search_legal_aid_orgs
        mcp_toolset,
        # Local function tool: final intake document generator
        generate_intake_doc,
    ],
)
