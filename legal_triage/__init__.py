"""
legal_triage — ADK Legal-Aid Triage Agent Package
==================================================
The ADK runner discovers the root agent by importing this package and looking
for `root_agent` at the top level. This __init__.py re-exports it.
"""

from legal_triage.agent import root_agent

__all__ = ["root_agent"]
