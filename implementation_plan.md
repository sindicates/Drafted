# Legal-Aid Triage Agent → Google ADK Capstone Pivot

This plan outlines the steps to pivot the current Legal-Aid Triage project to the Google ADK Capstone requirements, focusing on a multi-agent system, a custom MCP server, enforced guardrails, and clear deployability docs.

> [!NOTE]
> **Execution Strategy:** I (Antigravity AI) will act as your "Agent Coder" and implement Phases 0 through 6. This includes writing all the Python code, the MCP server, and drafting the README and Kaggle writeup. 
> You (the Orchestrator) will review my work, run the local tests (`adk web`), and record the final video (Phase 7).

## User Review Required
- Please review this plan to confirm the division of labor (I write the code, you test and present).
- Confirm you have your Gemini API key ready for Phase 0.
- Confirm if you want me to commit the changes to git or just leave them staged in the workspace.

## Proposed Changes

### Phase 0: Environment Reset
- **Task:** Create a Python 3.11 virtual environment, install ADK dependencies (`google-adk`, `mcp`, `pydantic`, `python-dotenv`), and remove `openai`.
- **Outputs:** Updated `requirements.txt`, `setup_venv.sh`, and a gitignored `legal_triage/.env`.

### Phase 1: MCP Server + Sample Dataset
- **Task:** Build a local FastMCP (stdio) server to replace the hardcoded dictionary lookups in `tools/mapper.py` and `tools/resource_router.py`.
- **Outputs:**
  - `mcp_server/data/statutes.json` (mock CA/NY/TX labor/housing laws)
  - `mcp_server/data/legal_aid_orgs.json` (mock legal aid organizations)
  - `mcp_server/server.py` (FastMCP exposing `get_statute_summary` and `search_legal_aid_orgs`)

### Phase 2: ADK Agent Port
- **Task:** Port the OpenAI logic to the ADK `Agent` and `McpToolset` architecture.
- **Outputs:**
  - `legal_triage/schemas.py`: Ported Pydantic schemas.
  - `legal_triage/prompt_loader.py`: Replaces the current `.MD` loader.
  - `legal_triage/intake.py`: Updated intake generator tool.
  - `legal_triage/agent.py`: Root `triage_orchestrator` with `issue_classifier` and `jurisdiction_resolver` sub-agents.
  - `legal_triage/__init__.py`: ADK package init.

### Phase 3: Enforced Guardrails
- **Task:** Implement deterministic callback shields around the LLM agents based on `prompts/guardrails.MD`.
- **Outputs:**
  - `legal_triage/callbacks.py`: Contains `crisis_interceptor`, `output_guard`, `confidence_gate_check`, and `confidence_gate_set`.

### Phase 4: Cleanup + Tests
- **Task:** Remove legacy OpenAI files and add data-layer tests.
- **Outputs:**
  - **[DELETE]** `tools/` and `agent/` folders.
  - **[NEW]** `tests/test_smoke.py`.

### Phase 5 & 6: Documentation Drafts
- **Task:** Write the required README and the Kaggle writeup draft.
- **Outputs:**
  - `README.md` (Updated with architecture, setup, and Cloud Run deploy notes).
  - `docs/writeup.md` (Kaggle submission draft).

### Phase 7: Video Script & Submission (User Task)
- **Task:** You will use the script drafted in Phase 6 to record the 5-minute video showing the `adk web` trace.

## Verification Plan

### Automated Tests
- `pytest tests/test_smoke.py` to ensure MCP functions and intake logic run correctly.

### Manual Verification
- You will run `adk run legal_triage` and test three scenarios:
  1. **Wage theft (Happy Path):** Confirm full 5-step flow.
  2. **Will I win? (Guardrail Trigger):** Confirm refusal + redirect.
  3. **Crisis Phrasing (Interceptor):** Confirm 988 response with no model call.
