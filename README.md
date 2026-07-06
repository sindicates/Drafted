# Drafted (Legal Aid Triage)

**Drafted** is an automated legal triage tool designed to help users prepare for a consultation with a licensed attorney. By describing their situation, users receive a tailored intake summary containing the relevant facts, potential legal issues, applicable statutes, and a list of local legal aid organizations. 

> **Disclaimer**: This system provides automated analysis for legal aid intake purposes. It does not constitute official legal advice. Only a licensed attorney can give legal advice about specific situations.

## Architecture

The project is built using:
- **Frontend**: A custom, distinctive UI built with pure HTML, CSS, and Vanilla JavaScript (featuring a deep sage and brass palette, and markdown rendering).
- **Backend API**: A lightweight **FastAPI** server (`api.py`) bridging the frontend to the agent layer.
- **Agent Framework**: Google's **Agent Development Kit (ADK)**. A multi-agent orchestration pipeline (`triage_orchestrator`) that delegates to sub-agents (`issue_classifier`, `jurisdiction_resolver`).
- **Tools**: Model Context Protocol (MCP) tools integration for looking up state statutes and fetching local legal aid resources.

## Prerequisites

- Python 3.11+
- `pip`
- Valid API keys (Google Gemini / OpenAI depending on your model configurations).

## Setup Instructions

1. **Clone the repository and enter the directory**:
   ```bash
   cd capstone-project
   ```

2. **Set up the virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Ensure you have a `.env.local` or `.env` file at the root of the project (or in the `legal_triage/` directory) containing your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Start the API Server**:
   ```bash
   uvicorn api:app --reload
   # or simply
   # python api.py
   ```

6. **Access the App**:
   Open your browser and navigate to [http://localhost:8000](http://localhost:8000).

## Project Structure

- `frontend/`: Contains the UI assets (`index.html`, `style.css`, `app.js`).
- `legal_triage/`: Contains the core ADK agent definitions, instructions, and tools.
- `mcp_server/`: The Model Context Protocol (MCP) server used by the agent to interface with external resources.
- `api.py`: The FastAPI server that orchestrates the backend and serves the frontend.
