/**
 * Grant Officer Console — Core Data & Agent Contract (`contract.ts`)
 * ==================================================================
 * Defines the unified schema shared between:
 *   1. The Vite + React + TypeScript Frontend (`frontend/src/*`)
 *   2. The Central Market Canonical Fixtures (`frontend/src/fixtures/central-market.ts`)
 *   3. The ADK Multi-Agent Backend (`agents/regime_orchestrator_agent.py`)
 */

export type UIStateMode =
  | 'recommendation'
  | 'compare'
  | 'leaf'
  | 'refusal'
  | 'streaming'
  | 'empty';

export type RightPanelTab =
  | 'memo'
  | 'compare'
  | 'assumptions'
  | 'equity'
  | 'provenance';

export type AllocationStatus =
  | 'FUNDED_TIER1'
  | 'FUNDED_TIER2'
  | 'FUNDED_LEAF'
  | 'REFUSED_TRAP'
  | 'OUT_OF_CORRIDOR';

export type EvidenceClassification = 'measured' | 'modeled' | 'verified_intake';

export interface ScenarioSpec {
  track: 'main_street_and_supply_continuity' | 'anchor_closure' | 'supply_continuity';
  corridor: string;
  budget_usd: number;
  prompt_text: string;
}

export interface BusinessIdentity {
  id: string;
  key: string;
  name: string;
  legal_name: string;
  address: string;
  naics: string;
  naics4: string;
  industry: string;
  tenure_years: number;
  direct_jobs: number;
  sba_status: string;
}

export interface CascadeNode {
  id: string;
  name: string;
  subtitle: string;
  hop: 0 | 1 | 2 | 3; // 0 = Inbound/Root, 1 = Seed Applicant, 2 = 1-Hop Direct, 3 = 2-Hop Network
  industry: string;
  node_type: 'Employer' | 'Lender' | 'Seed' | 'Buyer' | 'BuyerGroup' | 'ExposedCluster' | 'TrapSeed' | 'LeafNotice';
  is_leaf: boolean;
  badge: string;
  co_funded_grant_usd?: number;
}

export interface CascadeEdge {
  id: string;
  source: string;
  target: string;
  type: 'Supplies' | 'DrawsFootfall' | 'BorrowedFrom' | 'Cascade2Hop';
  label: string;
  intensity: number;
  decayed_intensity: number;
  metres: number;
  corridor_alternatives: number | null;
  worker_share: number | null;
  evidence: EvidenceClassification;
  verifiable_by_intake?: boolean;
  intake_quote?: string;
}

export interface CascadePath {
  path: string[];
  path_names: string[];
  weight: number;
  decayed_weight: number;
  method: 'product_of_intensity' | 'sum_of_decayed_intensity' | 'sba_expected_exposure';
}

export interface CascadeGraph {
  root: string;
  nodes: CascadeNode[];
  edges: CascadeEdge[];
  paths: CascadePath[];
  stats: {
    reach_1hop: number;
    reach_2hop: number;
    max_hop: number;
    corridor_alternatives: number;
    p_fail_shrunk: number;
    p_fail_ci_90: string;
    expected_exposed: number;
    leaf_nodes_in_corridor: number;
    total_nodes_in_corridor: number;
  };
}

export interface ApplicantRecommendation {
  business: BusinessIdentity;
  grant_usd: number;
  tier_label: string;
  status: AllocationStatus;
  confidence: 'high' | 'medium' | 'refused';
  confidence_reason: string;
  one_liner: string;
  memo_narrative: string;
  portfolio_synergy_note: string;
  cascade: CascadeGraph;
  runner_up: {
    business: BusinessIdentity;
    grant_usd: number;
    reach_1hop: number;
    reach_2hop: number;
    corridor_alternatives: number;
    p_fail_shrunk: number;
    expected_exposed: number;
    why_not: string;
  };
  demographics: {
    tract: string;
    median_income: number;
    pct_below_poverty: number;
    pct_no_vehicle: number;
    source: string;
  };
  provenance: {
    gql: string;
    rows_returned: number;
    job_id: string;
    elapsed_ms: number;
  };
}

export interface AssumptionSensitivity {
  statement: string;
  parameter_name: string;
  baseline_value: string;
  if_wrong: string;
  impact: 'ranking_invariant' | 'high' | 'moderate';
}

export interface IndustryEquityRow {
  industry: string;
  naics4: string;
  edge_share: number;
  biz_share: number;
  portfolio_funding_share: number;
  note: string;
}

export interface SbaValidationSummary {
  total_ca_loans: number;
  eligible_48m_loans: number;
  statewide_base_failure_rate: number;
  sf_holdout_loans: number;
  sf_base_failure_rate: number;
  models: {
    name: string;
    features: string;
    sf_holdout_auc: number;
    highlight?: boolean;
  }[];
  real_chargeoff_case: {
    business_id: string;
    name: string;
    legal_name: string;
    naics4: string;
    chargeoff_date: string;
    chargeoff_amount_usd: number;
    monthly_debt_est_usd: number;
  };
}

export interface AgentTraceStep {
  step: number;
  agent_name: string;
  tool_called: string;
  summary: string;
  elapsed_ms: number;
  status: 'PASS' | 'WARN' | 'REFUSED';
}

export interface GrantConsoleContract {
  scenario: ScenarioSpec;
  portfolio_summary: {
    total_budget_usd: number;
    allocated_usd: number;
    funded_count: number;
    evaluated_count: number;
    refused_trap_count: number;
    direct_jobs_protected: number;
    cost_per_direct_job_usd: number;
    downstream_dining_buyers_shielded: number;
    unique_2hop_nodes_reached: number;
    daily_patrons_served: number;
    tier1_total_usd: number;
    tier2_total_usd: number;
  };
  applicants: Record<string, ApplicantRecommendation>;
  queue_order: string[];
  assumptions: AssumptionSensitivity[];
  evidence: {
    measured: string[];
    modeled: string[];
    assumed: string[];
  };
  equity_audit: {
    by_industry: IndustryEquityRow[];
    finding: string;
    tract_summary: string;
  };
  sba_validation: SbaValidationSummary;
  agent_trace: AgentTraceStep[];
}
