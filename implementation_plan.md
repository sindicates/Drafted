# Legal-Aid Triage Agent → Google ADK Capstone Pivot

This plan outlines the steps to pivot the current Legal-Aid Triage project to the Google ADK Capstone requirements, focusing on a multi-agent system, a custom MCP server with a live API fallback, code-enforced guardrails, and clear course deliverables.

> [!NOTE]
> **Execution Strategy:** I (Antigravity AI) will act as your "Agent Coder" and implement Phases 0 through 6. 
> You (the Orchestrator) will review the work, run local tests using the `adk` CLI, and record the final 5-minute video demonstration (Phase 7).

## User Review Required
- Confirm that the updated model roadmap utilizing your exact IDE model names meets your expectations.
- Confirm if you have exported `OPENAI_API_KEY` in your terminal (switched from `GEMINI_API_KEY`).

---

## Best Model Recommendation for Coding Phases
Based on your specific IDE dropdown options, here is the optimal roadmap for driving the AI assistant during each phase:

| Phase | Tasks | Recommended Model (Select in IDE) | Rationale |
| :--- | :--- | :--- | :--- |
| **Phase 1: Dynamic MCP Server** | Implement dynamic MCP tools integrating LSC/LawHelp, Cornell LII, OpenStates, and CourtListener APIs. | **Gemini 3.5 Flash (High)** | **Best for Speed:** Fast at API integration and structured JSON mapping. |
| **Phase 2: ADK Agent Port** | Port schemas and rewrite orchestrator agents. | **Claude Sonnet 4.6 (Thinking)** | **Best for Structure:** High-reasoning model is excellent at translating framework rules, structural ports, and configuring tool pipelines. |
| **Phase 3: Enforced Guardrails** | Implement crisis and disclaimer callbacks. | **Claude Sonnet 4.6 (Thinking)** | **Best for Logic:** Active "Thinking" mode is perfect for resolving complex state tracking and callback middleware logic without errors. |
| **Phase 4: Cleanup & Smoke Tests** | Delete legacy code and write pytest smoke tests. | **Gemini 3.5 Flash (High)** | **Best for Boilerplate:** Fast execution for deleting folders and writing simple test assertions. |
| **Phase 5 & 6: Docs & Writeup** | Write README and Kaggle Capstone writeup. | **Claude Sonnet 4.6 (Thinking)** or **Claude Opus 4.6 (Thinking)** | **Best for Writing:** Both thinking models excel at drafting highly detailed, comprehensive, and natural narrative documents. |

---

## Proposed Changes

### Phase 0: Environment Reset
- **Task:** Verify Python 3.11 virtual environment, install ADK dependencies (`google-adk`, `mcp`, `pydantic`, `python-dotenv`), and install `openai` (removing `google-genai`).
- **Outputs:** Updated `requirements.txt`, `setup_venv.sh`, and `legal_triage/.env`. (Requires update to use openai).

### Phase 1: Dynamic MCP Server
- **Task:** Build a local FastMCP (stdio) server that replaces hardcoded JSON lookups with the official APIs specified in the architecture document:
  - **LSC / LawHelp API** for legal aid organizations (`search_legal_aid_orgs`)
  - **Cornell LII / OpenStates API** for federal/state statutes (`fetch_statute_summary`)
  - **CourtListener / PACER / Geo APIs** for deadlines and court info (`check_deadlines`)
  - **Migration to OpenAI:** Replace Gemini API with OpenAI API for synthesizing live search results.
- **Outputs:**
  - **[DELETE]** `mcp_server/data/statutes.json`
  - **[DELETE]** `mcp_server/data/legal_aid_orgs.json`
  - **[MODIFY]** `mcp_server/server.py` (Implement `search_legal_aid_orgs`, `fetch_statute_summary`, and `check_deadlines` using the specified external APIs via OpenAI instead of Gemini)
  - **[MODIFY]** `requirements.txt` (Swap `google-genai` for `openai`)

### Phase 2: ADK Agent Port
- **Task:** Port the OpenAI logic to the ADK `Agent` and `McpToolset` architecture.
- **Outputs:**
  - `legal_triage/schemas.py`: Ported Pydantic schemas.
  - `legal_triage/prompt_loader.py`: System prompt loading mechanism.
  - `legal_triage/intake.py`: Updated intake generator tool.
  - `legal_triage/agent.py`: Root `triage_orchestrator` with `issue_classifier` and `jurisdiction_resolver` sub-agents, mapped to use the MCP tools.

### Phase 3: Enforced Guardrails
- **Task:** Implement deterministic callback shields around the LLM agents based on `prompts/guardrails.MD`.
- **Outputs:**
  - `legal_triage/callbacks.py`:
    - `crisis_interceptor` (instant Emergency Hotline bypass on DV/crisis keywords)
    - `output_guard` (appends mandatory disclaimers and rewrites case-outcome predictions like "you will win")
    - `confidence_gate` (state machine blocking downstream tool calls if classifier confidence is < 0.7)

### Phase 4: Cleanup + Smoke Tests
- **Task:** Remove legacy OpenAI files and add data-layer tests.
- **Outputs:**
  - **[DELETE]** `tools/` and `agent/` folders.
  - **[NEW]** `tests/test_smoke.py` (testing MCP lookup logic and doc generation).

### Phase 5 & 6: Documentation Drafts (Kaggle Ready)
- **Task:** Write the required README and the Kaggle Capstone writeup.
- **Outputs:**
  - `README.md` (detailed architecture and "Production Scaling Plan" covering PostgreSQL/Redis/Celery/React).
  - `docs/writeup.md` (Kaggle submission writeup).

### Phase 7: Video Script & Submission (User Task)
- **Task:** Record a 5-minute video demonstrating the local execution trace via `adk web` (happy path, guardrail trigger, crisis intercept, and live MCP API lookup).

---

## Verification Plan

### Automated Tests
- `pytest tests/test_smoke.py` to ensure local lookup methods and document rendering work correctly.

### Manual Verification Scenarios (via `adk web` / `adk run`)
1. **Wage theft (Happy Path):** Triggers `issue_classifier` -> `jurisdiction_agent` -> Dynamic MCP lookup -> successful intake markdown.
2. **External API Search (Live Search Path):** Ensure the MCP dynamically queries the LSC/LawHelp and Cornell LII APIs to return actual organizations and statute summaries for any arbitrary state (e.g. Florida) or issue type.
3. **"Will I win?" (Guardrail Trigger):** Output guard replaces outcome prediction with safe redirect + disclaimer.
4. **Crisis / DV Phrasing (Bypass):** Instantly triggers hotline response with no LLM model call in the trace logs.
