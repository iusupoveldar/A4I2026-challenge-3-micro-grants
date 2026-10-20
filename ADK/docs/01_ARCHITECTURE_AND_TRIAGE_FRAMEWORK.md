> **Illustrative design record.** Financials, beneficiaries, grant awards and schematic examples below are assumptions, not verified outcomes or city determinations. [Source evidence and corrections](04_SOURCE_EVIDENCE_AND_REVIEW.md) take priority.

# Central Market Small Business Relief Showcase: System Architecture & Triage Framework

**Document Identifier**: `01_ARCHITECTURE_AND_TRIAGE_FRAMEWORK.md`  
**Target Corridor**: Central Market Commercial Corridor, San Francisco, CA  
**Audience**: Technical Systems Architects, Municipal Data Scientists, Grant Officers, and Economic Policy Analysts  
**Core Purpose**: End-to-End Technical & Mathematical Specification of the Dual-Track Triage and Portfolio Optimization Engine  

---

## 1. System Architecture Overview & Pipeline Flow

The Central Market Small Business Relief Engine transforms disparate municipal public records, commercial lease disclosures, micro-economic field surveys, and Census neighborhood vulnerability data into an optimal, defensible portfolio of emergency micro-grants under a strict **$50,000 budget constraint**.

Rather than relying on unweighted administrative heuristics or isolated financial statements, the system models the commercial corridor as an interdependent socio-economic ecosystem. It balances direct community service retention against multi-tier commercial supply chain protection, while ensuring that public dollars are safeguarded from corporate leakage and dilution.

```mermaid
flowchart TD
    subgraph S0["Stage 0: Ingestion & Corporate Exclusion"]
        direction TB
        A1["City Business Registry Records"] --> AC["Corporate Exclusion Gate"]
        A2["Federal Small Business Loan History"] --> AC
        A3["Census Neighborhood Need Metrics"] --> AC
        AC -->|"Disqualify Enterprise Tech, Biotech, Garages"| EX["Corporate Exclusion Tray\n(Waymo, WP Engine, Tradespace)"]
        AC -->|"Pass Authentic Main Street Storefronts"| V1["Verified Applicant Pool"]
    end

    subgraph S1["Stage 1: Intake & Administrative Verification"]
        direction TB
        V1 --> B1["Commercial Lease & Arrears Audit"]
        V1 --> B2["State Payroll Records (EDD DE-9C)"]
        V1 --> B3["Intake Urgency & 1-Invoice Verification"]
    end

    subgraph S2["Stage 2: Dual-Track Feature Extraction"]
        direction TB
        B1 & B2 & B3 --> TR1["Track 1: Community Anchor Stream\n• Foot-Traffic Gravity Model\n• Census Tract Equity Multiplier\n• Essential Access & Category Scarcity"]
        B1 & B2 & B3 --> TR2["Track 2: Commercial Network Stream\n• Root Producer Identification\n• Path-Attenuated Supply Contagion\n• Local Redundancy Haircut (r_j^-0.5)"]
    end

    subgraph S3["Stage 3: Extended Multi-Objective Synthesis"]
        direction TB
        TR1 & TR2 --> F1["1. Financial Runway & Survival Lift (ΔP)"]
        TR1 & TR2 --> F2["2. Sector Volatility & Macroeconomic Risk"]
        TR1 & TR2 --> F3["3. Total People Helped (Workers + Residents)"]
        TR1 & TR2 --> F4["4. Independent Small-Business Purity Score"]
        TR1 & TR2 --> F5["5. Upstream Root Supplier Hierarchy Weight"]
        F1 & F2 & F3 & F4 & F5 --> COMP["Composite Priority Index\n(Score per Requested Dollar)"]
    end

    subgraph S4["Stage 4: Constrained Knapsack Portfolio Optimization"]
        direction TB
        COMP --> KS["Constrained Optimization Engine\nBudget Cap: B = $50,000\nAllocation: g_i in {0, 0.5 R_i, R_i}\nConstraint: Downstream Overlap Deduplication"]
    end

    subgraph S5["Stage 5: Determination & Disbursement Governance"]
        direction TB
        KS --> D1["Recommended Portfolio Grant Awards"]
        KS --> D2["Executive Determination Memo"]
        KS --> D3["Direct Two-Party Warrant Issuance\n(Landlord / Utility / Equipment Vendor)"]
    end

    style S0 fill:#f8f9fa,stroke:#343a40,stroke-width:2px
    style S1 fill:#e9ecef,stroke:#495057,stroke-width:2px
    style S2 fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style S3 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style S4 fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style S5 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style EX fill:#ffebee,stroke:#c62828,stroke-width:2px
```

---

## 2. Stage 0: The Corporate Exclusion Gate

A primary vulnerability of naive data pipelines is the **Corporate Masquerade Trap**: municipal tax registries record legal corporate parents without distinguishing between an independent neighborhood bakery and a multinational corporate subsidiary. When national transaction benchmarks are naively applied, corporate cloud platforms, biotech firms, and parking conglomerates falsely capture high network centrality scores.

The **Corporate Exclusion Gate** enforces strict algorithmic and policy filters at the perimeter of the grant pipeline.

### 2.1 Filtering Logic and Rule Hierarchy

```mermaid
flowchart TD
    IN["Applicant Intake Record"] --> Q1{"Is Sector in Main Street Class?\n(Retail, Food Service, Personal Care,\nArtisan Maker, Community Service)"}
    Q1 -- "No (Software, Biotech, Conglomerates)" --> REJ1["Disqualified:\nNon-Main Street Sector"]
    Q1 -- "Yes" --> Q2{"Does Entity Have Physical Ground-Floor\nPresence in Central Market Corridor?"}
    Q2 -- "No (Virtual / Holding Entity)" --> REJ2["Disqualified:\nNo Physical Commercial Frontage"]
    Q2 -- "Yes" --> Q3{"Is Business Independent Single-Unit?\n(Locations <= 2, No Public/VC Backing)"}
    Q3 -- "No (Corporate Subsidiary / Multi-Unit)" --> REJ3["Disqualified:\nCorporate / Venture Capital Backed"]
    Q3 -- "Yes" --> Q4{"Is Business an Automobile Storage Facility\nor Street-Deadening Garage?"}
    Q4 -- "Yes" --> REJ4["Disqualified:\nOff-Street Parking Operator"]
    Q4 -- "No" --> PASS["PASSED STAGE 0 GATE:\nAdmitted to Evaluation Queue"]

    style PASS fill:#d4edda,stroke:#28a745,stroke-width:2px
    style REJ1 fill:#f8d7da,stroke:#dc3545,stroke-width:1px
    style REJ2 fill:#f8d7da,stroke:#dc3545,stroke-width:1px
    style REJ3 fill:#f8d7da,stroke:#dc3545,stroke-width:1px
    style REJ4 fill:#f8d7da,stroke:#dc3545,stroke-width:1px
```

### 2.2 Corporate False Positive Audit in Central Market

| Registered Business Name | Registry Address | Nominal Classification | Raw Model Masquerade | Disqualification Rationale & Exclusion Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Waymo LLC** | 400 2nd St / 215 Taylor St | Motor Vehicle Mfg / Fleet Ops | Captures 118 downstream edges via fleet maintenance records | **Corporate Tech Subsidiary ($30B+ Valuation)**: Wholly owned subsidiary of Alphabet Inc. Does not represent an independent Main Street commercial storefront. Excluded under Single-Unit Independence Rule. |
| **WP Engine, Inc.** | 300 Howard St / 1161 Mission St | Computer Systems Design / Cloud | Registers 121 reachable nodes via enterprise cloud hub bridging | **Global Tech Corporation ($1B+ Valuation)**: Multi-tenant software hosting provider. Connects to 3 corridor nodes but falsely inherits 114 downstream buyers via cloud infrastructure. Excluded under Non-Storefront Tech Rule. |
| **Tradespace** | 1455 Market St | Data Processing & Cloud Hosting | Models 114 direct corridor buyers in raw transaction tables | **Enterprise Cloud Software Platform**: High venture capitalization. Commercial software provider, not a vulnerable street-level merchant. Excluded under Sector Classification Rule. |
| **Ossium Health, Inc.** | 490 2nd St | Pharmaceutical & Biotech | Models 68 supply edges due to broad chemical sector rollup | **Clinical-Stage Biotechnology Laboratory**: Specializes in cryopreserved human bone marrow therapeutics. Aggregated industry codes conflate lab therapeutics with commercial cleaning soap. Excluded under Biotech Sector Rule. |
| **Impark / Propark America** | 945 Market St / Various | Commercial Parking Management | Models 42 commercial links under broad personal services | **National Commercial Parking Conglomerate**: Vehicle parking facilities deaden pedestrian activation, generate zero artisan value, and operate under national concessionaires. Excluded under Parking Garage Rule. |

---

## 3. The Dual-Track Triage Architecture

Once corporate false positives are eliminated, legitimate applicants enter the **Dual-Track Triage Architecture**. This structure reconciles two distinct economic forces:
1. **Track 1 (Community Anchor Stream)**: Prioritizes consumer-facing establishments that anchor pedestrian foot traffic and provide essential access to low-income, transit-dependent residents.
2. **Track 2 (Commercial Network Stream)**: Prioritizes upstream commercial producers whose failure would trigger cascading supply failures across downstream corridor restaurants and cafes.

```mermaid
flowchart LR
    subgraph INPUT["Stage 0 Approved Main Street Applicants"]
        direction TB
        APP["Verified Applicant Pool"]
    end

    subgraph TRACK1["Track 1: Community Anchor Stream (Walk-In Vitality & Equity)"]
        direction TB
        T1_1["Neighborhood Foot-Traffic Gravity\n• Commuter Transit Flows (Civic Center / Powell)\n• SRO Residential Footfall Agglomeration"]
        T1_2["Census Neighborhood Need Multiplier\n• Tract 012502: 34.2% Poverty, 78.5% Car-Free\n• Essential Food & Health Access Retention"]
        T1_3["Category Scarcity & Anti-Desert Factor\n• Solitary Neighborhood Bodegas\n• Eviction-Defense & Community Health"]
        T1_1 & T1_2 & T1_3 --> S_ANC["Community Anchor Score (S_anchor)"]
    end

    subgraph TRACK2["Track 2: Commercial Network Stream (Multi-Hop Contagion Prevention)"]
        direction TB
        T2_1["Root Producer Hierarchy Identification\n• Commissaries, Bakeries, Roasteries\n• High Out-Degree / Low In-Degree"]
        T2_2["Downstream Inter-Business Supply Links\n• 1-Hop Direct Commercial Buyers\n• 2-Hop Indirect Establishments (Discounted)"]
        T2_3["Local Redundancy Haircut & Substitution\n• Competitor Density Discount (r_j^-0.5)\n• Artisan vs. Commodity Friction"]
        T2_1 & T2_2 & T2_3 --> S_CAS["Supply Contagion Score (S_cascade)"]
    end

    subgraph SYNTH["Unified Policy Synthesis"]
        direction TB
        S_ANC --> BAL["Policy Balancing Weight (α)\n• Commercial Contagion (α = 0.50)\n• Community Anchor Vitality (1 - α = 0.50)"]
        S_CAS --> BAL
        BAL --> ECO["Base Ecosystem Economic Value (E_i)"]
    end

    INPUT --> TRACK1
    INPUT --> TRACK2

    style TRACK1 fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style TRACK2 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style SYNTH fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
```

### 3.1 Mathematical Formulation of the Dual Tracks

#### Track 1: Community Anchor Score ($S_{\text{anchor}}$)
For each consumer-facing establishment $i$, the anchor score measures pedestrian gravity, transit commuter draw, and essential neighborhood access:

$$S_{\text{anchor}}(i) = M_{\text{equity}}(\text{tract}_i) \cdot \left[ \gamma_{\text{transit}} \cdot G_{\text{transit}}(i) + \gamma_{\text{ped}} \cdot G_{\text{ped}}(i) + \gamma_{\text{scarcity}} \cdot C_{\text{scarcity}}(i) \right]$$

Where:
- $G_{\text{transit}}(i) \in [0, 100]$ quantifies pedestrian commuter capture from the Civic Center and Powell Street BART/Muni subway portals within a 500-meter radius.
- $G_{\text{ped}}(i) \in [0, 100]$ captures walk-in residential footfall density, particularly from dense Single Room Occupancy (SRO) housing blocks along 6th, 7th, and Mission Streets.
- $C_{\text{scarcity}}(i) \ge 1.0$ is the **Category Scarcity Multiplier**. If establishment $i$ is the only fresh grocery provider or walk-in community clinic within a 400-meter walking radius in a high-poverty tract, $C_{\text{scarcity}} = 2.0$.
- $M_{\text{equity}}(\text{tract}_i)$ is the **Census Neighborhood Equity Multiplier**:
  $$M_{\text{equity}}(\text{tract}_i) = 1.0 + \lambda_1 \cdot \text{PovertyRate}(\text{tract}_i) + \lambda_2 \cdot \text{ZeroVehicleShare}(\text{tract}_i)$$
  In Tract 012502 (Poverty Rate = 34.2%, Zero-Vehicle Rate = 78.5%), calibrated parameters ($\lambda_1 = 1.0, \lambda_2 = 0.5$) yield $M_{\text{equity}} \approx 1.73$, prioritizing essential storefronts in neighborhoods with zero private vehicle mobility.

#### Track 2: Commercial Network Contagion Score ($S_{\text{cascade}}$)
For each commercial supplier $i$, the contagion score models the systemic disruption triggered across downstream buyers if supplier $i$ closes:

$$S_{\text{cascade}}(i) = \sum_{j \in N_1^+(i)} w_{ij} \cdot r_j^{-0.5} \cdot (1 - \theta_{\text{ext}}) \cdot \text{Impact}(j) + \beta \sum_{k \in N_2^+(i)} w_{ik}^{(2)} \cdot r_k^{-0.5} \cdot (1 - \theta_{\text{ext}}) \cdot \text{Impact}(k)$$

Where:
- $N_1^+(i)$ denotes the set of direct commercial buyers (1-hop), and $N_2^+(i)$ denotes indirect downstream establishments (2-hop).
- $w_{ij}$ represents the normalized expenditure weight of buyer $j$ on supplier $i$.
- $r_j^{-0.5}$ is the **Local Redundancy Discount**: where $r_j$ is the number of alternative local suppliers of the same commodity within a 1-kilometer radius. If a buyer has multiple local alternatives, the closure of supplier $i$ is discounted.
- $\theta_{\text{ext}} \in [0.0, 0.8]$ is the **External Distributor Substitutability Parameter**, haircutting links where buyers can switch to national broadline food distributors. For artisan goods (e.g., fresh sourdough, specialty roast coffee), $\theta_{\text{ext}} \approx 0.15$ (high friction, low substitutability); for commodity goods, $\theta_{\text{ext}} \ge 0.60$.
- $\beta \in (0, 1)$ is the **Path Attenuation Factor** ($\beta = 0.35$), preventing second-order network bloat.
- $\text{Impact}(j)$ reflects the payroll employment and footfall scale of downstream establishment $j$.

#### Base Corridor Economic Value ($E_i$)
The dual tracks are synthesized via the policy balancing weight $\alpha \in [0, 1]$:

$$E_i = \alpha \cdot S_{\text{cascade}}(i) + (1 - \alpha) \cdot S_{\text{anchor}}(i)$$

---

## 4. The Complete Evaluation & Allocation Pipeline

The transition from applicant intake to public warrant disbursement follows an automated, five-stage pipeline.

```mermaid
sequenceDiagram
    autonumber
    actor Applicant as Central Market Business
    participant Intake as Stage 0 & 1: Intake & Gate
    participant DualEngine as Stage 2: Dual-Track Engine
    participant MultiObj as Stage 3: Multi-Objective Evaluator
    participant Knapsack as Stage 4: Knapsack Optimizer
    participant GrantOfficer as Stage 5: Grant Officer & Audit

    Applicant->>Intake: Submit Relief Intake (Lease, Payroll, Urgency)
    Intake->>Intake: Run Corporate Exclusion Gate (Filter Tech/Biotech)
    Intake->>Intake: Cross-Verify City Business Registry & DE-9C Payroll
    Intake-->>DualEngine: Admitted Main Street Establishment
    DualEngine->>DualEngine: Extract Anchor Metrics (Footfall Gravity & Census Equity)
    DualEngine->>DualEngine: Extract Network Metrics (1-Hop / 2-Hop Supply Links)
    DualEngine-->>MultiObj: Base Economic Scores (S_anchor, S_cascade)
    MultiObj->>MultiObj: Calculate Liquidity Runway & Marginal Lift ΔP(r_i)
    MultiObj->>MultiObj: Evaluate People Helped & Small-Biz Purity
    MultiObj->>MultiObj: Apply Root Supplier Hierarchy Multiplier
    MultiObj-->>Knapsack: Net Corridor Value per Grant Dollar
    Knapsack->>Knapsack: Execute 0/1 Knapsack with Overlap Deduplication ($50,000 Cap)
    Knapsack-->>GrantOfficer: Optimal Portfolio Allocation
    GrantOfficer->>GrantOfficer: Generate Public Determination Memo
    GrantOfficer->>Applicant: Issue Two-Party Warrants (Direct to Landlord/Vendor)
```

---

## 5. The Central Market Inter-Business Network

The real Central Market ecosystem consists of interdependent economic nodes: foundational upstream food and beverage producers, ground-floor dining storefronts, spatial anchors along the critical 6th & Mission tipping corridor, and essential community service providers.

```mermaid
graph TD
    subgraph UPSTREAM["Foundational Upstream Production Hubs (Root Makers)"]
        SF["Sour Flour\n(1182 Market St)\n• Production Deck Ovens\n• 85 Direct Wholesale Buyers\n• 10 Direct Employees"]
        CC["Cumaica Coffee\n(1398 Mission St)\n• Production Roastery & Espresso\n• 85 Direct Wholesale Accounts\n• 8 Direct Employees"]
    end

    subgraph DOWNSTREAM["Downstream Retail Dining & Quick-Service Storefronts"]
        GR["G.Rabbit Restaurant\n(90 7th St at Mission)\n• Sit-Down Asian Fusion\n• 12 Employees\n• High Mid-Market Footfall"]
        CP["Chico's Pizza\n(131 6th St)\n• Fast-Casual Slice Shop\n• 5 Employees\n• Low-Cost Calorie Anchor"]
        CAFES["Independent Corridor Cafes & Delis\n(Market & Mission Corridor)\n• 70+ Micro-Storefronts\n• Transit-Dependent Customers"]
    end

    subgraph SPATIAL["6th & Mission Revitalization Tipping Corridor"]
        MB["Monarch Beverage Catering\n(101 6th St at Mission)\n• 6th St Gateway Anchor\n• Event Commissary & Mobile Bar\n• 7 Employees"]
        PS["The Pawn Shop Tapas Lounge\n(993 Mission St near 6th)\n• Evening Footfall & Nightlife Anchor\n• Street-Level Active Lighting\n• 11 Employees"]
    end

    subgraph ESSENTIAL["Essential Household & Community Welfare Anchors"]
        CG["Central Market Corner Grocer\n(1028 Market St)\n• Full-Service Bodega & Fresh Produce\n• 950 Daily Pedestrian Residents\n• Census Tract 012502 (78.5% Car-Free)"]
        CL["Central Market Health & Legal Clinic\n(976 Mission St)\n• Free Walk-In Clinic & Eviction Defense\n• 16 Staff / 150 Daily Clients\n• Non-Profit Safety Net"]
    end

    subgraph CORPORATE["Blocked Corporate Traps (Stage 0 Exclusion)"]
        WAYMO["Waymo LLC\n(Autonomous Fleet Ops)\n[DISQUALIFIED: Corporate Subsidiary]"]
        WPENG["WP Engine, Inc.\n(Enterprise Cloud Hosting)\n[DISQUALIFIED: Tech Corp]"]
    end

    %% Supply Chain Linkages
    SF -->|"Fresh Sourdough & Baguettes Daily"| GR
    SF -->|"Daily Artisan Bread Delivery"| CP
    SF -->|"Wholesale Bakery Supply"| CAFES
    SF -->|"Fresh Loaves for Retail Shelf"| CG

    CC -->|"Roasted Espresso Beans & Cold Brew"| GR
    CC -->|"Direct Wholesale Coffee"| CAFES
    CC -->|"Packaged Whole Bean Coffee"| CG

    MB -.->|"Shared Event Catering & Pop-Ups"| PS
    MB -.->|"Commissary Kitchen Collaboration"| GR

    %% Spatial Co-Location & Agglomeration
    CP ---|"Mid-Block Pedestrian Agglomeration"| MB
    MB ---|"Corner Footfall & Safety Transition"| PS
    PS ---|"Street Lighting & Nighttime Activity"| CL

    %% Styling Nodes
    style SF fill:#ffecb3,stroke:#ff8f00,stroke-width:3px
    style CC fill:#ffe0b2,stroke:#f57c00,stroke-width:3px
    style CG fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    style CL fill:#d1c4e9,stroke:#512da8,stroke-width:2px
    style CP fill:#bbdefb,stroke:#1565c0,stroke-width:2px
    style GR fill:#b3e5fc,stroke:#0277bd,stroke-width:2px
    style MB fill:#b2dfdb,stroke:#00695c,stroke-width:2px
    style PS fill:#b2ebf2,stroke:#00838f,stroke-width:2px
    style CAFES fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,stroke-dasharray: 5 5
    style WAYMO fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px,stroke-dasharray: 3 3
    style WPENG fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px,stroke-dasharray: 3 3
```

### 5.1 Systemic Ecosystem Insights
1. **Upstream Root Dependency**: *Sour Flour* and *Cumaica Coffee* serve as the local production bedrock. If *Sour Flour* closes due to a failed oven, over 85 independent restaurants, cafes, and corner delis lose their primary fresh bread source overnight, forcing them into expensive, low-quality industrial substitutes or disrupted operating menus.
2. **The 6th Street Spatial Complementarity**: *Chico's Pizza*, *Monarch Beverage Catering*, and *The Pawn Shop* form an interdependent pedestrian safety cluster. *The Pawn Shop* generates evening exterior illumination and foot traffic; *Chico's Pizza* provides low-cost calories for neighborhood shift workers; *Monarch Beverage* anchors the northern gateway intersection. Allowing any two to fail triggers a vacancy cascade that depresses the entire corridor.
3. **Essential Final Demand**: The *Central Market Corner Grocer* sells zero goods to other businesses (pure consumer terminal node). However, its survival is critical to preventing a severe food desert for the 78.5% car-free SRO population in Census Tract 012502.

---

## 6. Extended Multi-Objective Scoring Mechanics

To transcend the limitations of baseline public records, the system integrates **five beyond-dataset real-world dimensions** into a unified mathematical optimization objective.

```mermaid
flowchart TD
    subgraph FACTORS["The 5 Beyond-Dataset Economic Dimensions"]
        D1["Dimension 1: Financial Buffer & Liquidity Runway\n• Inflection midpoint r* = 1.0 qtr\n• Viable Paycheck-to-Paycheck Sweet Spot (0.5 - 1.5 qtrs)\n• Discount Self-Insuring (>=4 qtrs) & Walking Dead (<0.25 qtr)"]
        D2["Dimension 2: Sector Health & Macroeconomic Volatility\n• Sector margin thickness (Food Service: 3-5% vs Grocer: 2-3%)\n• Cyclical shock sensitivity & demand elasticity index"]
        D3["Dimension 3: Total People Helped\n• Direct workers + Downstream protected workers\n• Daily walk-in commuter patrons + High-need SRO residents"]
        D4["Dimension 4: Independent Small-Business Purity\n• Single-location micro-enterprise priority\n• Penalizes multi-unit footprints and capital scale"]
        D5["Dimension 5: Upstream Root Supplier Hierarchy\n• High out-degree / Low in-degree multiplier (1.2x - 1.8x)\n• Safeguards foundational production infrastructure"]
    end

    subgraph SCORER["Composite Multi-Objective Formulation"]
        D1 & D2 & D3 & D4 & D5 --> FORMULA["Composite Value Formulation V_i(g_i)\nSynthesizes Survival Lift, Dual-Track Economic Value, Equity, Purity, Volatility, and Beneficiaries"]
    end

    style D1 fill:#e1f5fe,stroke:#0288d1,stroke-width:1px
    style D2 fill:#f3e5f5,stroke:#8e24aa,stroke-width:1px
    style D3 fill:#e8f8f5,stroke:#16a085,stroke-width:1px
    style D4 fill:#fff8e1,stroke:#fbc02d,stroke-width:1px
    style D5 fill:#fbe9e7,stroke:#d84315,stroke-width:1px
    style FORMULA fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

### 6.1 Dimension 1: Financial Runway & Marginal Survival Lift ($\Delta P$)
The emergency relief model targets viable storefronts where public cash provides maximum marginal survival lift, rather than subsidizing self-insuring firms or temporarily delaying terminal liquidations.

The post-grant marginal survival lift is formulated as:

$$\Delta P(g_i \mid r_i) = \frac{1}{1 + \exp\left(-k \left(r_i + \frac{g_i}{\kappa_i} - r^*\right)\right)} - \frac{1}{1 + \exp\left(-k (r_i - r^*)\right)}$$

Where:
- $r_i$ is current operational cash runway in consecutive bad quarters.
- $r^* = 1.0$ quarter is the critical median inflection threshold.
- $k = 2.0$ governs the steepness of the logistic transition.
- $\kappa_i$ is net quarterly operating burn.
- **Paycheck-to-Paycheck Sweet Spot ($0.5 \le r_i \le 1.5$)**: $\Delta P$ reaches its mathematical global maximum ($\Delta P \approx 0.55\text{–}0.72$), turning high-risk insolvency into stabilized operations.
- **Self-Insuring Limit ($r_i \ge 4.0$)**: $\Delta P \to 0$ ($\Delta P < 0.02$). Granting funds produces pure deadweight loss.
- **Walking Dead Limit ($r_i < 0.25$ with insurmountable burn $\kappa_i \gg R_i$)**: The grant provides under 14 days of life support; the business remains non-viable and is diverted to restructuring counseling.

### 6.2 Dimension 2: Sector Health & Macroeconomic Volatility ($\Omega_{\text{sector}}$)
Distinguishes temporary exogenous liquidity shocks from secular industry headwinds:

$$\Omega_{\text{sector}}(s) = 1.0 + \psi_{\text{margin}} \cdot (0.10 - \text{GrossMargin}_s) + \psi_{\text{elasticity}} \cdot \text{DemandElasticity}_s$$

Independent dining and arts establishments operating on 3–5% gross margins with high demand volatility receive higher stabilization weighting than counter-cyclical or inelastic sectors.

### 6.3 Dimension 3: Maximizing Total People Helped ($H_i$)
Quantifies human welfare preserved per dollar, combining direct jobs, indirect supply-chain workers, daily footfall patrons, and transit-dependent residents:

$$H_i = W_{\text{direct}}(i) + \sum_{j \in N_1^+(i)} W_{\text{downstream}}(j) \cdot w_{ij} + \eta_{\text{patron}} \cdot \text{DailyPatrons}(i) + \eta_{\text{resident}} \cdot \text{VulnerableResidents}(i)$$

Where $\eta_{\text{patron}} = 0.05$ and $\eta_{\text{resident}} = 0.20$, heavily weighting daily access for low-income, car-free neighbors.

### 6.4 Dimension 4: Independent Small-Business Purity ($P_{\text{purity}}$)
Protects the fund from larger corporate entities, multi-unit regional operators, or venture-backed concepts:

$$P_{\text{purity}}(i) = \frac{1}{\sqrt{\max(1, \text{OperatingLocations}_i)}} \cdot \left(1 - \frac{\text{Headcount}_i}{\text{MaxThreshold}}\right)$$

Sole-proprietor and single-location micro-enterprises achieve maximum purity ($P_{\text{purity}} = 1.0$), while multi-unit operations are downweighted.

### 6.5 Dimension 5: Foundational Upstream Producer Multiplier ($\omega_{\text{parent}}$)
Applies a structural boost to root producers that possess high outgoing supply edges and minimal local input procurement:

$$\omega_{\text{parent}}(i) = \begin{cases} 
1.50 & \text{if } \text{OutDegree}(i) \ge 10 \text{ and } \text{InDegree}(i) \le 2 \text{ (Root Producer)} \\
1.25 & \text{if } \text{OutDegree}(i) \ge 5 \text{ (Intermediate Hub)} \\
1.00 & \text{otherwise (Consumer Storefront)}
\end{cases}$$

---

## 7. Constrained Knapsack Portfolio Optimization

With scores computed for all qualifying applicants, the portfolio optimization engine solves an **Extended Multi-Choice Knapsack Problem** subject to the municipal budget cap and downstream overlap deduplication.

### 7.1 Mathematical Optimization Formulation

$$\max_{\{x_i, y_i\}} \sum_{i \in \mathcal{Q}} \Big[ x_i \cdot V_i(R_i) + y_i \cdot V_i(0.5 R_i) \Big] - \sum_{j \in \text{Overlaps}} \text{Penalty}(j)$$

Subject to:
1. **Municipal Budget Limit**:
   $$\sum_{i \in \mathcal{Q}} \Big[ x_i \cdot R_i + y_i \cdot (0.5 R_i) \Big] \le B = \$50,000$$
2. **Mutual Exclusivity of Grant Tiers**:
   $$x_i + y_i \le 1 \quad \forall i \in \mathcal{Q}, \quad x_i, y_i \in \{0, 1\}$$
3. **Indivisible Capital Cliff Rule**:
   If an applicant's intake audit verifies that its primary crisis is an indivisible capital cliff (e.g., commercial oven purchase or lease cure notice where partial payment is legally rejected), $y_i$ is constrained to 0:
   $$y_i = 0 \quad \implies \quad g_i \in \{0, R_i\}$$
4. **Downstream Overlap Deduplication**:
   When two upstream suppliers (*Sour Flour* and *Cumaica Coffee*) share identical downstream buyers, the optimization objective applies submodular set coverage deduplication, ensuring that shared downstream beneficiaries are counted once rather than twice.

### 7.2 Portfolio Regimes Comparison

```mermaid
flowchart TD
    subgraph REGIMES["Portfolio Allocation Regimes ($50,000 Budget)"]
        R1["Regime A: Concentrate Top 5 ($10k Full Grants)\n• 5 Grants x $10,000 = $50,000\n• Completely cures hard capital cliffs for top systemic hubs\n• Leaves 3-4 viable storefronts unassisted"]
        R2["Regime B: Equal Dilution ($6.25k Across 8)\n• 8 Grants x $6,250 = $50,000\n• Spreads relief broadly across corridor\n• HIGH FAILURE RISK: Violates capital cliffs (evictions/ovens)"]
        R3["Regime C: Tiered Hybrid (RECOMMENDED)\n• 3 Full Grants ($10k) to Systemic Anchors: Sour Flour, Grocer, Cumaica\n• 4 Bridge Grants ($5k) to Spatial Storefronts: Chico's, Monarch, Pawn, G.Rabbit\n• Maximizes jobs (59), protects supply web, anchors 6th St cluster"]
    end

    style R1 fill:#fff3e0,stroke:#f57c00,stroke-width:1px
    style R2 fill:#ffebee,stroke:#c62828,stroke-width:1px
    style R3 fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

The **Tiered Hybrid Regime** provides the superior policy outcome: it fully cures indivisible capital crises for the corridor's foundational anchors (*Sour Flour*, *Cumaica Coffee*, and the *Corner Grocer*) while deploying targeted working-capital bridge grants ($5,000) that stabilize operational payroll and lease buffers across the critical 6th & Mission spatial cluster.
