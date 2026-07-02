from typing import Optional


def fetch_statute_summary(statute_name: str, citation: Optional[str] = None) -> dict:
    normalized_name = statute_name.lower().strip()

    if "labor code" in normalized_name:
        summary = (
            "This law generally governs wage protections, minimum labor standards, "
            "and employee rights in California workplaces. It provides a framework "
            "for bringing claims related to unpaid wages and similar labor disputes."
        )
        sol = "4 years"
        sol_notes = (
            "Claims are commonly subject to a 4-year period for certain wage-related "
            "actions, but deadlines can vary by claim type and procedure."
        )
    else:
        summary = (
            "This law generally sets rules and protections relevant to the legal issue "
            "category identified in triage. A licensed attorney can assess whether it "
            "applies to a specific situation."
        )
        sol = "Unknown"
        sol_notes = "Statute of limitations depends on claim type and forum."

    return {
        "statute_name": statute_name,
        "citation": citation or "California Labor Code § 1194",
        "plain_language_summary": summary,
        "statute_of_limitations": sol,
        "sol_notes": sol_notes,
    }