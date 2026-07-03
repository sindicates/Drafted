import sys
from tools.classifier import classify_legal_issue
from tools.jurisdiction import resolve_jurisdiction
from tools.mapper import fetch_statute_summary
from tools.resource_router import search_legal_aid_orgs
from tools.intake import generate_intake_doc


GUARDRAILS = open("prompts/guardrails.MD").read()

CLASSIFIER_SYSTEM = GUARDRAILS + "\n\n" + open("capstone-project/prompts/classifier.MD").read()
RESOLVER_SYSTEM = GUARDRAILS + "\n\n" + open("prompts/juisidction_resolver.MD").read()
ROUTER_SYSTEM = GUARDRAILS + "\n\n" + open("prompts/resource_router.MD").read()
DRAFTER_SYSTEM = GUARDRAILS + "\n\n" + open("prompts/intake_drafter.MD").read()
ORCHESTRATOR_SYSTEM = GUARDRAILS + "\n\n" + open("prompts/triage_agent.MD").read()





if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "I was laid off from my job and I need help finding a new one."
    
    print(CLASSIFIER_SYSTEM)