
def resolve_jurisdiction(usr_input: str) -> dict:
    return {
        "jurisdiction": {
            "state": "California",
            "city": "<city or null>",
            "county": "San Francisco County",
            "federal_circuit": "9th Circuit",
            "state_court_system": "California Superior Court"
        },
        "statutes": [
            {
            "name": "California Labor Code",
            "citation": "California Labor Code § 1194",
            "level": "state",
            "coverage_summary": "The California Labor Code is a comprehensive set of laws that govern the employment relationship between employers and employees in California.",
            "statute_of_limitations": "4 years",
            "sol_notes": "The SOL for wage claims is 4 years from the date of the last pay period.",
            "relevant_agency": "California Department of Industrial Relations",
            "agency_complaint_url": "https://www.dir.ca.gov/complaints/"
            }
        ],
        "local_ordinances": [
            {
            "name": "San Francisco Fair Chance Ordinance",
            "jurisdiction": "San Francisco",
            "coverage_summary": "The San Francisco Fair Chance Ordinance is a law that prohibits employers from discriminating against job applicants or employees based on their criminal history.",
            "source_url": "https://www.sfgov.org/sf/content/fair-chance-ordinance"
            }
        ],
        "court_info": {
            "relevant_court": "San Francisco Superior Court",
            "self_help_url": "https://www.sfsuperiorcourt.org/self-help",
            "filing_fee_waiver": "The San Francisco Superior Court offers a filing fee waiver for certain cases."
        },
        "urgency_notes": None
    }