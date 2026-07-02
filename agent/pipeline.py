import sys
from tools.classifier import classify_legal_issue
from tools.jurisdiction import resolve_jurisdiction
from tools.mapper import fetch_statute_summary
from tools.resource_router import search_legal_aid_orgs
from tools.intake import generate_intake_doc

def legal_issue_pipeline(user_input: str) -> str:
    classified_issue = classify_legal_issue(user_input)
    jurisdiction_info = resolve_jurisdiction(user_input)
    statute_summaries = [
        fetch_statute_summary(s["name"], s.get("citation"))
        for s in jurisdiction_info["statutes"]
    ]
    org_results = search_legal_aid_orgs(
        classified_issue["primary_domain"],
        classified_issue["sub_type"],
        jurisdiction_info["jurisdiction"]["state"],
        jurisdiction_info["jurisdiction"].get("city"),
        urgency=classified_issue["urgency"],
    )
    return generate_intake_doc({
        "user_input": user_input,
        "classification": classified_issue,
        "jurisdiction": jurisdiction_info,
        "statute_summaries": statute_summaries,
        "referrals": org_results,
    })

if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "I was laid off from my job and I need help finding a new one."
    print(legal_issue_pipeline(message))