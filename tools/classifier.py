


def classify_legal_issue(user_input: str) -> dict:

    return {

        "primary_domain" : "employment",
        "sub_type": "unemployment",
        "confidence": 0.9,
        "urgency": "high",
        "ambiguity_flags": ["multiple_domains", "jurisdiction_unclear"],
        "secondary_domains": ["contract", "discrimination", "wage_and_hour", "non_compete", "class_action"],
        "keywords_matched": ["unemployment", "layoff", "termination", "severance", "retirement"],


    }