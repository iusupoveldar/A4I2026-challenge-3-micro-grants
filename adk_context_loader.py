"""
Root-level re-export of the Dynamic Guideline Loader (`ADK/adk_context_loader.py`).

Allows seamless imports via `import adk_context_loader` from the repository root
as well as `from ADK import adk_context_loader`.
"""

from ADK.adk_context_loader import (
    ADKContextLoader,
    MarkdownSection,
    RedTeamVectorSpec,
    build_system_prompt_with_adk_docs,
    get_agent_rubric,
    get_context_audit_summary,
    get_loader,
    get_red_team_defenses,
    get_red_team_vectors_structured,
    get_scoring_formulas,
    get_system_instructions,
    load_adk_guidelines,
    resolve_docs_directory,
)

__all__ = [
    "ADKContextLoader",
    "MarkdownSection",
    "RedTeamVectorSpec",
    "build_system_prompt_with_adk_docs",
    "get_agent_rubric",
    "get_context_audit_summary",
    "get_loader",
    "get_red_team_defenses",
    "get_red_team_vectors_structured",
    "get_scoring_formulas",
    "get_system_instructions",
    "load_adk_guidelines",
    "resolve_docs_directory",
]
