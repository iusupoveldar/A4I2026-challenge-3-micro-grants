"""
Dynamic Guideline Loader for the Ecosystem & Demand-Anchored Micro-Grant ADK.

Reads and indexes all Markdown (.md) specification files inside `./ADK/DOCS`
(`./ADK/docs`) at startup and exposes structured helper functions so specialized
agents and deterministic tools can inject exact mathematical guidelines, piecewise
thresholds, and Red-Team verification rules into runtime context and audit logs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parent.parent


def resolve_docs_directory(adk_dir: Optional[str] = None) -> Path:
    """
    Resolves the canonical `./ADK/DOCS` (`./ADK/docs`) directory regardless of
    current working directory or OS filesystem case-sensitivity.
    """
    candidates: List[Path] = []
    if adk_dir:
        provided = Path(adk_dir)
        candidates.extend([
            provided,
            provided / "docs",
            provided / "DOCS",
            REPO_ROOT / provided,
            REPO_ROOT / provided / "docs",
            REPO_ROOT / provided / "DOCS",
        ])

    candidates.extend([
        REPO_ROOT / "ADK" / "docs",
        REPO_ROOT / "ADK" / "DOCS",
        Path.cwd() / "ADK" / "docs",
        Path.cwd() / "ADK" / "DOCS",
        Path(__file__).resolve().parent / "docs",
        Path(__file__).resolve().parent / "DOCS",
    ])

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            md_files = list(candidate.glob("*.md"))
            if md_files:
                return candidate.resolve()

    raise FileNotFoundError(
        f"Could not locate ADK Markdown guidelines directory (searched from '{adk_dir or 'ADK/docs'}')."
    )


@dataclass(frozen=True)
class MarkdownSection:
    """Indexed Markdown section with heading hierarchy and extracted LaTeX blocks."""

    file_name: str
    heading: str
    level: int
    content: str
    display_equations: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RedTeamVectorSpec:
    """Structured representation of a Red-Team attack vector from 02_RED_TEAM_AND_DEFENSE_PLAYBOOK.md."""

    vector_number: int
    title: str
    attack_description: str
    failure_scenario: str
    algorithmic_defense: str
    residual_risk_and_verification: str
    executive_qa_response: str
    raw_markdown: str


class ADKContextLoader:
    """
    Single-source-of-truth loader and indexer for all `.md` files in `./ADK/DOCS`.
    """

    AGENT_RUBRIC_MAP: Dict[str, Dict[str, Any]] = {
        "supply_provenance_agent": {
            "role": "Supply & Provenance Agent",
            "source_files": [
                "01_ARCHITECTURE_AND_TRIAGE_FRAMEWORK.md",
                "02_RED_TEAM_AND_DEFENSE_PLAYBOOK.md",
                "03_BEYOND_DATASET_ENHANCEMENT_MODEL.md",
                "SYSTEM_INSTRUCTIONS.md",
            ],
            "section_keywords": [
                "Track 2: Commercial Network Contagion",
                "Root / Parent Supplier Multiplier",
                "Dimension 5: Upstream / Parent Supplier",
                "Vector 1: Inferred vs. Actual Supply Links",
                "Vector 2: External Distributor",
                "Vector 8: Corporate & Aggregation Leakage",
                "Vector 9: Un-Applied Bottleneck Blindness",
            ],
            "mandate": (
                "Evaluate B2B network topology, upstream parent/root suppliers (xi_i, mu_i, omega_parent), "
                "local redundancy discount (r_j^-0.5), external distributor substitutability friction (theta_ext), "
                "4-digit NAICS B2B disaggregation, un-applied upstream corridor bottlenecks, and mandatory "
                "[MODELED] vs. [VERIFIED] 1-invoice provenance verification gates."
            ),
        },
        "runway_sector_purity_agent": {
            "role": "Runway, Sector & Purity Agent",
            "source_files": [
                "01_ARCHITECTURE_AND_TRIAGE_FRAMEWORK.md",
                "02_RED_TEAM_AND_DEFENSE_PLAYBOOK.md",
                "03_BEYOND_DATASET_ENHANCEMENT_MODEL.md",
                "SYSTEM_INSTRUCTIONS.md",
            ],
            "section_keywords": [
                "Stage 0: Corporate Exclusion",
                "Dimension 1: Financial Buffer, Runway & Consecutive Bad-Quarter",
                "Dimension 2: Sector-Specific Macroeconomic Volatility",
                "Dimension 4: Small-Business Purity Score",
                "Vector 3: Strategic Gaming & Moral Hazard",
                "Vector 4: \"Walking Dead\" vs. \"Self-Insuring\"",
                "Vector 8: Corporate & Aggregation Leakage",
            ],
            "mandate": (
                "Enforce Stage 0 Corporate Exclusion Gate (E_corp in (0, 1)), evaluate financial runway "
                "logistic survival lift Delta P(g_i | r_i), non-monotonic survival bell curve Phi_runway(r_i), "
                "structural viability gate Theta_viable, sector volatility/margins (Omega_s, Psi_s, rho_s), "
                "and Small-Business Purity Score P_pure(i) across employee size, locations, ownership, and revenue."
            ),
        },
        "spatial_human_impact_agent": {
            "role": "Spatial Foot-Traffic & Human-Impact Agent",
            "source_files": [
                "00_CENTRAL_MARKET_EXECUTIVE_SUMMARY.md",
                "01_ARCHITECTURE_AND_TRIAGE_FRAMEWORK.md",
                "02_RED_TEAM_AND_DEFENSE_PLAYBOOK.md",
                "03_BEYOND_DATASET_ENHANCEMENT_MODEL.md",
                "SYSTEM_INSTRUCTIONS.md",
            ],
            "section_keywords": [
                "Track 1: Community Anchor",
                "Dimension 3: Total People Helped",
                "Vector 6: Spatial Blight & Two-Block Tipping Points",
                "Vector 7: Sector Starvation & Structural Bias",
            ],
            "mandate": (
                "Enforce 200m spatial critical-mass cluster rules (requiring >= 3 co-located storefronts if "
                "cluster vacancy risk > 35% to preserve pedestrian trip chaining and prevent stranded grants), "
                "compute Track 1 Community Anchor Score (S_anchor), Census Tract Equity Multiplier (M_equity), "
                "and Total People Helped per Grant Dollar (H_i, eta_i, S_people)."
            ),
        },
        "regime_orchestrator_agent": {
            "role": "Regime Stress-Test & Orchestrator Agent",
            "source_files": [
                "00_CENTRAL_MARKET_EXECUTIVE_SUMMARY.md",
                "01_ARCHITECTURE_AND_TRIAGE_FRAMEWORK.md",
                "02_RED_TEAM_AND_DEFENSE_PLAYBOOK.md",
                "03_BEYOND_DATASET_ENHANCEMENT_MODEL.md",
                "SYSTEM_INSTRUCTIONS.md",
            ],
            "section_keywords": [
                "Why Conventional Allocation Mechanisms Fail",
                "Recommended Portfolio Summary",
                "Extended Multi-Objective Prioritization Equation",
                "Unified Multi-Objective Optimization & Knapsack Formulation",
                "Vector 5: Partial-Grant Dilution Trap",
                "Vector 10: Weighting Arbitrariness & Sensitivity Bounds",
                "Summary of Grant Officer Verification Protocol",
            ],
            "mandate": (
                "Synthesize all specialist agent outputs, execute submodular multi-choice knapsack portfolio "
                "optimization across Regimes A (Hard Threshold), B (Concave Diminishing Returns), and C "
                "(Tiered Hybrid $10k/$5k) with Jaccard downstream overlap penalty, compute parameter invariance "
                "bounds and Robust Awardee Set S_robust, and generate the Red-Team Compliance Report."
            ),
        },
    }

    def __init__(self, adk_dir: Optional[str] = None) -> None:
        self.docs_dir: Path = resolve_docs_directory(adk_dir)
        self.documents: Dict[str, str] = {}
        self.sections: List[MarkdownSection] = []
        self.red_team_vectors: List[RedTeamVectorSpec] = []
        self._load_and_index()

    def _load_and_index(self) -> None:
        """Loads all .md files in self.docs_dir and indexes sections, equations, and Red-Team vectors."""
        for md_path in sorted(self.docs_dir.glob("*.md")):
            text = md_path.read_text(encoding="utf-8")
            self.documents[md_path.name] = text
            self.sections.extend(self._parse_sections(md_path.name, text))

        playbook_text = self.documents.get("02_RED_TEAM_AND_DEFENSE_PLAYBOOK.md", "")
        if playbook_text:
            self.red_team_vectors = self._parse_red_team_vectors(playbook_text)

    @staticmethod
    def _parse_sections(file_name: str, text: str) -> List[MarkdownSection]:
        """Splits a Markdown document into heading-delimited sections and extracts display math blocks."""
        heading_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
        matches = list(heading_pattern.finditer(text))
        parsed: List[MarkdownSection] = []

        if not matches:
            eqs = re.findall(r"\$\$(.*?)\$\$", text, flags=re.DOTALL)
            parsed.append(
                MarkdownSection(
                    file_name=file_name,
                    heading=file_name,
                    level=1,
                    content=text.strip(),
                    display_equations=[e.strip() for e in eqs],
                )
            )
            return parsed

        for idx, match in enumerate(matches):
            level = len(match.group(1))
            heading = match.group(2).strip()
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            eqs = re.findall(r"\$\$(.*?)\$\$", body, flags=re.DOTALL)
            parsed.append(
                MarkdownSection(
                    file_name=file_name,
                    heading=heading,
                    level=level,
                    content=body,
                    display_equations=[e.strip() for e in eqs],
                )
            )
        return parsed

    @staticmethod
    def _parse_red_team_vectors(playbook_text: str) -> List[RedTeamVectorSpec]:
        """Extracts all 10 Red-Team Attack Vectors and their (a)-(e) subsections."""
        vector_header_re = re.compile(r"^##\s+Vector\s+(\d+):\s*(.+)$", re.MULTILINE)
        matches = list(vector_header_re.finditer(playbook_text))
        vectors: List[RedTeamVectorSpec] = []

        def _extract_sub(body: str, marker: str, next_markers: List[str]) -> str:
            sub_re = re.compile(rf"###\s*\({marker}\)[^\n]*\n", re.IGNORECASE)
            m = sub_re.search(body)
            if not m:
                return ""
            start_idx = m.end()
            end_idx = len(body)
            for nm in next_markers:
                nm_re = re.compile(rf"###\s*\({nm}\)|^---$", re.IGNORECASE | re.MULTILINE)
                nm_match = nm_re.search(body[start_idx:])
                if nm_match:
                    end_idx = min(end_idx, start_idx + nm_match.start())
            return body[start_idx:end_idx].strip()

        for idx, match in enumerate(matches):
            vec_num = int(match.group(1))
            title = match.group(2).strip()
            start = match.start()
            # Stop at next vector or at '## Summary of Grant Officer Verification Protocol'
            if idx + 1 < len(matches):
                end = matches[idx + 1].start()
            else:
                summary_match = re.search(
                    r"^##\s+Summary of Grant Officer Verification Protocol",
                    playbook_text[start:],
                    flags=re.MULTILINE,
                )
                end = start + summary_match.start() if summary_match else len(playbook_text)

            raw_block = playbook_text[start:end].strip()
            vectors.append(
                RedTeamVectorSpec(
                    vector_number=vec_num,
                    title=title,
                    attack_description=_extract_sub(raw_block, "a", ["b", "c", "d", "e"]),
                    failure_scenario=_extract_sub(raw_block, "b", ["c", "d", "e"]),
                    algorithmic_defense=_extract_sub(raw_block, "c", ["d", "e"]),
                    residual_risk_and_verification=_extract_sub(raw_block, "d", ["e"]),
                    executive_qa_response=_extract_sub(raw_block, "e", []),
                    raw_markdown=raw_block,
                )
            )
        return vectors

    def get_all_documents(self) -> Dict[str, str]:
        """Returns a dictionary mapping filename -> full Markdown content."""
        return dict(self.documents)

    def get_system_instructions(self) -> str:
        """Returns the exact contents of `SYSTEM_INSTRUCTIONS.md`."""
        return self.documents.get("SYSTEM_INSTRUCTIONS.md", "")

    def get_red_team_defenses(self, vector_number: Optional[int] = None) -> str:
        """
        Returns the Red-Team & Defense Playbook guidelines. If `vector_number` (1-10)
        is specified, returns that specific attack vector and its 5 subsections;
        otherwise returns the complete Red-Team defense specification and 5-Step Field Protocol.
        """
        if vector_number is not None:
            for vec in self.red_team_vectors:
                if vec.vector_number == vector_number:
                    return vec.raw_markdown
            raise ValueError(f"Red-Team Vector {vector_number} not found (valid range: 1..10).")
        return self.documents.get("02_RED_TEAM_AND_DEFENSE_PLAYBOOK.md", "")

    def get_scoring_formulas(self, dimension: Optional[str] = None) -> str:
        """
        Extracts all mathematical equations, piecewise functions, and threshold rules
        from `01_ARCHITECTURE_AND_TRIAGE_FRAMEWORK.md` and `03_BEYOND_DATASET_ENHANCEMENT_MODEL.md`.
        Optionally filters by a dimension or keyword (e.g., 'runway', 'volatility', 'people',
        'purity', 'cascade', 'knapsack', 'anchor').
        """
        formula_files = [
            "01_ARCHITECTURE_AND_TRIAGE_FRAMEWORK.md",
            "03_BEYOND_DATASET_ENHANCEMENT_MODEL.md",
        ]
        blocks: List[str] = []
        query = dimension.lower().strip() if dimension else None

        for sec in self.sections:
            if sec.file_name not in formula_files:
                continue
            has_math = bool(sec.display_equations) or ("$" in sec.content)
            if not has_math:
                continue
            if query and (query not in sec.heading.lower() and query not in sec.content.lower()):
                continue
            blocks.append(f"<!-- Source: {sec.file_name} | Section: {sec.heading} -->\n{sec.content}")

        if not blocks:
            # Fallback to returning both mathematical specification documents in full
            return "\n\n".join(
                f"# {fname}\n{self.documents[fname]}"
                for fname in formula_files
                if fname in self.documents
            )
        return "\n\n".join(blocks)

    def get_agent_rubric(self, agent_name: str) -> str:
        """
        Builds a specialized context rubric for one of the 4 ADK agents by combining
        `SYSTEM_INSTRUCTIONS.md`, the agent's operational mandate, and the exact
        Markdown sections from `./ADK/DOCS/*.md` mapped to that agent.
        """
        normalized = agent_name.strip().lower().replace("-", "_").replace(" ", "_")
        # Alias matching
        alias_map = {
            "supply": "supply_provenance_agent",
            "supply_and_provenance": "supply_provenance_agent",
            "supply_provenance": "supply_provenance_agent",
            "supply_provenance_agent": "supply_provenance_agent",
            "runway": "runway_sector_purity_agent",
            "runway_sector_purity": "runway_sector_purity_agent",
            "runway_sector_and_purity": "runway_sector_purity_agent",
            "runway_sector_purity_agent": "runway_sector_purity_agent",
            "spatial": "spatial_human_impact_agent",
            "spatial_foot_traffic": "spatial_human_impact_agent",
            "spatial_human_impact": "spatial_human_impact_agent",
            "spatial_human_impact_agent": "spatial_human_impact_agent",
            "orchestrator": "regime_orchestrator_agent",
            "regime_stress_test": "regime_orchestrator_agent",
            "regime_stress_test_orchestrator": "regime_orchestrator_agent",
            "regime_stress_test_orchestrator_agent": "regime_orchestrator_agent",
            "regime_orchestrator": "regime_orchestrator_agent",
            "regime_orchestrator_agent": "regime_orchestrator_agent",
        }
        canonical_key = alias_map.get(normalized)
        if not canonical_key:
            for key in self.AGENT_RUBRIC_MAP:
                if key in normalized or normalized in key:
                    canonical_key = key
                    break
        if not canonical_key:
            raise ValueError(
                f"Unknown agent_name '{agent_name}'. Valid agents: {list(self.AGENT_RUBRIC_MAP.keys())}"
            )

        spec = self.AGENT_RUBRIC_MAP[canonical_key]
        matched_sections: List[str] = []
        for sec in self.sections:
            if sec.file_name not in spec["source_files"]:
                continue
            if any(kw.lower() in sec.heading.lower() for kw in spec["section_keywords"]):
                matched_sections.append(
                    f"<guideline_section file=\"{sec.file_name}\" heading=\"{sec.heading}\">\n"
                    f"{sec.content}\n"
                    f"</guideline_section>"
                )

        sys_inst = self.get_system_instructions()
        compiled_sections = "\n\n".join(matched_sections)
        return (
            f"# AGENT SPECIFICATION: {spec['role']} (`{canonical_key}`)\n\n"
            f"## Core Mandate\n{spec['mandate']}\n\n"
            f"## Global System Instructions (`SYSTEM_INSTRUCTIONS.md`)\n{sys_inst}\n\n"
            f"## Authoritative Domain Guidelines (`./ADK/DOCS/*.md`)\n{compiled_sections}"
        )

    def get_context_audit_summary(self) -> Dict[str, Any]:
        """
        Produces a structured audit summary of every `.md` file discovered in `./ADK/DOCS`,
        including line counts, section counts, extracted LaTeX equations, and Red-Team vectors.
        """
        file_summaries: Dict[str, Any] = {}
        for fname, content in self.documents.items():
            file_secs = [s for s in self.sections if s.file_name == fname]
            all_eqs = [eq for s in file_secs for eq in s.display_equations]
            file_summaries[fname] = {
                "line_count": len(content.splitlines()),
                "char_count": len(content),
                "section_count": len(file_secs),
                "display_equation_count": len(all_eqs),
                "headings": [s.heading for s in file_secs],
                "equations": all_eqs,
            }

        return {
            "docs_directory": str(self.docs_dir),
            "total_markdown_files": len(self.documents),
            "files": file_summaries,
            "red_team_vector_count": len(self.red_team_vectors),
            "red_team_vectors": [
                {
                    "vector_number": v.vector_number,
                    "title": v.title,
                    "has_all_5_subsections": all([
                        bool(v.attack_description),
                        bool(v.failure_scenario),
                        bool(v.algorithmic_defense),
                        bool(v.residual_risk_and_verification),
                        bool(v.executive_qa_response),
                    ]),
                }
                for v in self.red_team_vectors
            ],
        }


# Singleton cache for fast repeated tool/agent calls
_DEFAULT_LOADER: Optional[ADKContextLoader] = None


def get_loader(adk_dir: Optional[str] = None) -> ADKContextLoader:
    """Returns a cached or freshly initialized `ADKContextLoader` instance."""
    global _DEFAULT_LOADER
    if adk_dir is not None:
        return ADKContextLoader(adk_dir=adk_dir)
    if _DEFAULT_LOADER is None:
        _DEFAULT_LOADER = ADKContextLoader()
    return _DEFAULT_LOADER


def load_adk_guidelines(adk_dir: Optional[str] = None) -> Dict[str, str]:
    """Reads all .md files in `./ADK/DOCS` and returns a map of filename -> content."""
    return get_loader(adk_dir).get_all_documents()


def get_red_team_defenses(
    vector_number: Optional[int] = None,
    adk_dir: Optional[str] = None,
) -> str:
    """Returns Red-Team defense specifications from `02_RED_TEAM_AND_DEFENSE_PLAYBOOK.md`."""
    return get_loader(adk_dir).get_red_team_defenses(vector_number=vector_number)


def get_red_team_vectors_structured(adk_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns all 10 Red-Team vectors as structured dictionaries with subsections (a)-(e)."""
    loader = get_loader(adk_dir)
    return [
        {
            "vector_number": v.vector_number,
            "title": v.title,
            "a_attack": v.attack_description,
            "b_scenario": v.failure_scenario,
            "c_defense": v.algorithmic_defense,
            "d_verification": v.residual_risk_and_verification,
            "e_executive_qa": v.executive_qa_response,
        }
        for v in loader.red_team_vectors
    ]


def get_scoring_formulas(
    dimension: Optional[str] = None,
    adk_dir: Optional[str] = None,
) -> str:
    """Returns exact mathematical formulas and piecewise definitions from `./ADK/DOCS`."""
    return get_loader(adk_dir).get_scoring_formulas(dimension=dimension)


def get_agent_rubric(agent_name: str, adk_dir: Optional[str] = None) -> str:
    """Returns the specialized Markdown guideline rubric for `agent_name`."""
    return get_loader(adk_dir).get_agent_rubric(agent_name=agent_name)


def get_system_instructions(adk_dir: Optional[str] = None) -> str:
    """Returns the core orchestrator instructions from `SYSTEM_INSTRUCTIONS.md`."""
    return get_loader(adk_dir).get_system_instructions()


def get_context_audit_summary(adk_dir: Optional[str] = None) -> Dict[str, Any]:
    """Returns a complete audit summary of all indexed `.md` files in `./ADK/DOCS`."""
    return get_loader(adk_dir).get_context_audit_summary()


def _sanitize_adk_template_braces(text: str) -> str:
    """
    Sanitizes curly braces `{` and `}` in system instructions so Google ADK's
    `inject_session_state` template parser does not mistake LaTeX subscripts
    (e.g., `\\theta_{\\text{ext}}`) or GQL quantifiers (`->{1,2}`) for missing
    session context variables.
    """
    return text.replace("{", "(").replace("}", ")")


def build_system_prompt_with_adk_docs(
    base_system_prompt: str = "",
    adk_dir: Optional[str] = None,
    agent_name: Optional[str] = None,
) -> str:
    """
    Appends `./ADK/DOCS/*.md` specifications directly into an agent's system context.
    If `agent_name` is provided, injects that agent's targeted rubric alongside
    `SYSTEM_INSTRUCTIONS.md`; otherwise injects all `.md` files in `./ADK/DOCS`.
    """
    loader = get_loader(adk_dir)
    if agent_name:
        rubric = loader.get_agent_rubric(agent_name)
        return _sanitize_adk_template_braces(f"{base_system_prompt}\n\n{rubric}".strip())

    docs = loader.get_all_documents()
    compiled_docs = "\n\n".join(
        f"<adk_guideline file=\"{filename}\">\n{content}\n</adk_guideline>"
        for filename, content in docs.items()
    )
    prefix = f"{base_system_prompt}\n\n" if base_system_prompt else ""
    return _sanitize_adk_template_braces(
        f"{prefix}# LOADED ./ADK/DOCS/*.md SPECIFICATIONS\n{compiled_docs}"
    )
