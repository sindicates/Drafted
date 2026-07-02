from typing import Optional


def search_legal_aid_orgs(
    issue_type: str,
    sub_type: str,
    state: str,
    city: Optional[str] = None,
    zip_code: Optional[str] = None,
    urgency: str = "medium",
) -> dict:
    return {
        "results": [
            {
                "org_name": "Legal Aid at Work",
                "address": "San Francisco, CA",
                "phone": "(415) 864-8848",
                "website": "https://legalaidatwork.org",
                "issue_types": ["labor", "employment", "wage theft"],
                "eligibility_notes": (
                    "Generally serves individuals at or below 125% of the federal poverty level"
                ),
                "intake_process": "Call intake line Mon-Fri 9am-5pm",
                "capacity_signal": "moderate_wait",
                "urgency_capable": True,
            },
            {
                "org_name": "Bay Area Legal Aid",
                "address": "San Francisco, CA",
                "phone": "(800) 551-5554",
                "website": "https://baylegal.org",
                "issue_types": ["labor", "housing", "consumer"],
                "eligibility_notes": "Income-based eligibility; call to confirm if you qualify",
                "intake_process": "Apply online or call hotline for eligibility screening",
                "capacity_signal": "unknown",
                "urgency_capable": True,
            },
            {
                "org_name": "Legal Aid Foundation of Los Angeles",
                "address": "Los Angeles, CA",
                "phone": "(800) 399-4529",
                "website": "https://lafla.org",
                "issue_types": ["employment", "wage theft", "retaliation"],
                "eligibility_notes": "Prioritizes low-income clients; may refer some callers",
                "intake_process": "Phone intake and web contact form",
                "capacity_signal": "high_wait",
                "urgency_capable": False,
            },
        ],
        "query": {
            "issue_type": issue_type,
            "sub_type": sub_type,
            "state": state,
            "city": city,
            "zip_code": zip_code,
            "urgency": urgency,
        },
    }
