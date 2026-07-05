import sys
from tools.classifier import classify_legal_issue
from tools.jurisdiction import resolve_jurisdiction
from tools.mapper import fetch_statute_summary
from tools.resource_router import search_legal_aid_orgs
from tools.intake import generate_intake_doc


GUARDRAILS = open("prompts/guardrails.MD").read()

CLASSIFIER_SYSTEM = GUARDRAILS + "\n\n" + open("prompts/classifier.MD").read()
RESOLVER_SYSTEM = GUARDRAILS + "\n\n" + open("prompts/jurisdiction_resolver.MD").read()
ROUTER_SYSTEM = GUARDRAILS + "\n\n" + open("prompts/resource_router.MD").read()
DRAFTER_SYSTEM = GUARDRAILS + "\n\n" + open("prompts/intake_drafter.MD").read()
ORCHESTRATOR_SYSTEM = GUARDRAILS + "\n\n" + open("prompts/triage_agent.MD").read()



SAMPLE_USER_INPUT = "I work at a restaurant in San Francisco, California. My employer stopped paying me about two months ago, and last week they fired me after I asked about my missing paychecks. I have some pay stubs, text messages with my manager, and a termination email. I'm not sure what to do next or how soon I need to act."

if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "I was laid off from my job and I need help finding a new one."
    
    classifier_result = classify_legal_issue(SAMPLE_USER_INPUT)
    
    
    
    domain = classifier_result.get("primary_domain", "not found")
    sub_type = classifier_result.get("sub_type", "not found")
    urgency = classifier_result.get("urgency", "not found")
    flags = classifier_result.get("ambiguity_flags", [])
    keywords = classifier_result.get("keywords_matched", [])

    jurisdiction_result = resolve_jurisdiction(domain, sub_type, urgency, flags, keywords)

    relevant_court = jurisdiction_result["court_info"]["relevant_court"]
    statutes = jurisdiction_result["statutes"]

    print(f"Relevant Court: {relevant_court}")
    print(f"Statutes: {statutes}")


    