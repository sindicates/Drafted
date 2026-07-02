from tools.classifier import classify_legal_issue
from tools.jurisdiction import resolve_jurisdiction
from tools.mapper import fetch_statute_summary
from tools.resource_router import search_legal_aid_orgs
from tools.intake import build_intake_response

def legal_issue_pipeline(user_input: str) -> str:
    classified_issue = classify_legal_issue(user_input)

    jurisdiction_info = resolve_jurisdiction()
    statute_summary = fetch_statute_summary(classified_issue["primary_domain"])
    org_results = search_legal_aid_orgs(classified_issue["primary_domain"], classified_issue["sub_type"], jurisdiction_info["jurisdiction"]["state"])
    intake_response = generate_intake_doc(user_input, classified_issue, jurisdiction_info, statute_summary, org_results)

    return intake_response

print(classify_legal_issue("I was laid off from my job and I need help finding a new one."))