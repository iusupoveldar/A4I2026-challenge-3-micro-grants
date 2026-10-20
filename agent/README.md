# A4I 2026 Micro-Grant Triage ADK — Multi-Agent Breakdown & Usage Guide

This directory (`agent/`) and the companion `agents/`, `tools/`, and `ADK/` packages implement the **Ecosystem & Demand-Anchored Micro-Grant Agent Development Kit (ADK)** for the SoMa & Mission Street Corridor (`$50,000` OEWD Emergency Stabilization Pool).

Instead of allowing an LLM to guess scores or rank businesses by raw degree centrality, this architecture dynamically loads its domain rules from [`./ADK/DOCS/*.md`](../ADK/DOCS) at startup, traverses the multi-hop **BigQuery Property Graph (`GRAPH_TABLE`)**, executes pure deterministic quantitative economics tools in [`tools/scoring_engine.py`](../tools/scoring_engine.py), and verifies every grant allocation against a **10-Vector Red-Team Compliance Suite**.

---

## 1. The 4 Named ADK Agents (Selectable Individually or as a Full Pipeline)

Every agent in this ADK has an explicit **ADK Agent ID (`name`)** and **Human-Readable Display Name (`display_name`)**, and can be selected and invoked either as a coordinated multi-agent hierarchy or as an isolated domain specialist:

| # | ADK Agent ID (`name`) | Display Name (`display_name`) | Role & Primary Responsibility | Standalone ADK Package |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `Regime_Stress_Test_Orchestrator_Agent` | **Regime Stress-Test & Orchestrator Agent** | **Root Coordinator:** Synthesizes all 3 domain sub-agents, runs portfolio optimization across 3 funding regimes (`Concentrate Top 5`, `Spread Across 8`, `Tiered Hybrid`), prevents partial-grant dilution, and generates the 10-Vector Red-Team Compliance Report. | [`agents/Regime_Stress_Test_Orchestrator_Agent/`](../agents/Regime_Stress_Test_Orchestrator_Agent/agent.py) |
| **2** | `Supply_Provenance_Agent` | **Supply & Provenance Agent** | **Sub-Agent 1 (B2B Supply & Provenance):** Evaluates multi-hop upstream parent/root suppliers (`Sour Flour`, `Cumaica Coffee`), trophic cascade multipliers ($M_{\text{trophic}}$), substitutability friction ($\sigma_{\text{sub}}$), submodular buyer overlap deduplication, and verified invoice provenance gates (`ttxid` vs. modeled edges). | [`agents/Supply_Provenance_Agent/`](../agents/Supply_Provenance_Agent/agent.py) |
| **3** | `Runway_Sector_Purity_Agent` | **Runway, Sector & Purity Agent** | **Sub-Agent 2 (Runway, Sector & Purity):** Enforces the Stage 0 Small-Business Purity Gate ($P_i = 0$ for corporate/private-equity entities), evaluates the asymmetric bell-shaped cash runway urgency curve $U_i(R_i)$, consecutive bad-quarter trajectory $T_i$, and sector volatility adjustments $V_{\text{sector}}$. | [`agents/Runway_Sector_Purity_Agent/`](../agents/Runway_Sector_Purity_Agent/agent.py) |
| **4** | `Spatial_Human_Impact_Agent` | **Spatial Foot-Traffic & Human-Impact Agent** | **Sub-Agent 3 (Spatial Cluster & Human Impact):** Calculates daily human beneficiaries per dollar ($H_i$), low-income neighborhood equity multipliers ($E_i \in [1.0, 1.35]$), and enforces the two-block storefront cluster critical-mass bonus ($J_{\text{clust}} = 1.20$ when $\ge 3$ co-located storefronts are preserved on 6th & Mission). | [`agents/Spatial_Human_Impact_Agent/`](../agents/Spatial_Human_Impact_Agent/agent.py) |

---

## 2. How to Use & Select Agents in the ADK

You can run and select any of the 4 named agents in **four ways**:

### Option A: Interactive Google ADK Web UI (`adk web`)
To see all **4 named agents** directly in the top-left **"Select an agent"** dropdown in the Google ADK Web UI, run:

```powershell
# Recommended: Launch adk web pointing at the multi-agent directory
adk web agents
```
*(Note: Running `adk web` from the repository root `.` also exposes `agent` and registers all 4 named agents in the dropdown once initialized.)*

In the `adk web` dropdown, you can select:
- **`Regime_Stress_Test_Orchestrator_Agent`** — Full multi-agent orchestration + 3-regime stress test + Red-Team audit.
- **`Supply_Provenance_Agent`** — Inspect upstream B2B root suppliers, multi-hop GQL cascades, and invoice provenance gates.
- **`Runway_Sector_Purity_Agent`** — Audit Stage 0 corporate disqualifications, cash-burn runway urgency, and survival lift curves.
- **`Spatial_Human_Impact_Agent`** — Audit daily human beneficiaries, neighborhood equity weights, and 6th & Mission cluster critical mass.

#### Choosing an Agent via Environment Variable (`ADK_AGENT_NAME`)
You can also bind the root `agent/` package to a specific named agent via `.env` or PowerShell before launching `adk web`:
```powershell
$env:ADK_AGENT_NAME="Supply_Provenance_Agent"
adk web
```

---

### Option B: Deterministic CLI Runner (`run_adk_test.py`) — No Cloud Credentials Required
You can test the entire ADK pipeline or select any individual agent from your terminal using [`run_adk_test.py`](../run_adk_test.py):

```powershell
# 1. List all 4 selectable ADK agents and their descriptions
python run_adk_test.py --list-agents

# 2. Run the full multi-agent pipeline (default: Regime_Stress_Test_Orchestrator_Agent)
python run_adk_test.py

# 3. Run a specific specialist sub-agent by ADK name or alias
python run_adk_test.py --agent Supply_Provenance_Agent
python run_adk_test.py --agent Runway_Sector_Purity_Agent
python run_adk_test.py --agent Spatial_Human_Impact_Agent

# 4. Run with custom budget or policy slider weights
python run_adk_test.py --agent Regime_Stress_Test_Orchestrator_Agent --budget 75000 --alpha 0.65
```

---

### Option C: Python API (`select_adk_agent` & `select_deterministic_agent`)
Import the selector functions directly from [`agents/regime_orchestrator_agent.py`](../agents/regime_orchestrator_agent.py) or [`agent/agent.py`](./agent.py):

```python
from agents.regime_orchestrator_agent import (
    list_available_agents,
    select_adk_agent,
    select_deterministic_agent,
)

# Inspect all 4 registered agents
for info in list_available_agents():
    print(info["agent_id"], "->", info["display_name"])

# 1. Get the Google ADK LlmAgent instance for any of the 4 named agents
adk_agent = select_adk_agent("Supply_Provenance_Agent")
print("Selected ADK Agent:", adk_agent.name)

# 2. Or run the deterministic Python evaluator for any of the 4 named agents
det_agent = select_deterministic_agent("Spatial_Human_Impact_Agent")
result = det_agent.evaluate_all()
```

---

### Option D: Interactive Executive Web Showcase (`ADK/index.html`)
Open [`ADK/index.html`](../ADK/index.html) in any browser (or serve via `python -m http.server 8080`). Use the **"Select Active ADK Agent"** dropdown in the left policy sidebar to switch between the 4 named agents in real time and inspect how each agent weights the corridor applicants and updates the Official Determination Memo.

---

## 3. Authentication & BigQuery Setup (`adk web` on Windows)

### 1. Configuring Gemini LLM Credentials for `adk web`
Each agent folder (`agent/.env` and `agents/<Agent_Name>/.env`) includes a pre-configured `.env` template. Choose **one** of the two modes:

- **Mode 1: Free Gemini API Key (Easiest for Local Windows Testing)**
  1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).
  2. Set it in [`agent/.env`](./.env) (or in PowerShell):
     ```env
     GOOGLE_GENAI_USE_VERTEXAI=FALSE
     GOOGLE_API_KEY=your_api_key_here
     ```
- **Mode 2: Google Cloud Vertex AI + Live BigQuery (`qwiklabs-gcp-04-486b161c6a8e`)**
  1. Install the [Google Cloud SDK (`gcloud`)](https://cloud.google.com/sdk/docs/install) and authenticate Application Default Credentials:
     ```powershell
     gcloud auth application-default login
     gcloud config set project qwiklabs-gcp-04-486b161c6a8e
     ```
  2. Set [`agent/.env`](./.env) to:
     ```env
     GOOGLE_GENAI_USE_VERTEXAI=TRUE
     GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-04-486b161c6a8e
     GOOGLE_CLOUD_LOCATION=us-central1
     ```

### 2. Live BigQuery Property Graph vs. Automatic Offline Fallback
The BigQuery connector in [`tools/bq_graph_connector.py`](../tools/bq_graph_connector.py) automatically checks if `GOOGLE_CLOUD_PROJECT` and ADC credentials are active:
- **When connected to BigQuery (`LIVE_BIGQUERY_GQL`)**: Executes multi-hop `GRAPH_TABLE(a4i_econ.LocalEconomy MATCH -[e:supplies_to]->{1,3})` queries and joins live node metrics.
- **When offline (`OFFLINE_VERIFIED_SNAPSHOT_FALLBACK`)**: Gracefully falls back to the verified 15-applicant SoMa/Mission corridor dataset in [`tools/scoring_engine.py`](../tools/scoring_engine.py) so every tool call succeeds with zero downtime.

---

## 4. Core Functionality Breakdown (The 5 Modules)

### Module 1: Dynamic Guideline Loader ([`ADK/adk_context_loader.py`](../ADK/adk_context_loader.py))
Reads and indexes all 5 Markdown specification files inside [`./ADK/DOCS/`](../ADK/DOCS) at startup so that prompts, formulas, and Red-Team audit logs are never hardcoded in prose:
- `GET_STARTED.md` — Executive mission & ecosystem preservation thesis
- `FIRST_PRINCIPLES_ENHANCEMENTS.md` — Mathematical equations & 6 first-principles enhancements
- `DECISION_ENGINE_SPEC.md` — Multi-agent architecture & tool specifications
- `RED_TEAM_DEFENSE_MATRIX.md` — 10 adversarial attack vectors & mathematical defenses
- `JUDGE_SCORING_ALIGNMENT.md` — Rubric alignment & verification gates

Key helper tools exposed to the agents:
- `get_scoring_formulas()` — Returns all 10 extracted mathematical formulas and constraints.
- `get_red_team_defenses(category_filter)` — Returns the 10 Red-Team attack vectors and deterministic defenses.
- `get_agent_rubric(agent_name)` — Injects the exact domain rubric for any of the 4 named agents.

---

### Module 2: Deterministic Math & Tool Engine ([`tools/scoring_engine.py`](../tools/scoring_engine.py))
LLM agents **never** compute scores in prose. All calculations are executed by strict, type-annotated Python functions:

1. **Stage 0 Purity & Eligibility Gate (`evaluate_purity_gate`)**:
   $$P_i \in \{0.00, 0.25, 0.65, 0.85, 1.00\}$$
   Hard-blocks corporate chains, private-equity rollups, and non-storefront SaaS offices ($P_i = 0 \implies \text{Score}_i = 0, \text{Grant}_i = \$0$), including **Starbucks Reserve #402**, **Westfield Retail Holdings**, **CloudScale AI**, and **6th Street Check Cashing Corp**.

2. **Asymmetric Bell-Shaped Runway Urgency (`calculate_runway_urgency`)**:
   $$U_i(R_i) = \begin{cases} 0.35 + 0.65 \cdot (R_i / 0.50), & 0 < R_i < 0.50 \\ 1.00, & 0.50 \le R_i \le 1.25 \\ \exp(-1.15 \cdot (R_i - 1.25)), & R_i > 1.25 \end{cases}$$
   Peaks in the `0.50 - 1.25` quarter rescue window where a `$5k–$10k` micro-grant prevents default, while discounting already-insolvent (`<0.5q`) or comfortable (`>2.0q`) applicants.

3. **Grant-Relative Survival Lift (`calculate_survival_lift`)**:
   $$\Delta S_i(g_i) = \sigma(2.5 \cdot (R_i + \Delta R_i(g_i) - 1.0)) - \sigma(2.5 \cdot (R_i - 1.0)), \quad \Delta R_i(g_i) = \frac{g_i}{3 \cdot \text{Burn}_i}$$
   Measures what the grant dollar **actually changes** in 12-month survival probability, preventing high-burn businesses from absorbing `$10,000` grants that only buy days of survival.

4. **Trophic Cascade Multiplier & Provenance Gate (`calculate_trophic_multiplier`)**:
   $$M_{\text{trophic}}(i) = 1.0 + 0.35 \cdot \ln(1 + k_{\text{out}}(i)) \cdot \sigma_{\text{sub}}(i) \cdot \pi_{\text{prov}}(i)$$
   Rewards verified root B2B suppliers (**Sour Flour Bakery** at `2.38x`, **Cumaica Coffee** at `2.06x`) only when backed by real tax-invoice edges (`ttxid`, $\pi_{\text{prov}} = 1.00$), while capping modeled BEA/footfall edges at $\pi_{\text{prov}} \le 0.35$.

5. **Human Beneficiaries & Spatial Cluster Critical Mass (`calculate_human_impact`, `calculate_spatial_cluster_bonus`)**:
   $$H_i = \frac{\ln(1 + \text{Patrons}_i + 15 \cdot \text{Employees}_i)}{\ln(1 + 750)} \cdot E_i, \quad J_{\text{clust}}(i) = \begin{cases} 1.20, & N_{\text{active}}(C_k) \ge 3 \\ 1.00, & \text{otherwise} \end{cases}$$
   Incorporates low-income neighborhood equity ($E_i \in [1.00, 1.35]$) and enforces a two-block storefront cluster critical-mass bonus on 6th & Mission to preserve pedestrian trip-chaining.

6. **Composite Ecosystem-Anchored Priority Score (`score_applicant`)**:
   $$\text{Score}_i = 100 \cdot P_i^{w_{\text{pur}}} \cdot U_i(R_i)^{w_{\text{run}}} \cdot T_i \cdot V_{\text{sector}}(i)^{w_{\text{vol}}} \cdot \left[\alpha \cdot \frac{M_{\text{trophic}}(i)^{w_{\text{par}}}}{2.50} + (1 - \alpha) \cdot H_i^{w_{\text{peo}}}\right] \cdot J_{\text{clust}}(i)$$

7. **Submodular Overlap Deduplication & Multi-Regime Stress-Testing (`optimize_portfolio`, `run_multi_regime_stress_test`)**:
   Evaluates `Concentrate Top 5 ($10k)`, `Spread Across 8 ($6.25k)`, and `Tiered Hybrid ($10k Anchors + $5k Bridge)` while applying a `60%` submodular overlap discount (`0.40x` marginal credit) when two upstream suppliers share the same downstream cafes.

---

### Module 3: Live BigQuery Property Graph Connector ([`tools/bq_graph_connector.py`](../tools/bq_graph_connector.py))
Implements the required multi-hop GQL Property Graph traversal (`query_corridor_cascade_graph`) over `a4i_econ.LocalEconomy`:
- Traverses `1 to 3` hops (`-[e:supplies_to]->{1,3}`) from upstream nodes to downstream corridor storefronts.
- Computes hop-attenuated cascade weights ($\gamma^h$ with $\gamma = 0.65$) and distinguishes verified tax records (`ttxid`) from modeled relationships (`bea_direct_requirements`, `draws_footfall_from`).

---

### Module 4: 10-Vector Red-Team Compliance Report Generator ([`tools/compliance_reporter.py`](../tools/compliance_reporter.py))
Generates a deterministic **10/10 PASS** verification audit (`run_red_team_compliance_audit` and `generate_red_team_compliance_markdown`) proving that:
1. All 4 corporate/non-storefront traps receive `$0`.
2. Partial-grant dilution is prevented on indivisible capital cliffs.
3. Modeled edges cannot manufacture fake supply-chain cascades.
4. Shared downstream buyers are never double-counted (`118` deduplicated network jobs vs. `162` naive sum).
5. The 6th & Mission two-block storefront cluster maintains critical mass ($\ge 3$ funded storefronts).
