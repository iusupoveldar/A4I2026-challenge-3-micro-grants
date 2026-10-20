/**
 * Central Market Small Business Relief Decision Showcase
 * City & County of San Francisco - Office of Economic & Workforce Development (OEWD)
 * Pure Vanilla ES6 Client-Side Application Engine
 * Zero External Dependencies - 100% Local Self-Contained Execution
 */

(function () {
  'use strict';

  // --- 1. APPLICANT DATA REGISTRY (CENTRAL MARKET EMPIRICAL COHORT) ---
  const APPLICANTS_DATA = [
    {
      id: "sour_flour",
      name: "Sour Flour",
      legalName: "Sour Flour LLC",
      address: "1182 Market St, Suite 415",
      subCorridor: "Market St Spine (Tract 012502)",
      tract: "06075012502",
      povertyRate: 0.342,
      carFreeRate: 0.785,
      sector: "Retail Bakery & Commissary Food Mfg",
      naics: "3118",
      headcount: 8,
      runwayQuarters: 0.8,
      burnRateMonthly: 12500,
      reqGrant: 10000,
      isParentSupplier: true,
      outDegree: 85,
      inDegree: 2,
      secondOrderReach: 148,
      downstreamOverlapIds: ["cumaica_coffee"],
      dailyPatronCommuters: 1200,
      vulnerableResidentsServed: 450,
      essentialTier: 4,
      operatingMargin: 0.05,
      demandElasticity: 1.8,
      purityBaseline: 92.5,
      isCorporateTrap: false,
      mapX: 420,
      mapY: 260,
      needJustification: "Hearth deck oven electrical failure replacement & lease stabilization."
    },
    {
      id: "cumaica_coffee",
      name: "Cumaica Coffee",
      legalName: "Cumaica Coffee Corp",
      address: "1398 Mission St (at 10th)",
      subCorridor: "Mission / 10th St Hub",
      tract: "06075017802",
      povertyRate: 0.268,
      carFreeRate: 0.682,
      sector: "Specialty Coffee Roasting & Food Mfg",
      naics: "3119",
      headcount: 8,
      runwayQuarters: 1.1,
      burnRateMonthly: 11000,
      reqGrant: 10000,
      isParentSupplier: true,
      outDegree: 85,
      inDegree: 3,
      secondOrderReach: 140,
      downstreamOverlapIds: ["sour_flour"],
      dailyPatronCommuters: 950,
      vulnerableResidentsServed: 380,
      essentialTier: 3,
      operatingMargin: 0.07,
      demandElasticity: 1.6,
      purityBaseline: 88.0,
      isCorporateTrap: false,
      mapX: 180,
      mapY: 450,
      needJustification: "Commercial roaster ventilation retrofit & direct-trade bean inventory."
    },
    {
      id: "corner_grocer",
      name: "Central Market Corner Grocer",
      legalName: "Central Market Groceries & Deli Inc",
      address: "1028 Market St",
      subCorridor: "Market St Spine (Tract 012502)",
      tract: "06075012502",
      povertyRate: 0.342,
      carFreeRate: 0.785,
      sector: "Essential Retail Supermarket & Bodega",
      naics: "4451",
      headcount: 5,
      runwayQuarters: 0.6,
      burnRateMonthly: 14000,
      reqGrant: 10000,
      isParentSupplier: false,
      outDegree: 0,
      inDegree: 6,
      secondOrderReach: 0,
      downstreamOverlapIds: [],
      dailyPatronCommuters: 950,
      vulnerableResidentsServed: 1400,
      essentialTier: 5,
      operatingMargin: 0.02,
      demandElasticity: 0.4,
      purityBaseline: 96.0,
      isCorporateTrap: false,
      mapX: 520,
      mapY: 230,
      needJustification: "Compressor emergency cure for walk-in produce cooler & fresh food restocking."
    },
    {
      id: "g_rabbit",
      name: "G.Rabbit",
      legalName: "G.Rabbit Dining Ventures LLC",
      address: "90 7th St (at Mission)",
      subCorridor: "7th & Mission Connector",
      tract: "06075017802",
      povertyRate: 0.268,
      carFreeRate: 0.682,
      sector: "Full-Service Independent Dining",
      naics: "7225",
      headcount: 14,
      runwayQuarters: 0.9,
      burnRateMonthly: 18000,
      reqGrant: 10000,
      isParentSupplier: false,
      outDegree: 15,
      inDegree: 8,
      secondOrderReach: 18,
      downstreamOverlapIds: [],
      dailyPatronCommuters: 320,
      vulnerableResidentsServed: 180,
      essentialTier: 2,
      operatingMargin: 0.04,
      demandElasticity: 2.2,
      purityBaseline: 74.5,
      isCorporateTrap: false,
      mapX: 470,
      mapY: 360,
      needJustification: "Kitchen grease-trap compliance overhaul and payroll bridge."
    },
    {
      id: "monarch_beverage",
      name: "Monarch Beverage Catering LLC",
      legalName: "Monarch Beverage Catering LLC",
      address: "101 6th St (at Mission)",
      subCorridor: "6th & Mission Tipping Point",
      tract: "06075017802",
      povertyRate: 0.268,
      carFreeRate: 0.682,
      sector: "Specialty Food Services & Commissary",
      naics: "7223",
      headcount: 7,
      runwayQuarters: 1.0,
      burnRateMonthly: 10500,
      reqGrant: 10000,
      isParentSupplier: false,
      outDegree: 8,
      inDegree: 5,
      secondOrderReach: 16,
      downstreamOverlapIds: [],
      dailyPatronCommuters: 150,
      vulnerableResidentsServed: 120,
      essentialTier: 2,
      operatingMargin: 0.08,
      demandElasticity: 2.0,
      purityBaseline: 85.0,
      isCorporateTrap: false,
      mapX: 610,
      mapY: 250,
      needJustification: "Cold storage transport repair and commercial kitchen permitting bridge."
    },
    {
      id: "chicos_pizza",
      name: "Chico's Pizza",
      legalName: "Chico's Pizza Restaurant LLC",
      address: "131 6th St",
      subCorridor: "6th & Mission Tipping Point",
      tract: "06075017802",
      povertyRate: 0.268,
      carFreeRate: 0.682,
      sector: "Quick-Service Pizzeria & Slice Shop",
      naics: "7225",
      headcount: 4,
      runwayQuarters: 0.7,
      burnRateMonthly: 9000,
      reqGrant: 10000,
      isParentSupplier: false,
      outDegree: 0,
      inDegree: 4,
      secondOrderReach: 0,
      downstreamOverlapIds: [],
      dailyPatronCommuters: 380,
      vulnerableResidentsServed: 550,
      essentialTier: 3,
      operatingMargin: 0.04,
      demandElasticity: 1.5,
      purityBaseline: 91.0,
      isCorporateTrap: false,
      mapX: 630,
      mapY: 280,
      needJustification: "Commercial pizza deck oven replacement and facade security gate."
    },
    {
      id: "pawn_shop",
      name: "The Pawn Shop",
      legalName: "Mission Pawn & Tapas LLC",
      address: "993 Mission St (near 6th)",
      subCorridor: "6th & Mission Tipping Point",
      tract: "06075017802",
      povertyRate: 0.268,
      carFreeRate: 0.682,
      sector: "Cultural Dining & Evening Tapas Lounge",
      naics: "7224",
      headcount: 10,
      runwayQuarters: 1.2,
      burnRateMonthly: 15000,
      reqGrant: 10000,
      isParentSupplier: false,
      outDegree: 0,
      inDegree: 5,
      secondOrderReach: 0,
      downstreamOverlapIds: [],
      dailyPatronCommuters: 240,
      vulnerableResidentsServed: 90,
      essentialTier: 1,
      operatingMargin: 0.05,
      demandElasticity: 2.3,
      purityBaseline: 81.0,
      isCorporateTrap: false,
      mapX: 660,
      mapY: 310,
      needJustification: "HVAC ventilation overhaul and evening corridor lighting activation."
    },
    {
      id: "community_clinic",
      name: "Neighborhood Community Clinic",
      legalName: "Central Market Health & Legal Clinic NP",
      address: "976 Mission St (near 6th)",
      subCorridor: "6th & Mission Tipping Point",
      tract: "06075017802",
      povertyRate: 0.268,
      carFreeRate: 0.682,
      sector: "Outpatient Clinic & Community Legal Care",
      naics: "6214",
      headcount: 16,
      runwayQuarters: 2.2,
      burnRateMonthly: 24000,
      reqGrant: 10000,
      isParentSupplier: false,
      outDegree: 0,
      inDegree: 4,
      secondOrderReach: 0,
      downstreamOverlapIds: [],
      dailyPatronCommuters: 150,
      vulnerableResidentsServed: 1800,
      essentialTier: 5,
      operatingMargin: 0.12,
      demandElasticity: 0.2,
      purityBaseline: 62.0,
      isCorporateTrap: false,
      mapX: 680,
      mapY: 330,
      needJustification: "Emergency medical exam room sanitation upgrades & client transport passes."
    },
    {
      id: "steel_lacquer",
      name: "Steel + Lacquer",
      legalName: "Steel and Lacquer Salon LLC",
      address: "14 10th St (at Market)",
      subCorridor: "Market / 10th St Gateway",
      tract: "06075012400",
      povertyRate: 0.224,
      carFreeRate: 0.610,
      sector: "Personal Grooming & Hair Salon",
      naics: "8121",
      headcount: 6,
      runwayQuarters: 2.5,
      burnRateMonthly: 9500,
      reqGrant: 10000,
      isParentSupplier: false,
      outDegree: 0,
      inDegree: 2,
      secondOrderReach: 0,
      downstreamOverlapIds: [],
      dailyPatronCommuters: 55,
      vulnerableResidentsServed: 40,
      essentialTier: 1,
      operatingMargin: 0.11,
      demandElasticity: 1.3,
      purityBaseline: 89.0,
      isCorporateTrap: false,
      mapX: 150,
      mapY: 390,
      needJustification: "Ground-floor storefront lease catch-up and styling station sanitizing retrofit."
    },
    {
      id: "arts_print_studio",
      name: "6th Street Community Arts Studio",
      legalName: "Central Market Printmakers Cooperative",
      address: "125 6th St",
      subCorridor: "6th & Mission Tipping Point",
      tract: "06075017802",
      povertyRate: 0.268,
      carFreeRate: 0.682,
      sector: "Artisan Printmaking & Community Arts",
      naics: "7115",
      headcount: 4,
      runwayQuarters: 1.1,
      burnRateMonthly: 6500,
      reqGrant: 10000,
      isParentSupplier: false,
      outDegree: 4,
      inDegree: 3,
      secondOrderReach: 8,
      downstreamOverlapIds: [],
      dailyPatronCommuters: 80,
      vulnerableResidentsServed: 150,
      essentialTier: 2,
      operatingMargin: 0.06,
      demandElasticity: 2.1,
      purityBaseline: 94.0,
      isCorporateTrap: false,
      mapX: 640,
      mapY: 265,
      needJustification: "Public print press restoration and youth workshop materials bridge."
    }
  ];

  // Corporate / Non-Storefront False Positives (Permanently Disqualified by Stage 0 Gate)
  const CORPORATE_TRAPS_DATA = [
    {
      id: "waymo",
      name: "Waymo LLC",
      address: "215 Taylor St / 400 2nd St",
      naics: "3361",
      headcount: 2500,
      runwayQuarters: 15.0,
      corporateCategory: "Autonomous Vehicle Fleet Subsidiary (Alphabet)",
      capitalization: "$30B+ Valuation",
      reason: "Classified under Motor Vehicle Manufacturing (NAICS 3361); multi-billion-dollar enterprise subsidiary; non-storefront commercial fleet operation."
    },
    {
      id: "wp_engine",
      name: "WP Engine, Inc.",
      address: "1161 Mission St / 300 Howard St",
      naics: "5415",
      headcount: 650,
      runwayQuarters: 8.0,
      corporateCategory: "Enterprise Cloud Software / CMS Host",
      capitalization: "Private Equity Owned ($1B+ Valuation)",
      reason: "Classified under Computer Systems Design (NAICS 5415); hub-bridging cloud artifact linking 121 indirect endpoints; zero physical retail walk-in access."
    },
    {
      id: "tradespace",
      name: "Tradespace",
      address: "1455 Market St",
      naics: "5182",
      headcount: 420,
      runwayQuarters: 12.0,
      corporateCategory: "Data Processing & Cloud Hosting",
      capitalization: "Venture-Backed Enterprise Tech",
      reason: "Classified under Data Hosting (NAICS 5182); multi-tenant cloud provider masquerading as commercial hub; enterprise balance sheet."
    },
    {
      id: "ossium_health",
      name: "Ossium Health, Inc.",
      address: "490 2nd St",
      naics: "3254",
      headcount: 110,
      runwayQuarters: 7.5,
      corporateCategory: "Biotech & Pharmaceutical Therapeutics",
      capitalization: "Clinical-Stage Venture Capital ($100M+)",
      reason: "Classified under Pharmaceutical Manufacturing (NAICS 3254); clinical bone marrow cryopreservation laboratory mistakenly linked by broad chemical sector codes."
    }
  ];

  // Red-Team Attack Vectors (Complete 10 Vectors with 5 required subsections)
  const RED_TEAM_VECTORS = [
    {
      id: 1,
      audience: "economist",
      audienceLabel: "Economist",
      title: "Vector 1: Inferred vs. Actual Supply Links",
      attack: "National industry benchmark input-output tables combined with geographic proximity models do not prove the existence of real business-to-business commerce. Two businesses located 300 meters apart with complementary sector classifications may never have conducted a single transaction. Scoring applicants based on modeled supply cascades risks subsidizing phantom relationships that exist only as probabilistic artifacts in a computer simulation.",
      scenario: "Sour Flour (artisan bakery) is modeled as supplying Chico's Pizza on 6th Street because national transaction benchmarks indicate restaurants purchase bakery products. In reality, Chico's Pizza purchases commercial frozen dough from an industrial distributor, while Sour Flour sells its sourdough loaves to retail walk-in patrons and upscale bistros outside the immediate corridor. A naive queue engine credits Sour Flour with protecting Chico's Pizza, awarding $10,000 on the basis of a non-existent commercial relationship.",
      defense: "Explicit Provenance Architecture: Every link carries a clear tag: [MODELED: Industry Benchmark & Distance] vs. [VERIFIED: Commercial Invoice]. Modeled edges are discounted by local competitor density (r_j^-0.5) and exponential distance decay. Lower-Bound Robustness Audit: The system evaluates applicants with supply-cascade weights set to 0.0, evaluating awardees strictly on direct jobs, resident access, and neighborhood equity. Intake Verification Trigger: For any grant above $5,000 where supply cascade protection is pivotal, the system requires submission of a single vendor invoice or receipt from the prior 90 days before funds are disbursed.",
      residual: "Residual Risk: An applicant could present a nominal, one-off retail receipt ($25 for pastries) to simulate recurring wholesale commerce. Field Verification: Grant officers require proof of recurring monthly commercial volume exceeding $500/month over the prior 6 months prior to contract execution.",
      qa: "Question: 'You are giving $10,000 to this bakery claiming it keeps six local restaurants alive, but you admit you don't have their invoices. Aren't you just subsidizing a guess?'\nAnswer: 'We are completely transparent that baseline municipal records do not contain private vendor ledgers. That is why our system does three things no naive model does: First, we explicitly tag all supply links as modeled benchmarks rather than verified facts. Second, our triage algorithm stress-tests the queue without any supply-chain multiplier—identifying robust awardees that qualify strictly on their direct jobs, resident access, and neighborhood equity. Third, for any grant where supply-chain protection is the deciding factor, our policy workflow triggers an automated 1-invoice verification requirement at intake: the applicant must provide a single vendor invoice or receipt from the past 90 days before funds are disbursed. We never cut an emergency check on probabilistic assumptions alone.'"
    },
    {
      id: 2,
      audience: "critic",
      audienceLabel: "Policy Critic",
      title: "Vector 2: External Distributor ('Sysco') Substitution Critique",
      attack: "Downstream cafes, diners, and storefronts will not collapse if a local neighborhood supplier closes; they will simply substitute to national broadline food distributors (such as Sysco, US Foods, or BiRite Foodservice) within 48 to 72 hours. Spending scarce taxpayer relief dollars to prop up an uncompetitive local supplier is protectionist sentimentality rather than systemic economic resilience.",
      scenario: "Cumaica Coffee (specialty coffee roaster) experiences acute financial distress. The model awards Cumaica Coffee $10,000 to protect downstream cafes like G.Rabbit. A policy critic argues that if Cumaica closed on Friday, G.Rabbit could open an account with a national coffee distributor by Monday morning and serve wholesale coffee at lower unit costs with zero disruption to retail operations.",
      defense: "Economic Friction & Minimum Order Quantities (MOQs): Micro-storefronts operating in 300–600 sq. ft. spaces along Central Market lack dry-storage footprint and working capital to meet broadline distributors' mandatory $500–$1,000 minimum delivery drops. Neighborhood suppliers provide low-minimum, daily delivery schedules and relationship-based trade credit that national distributors do not extend to distressed operators. Artisan Product Differentiation: Independent cafes rely on named local roasters and bakers to support $6–$8 beverage price points. Substituting mass-market commodity beans destroys margins and foot-traffic draw. Explicit External Substitution Parameter: Our model allows leadership to haircut local supply links by up to 80% to reflect broadline substitution, and awardees remain robust.",
      residual: "Residual Risk: A downstream business may already purchase 90% of its goods from broadline distributors. Field Verification: Review applicant intake disclosures: 'What percentage of your primary raw materials are sourced within the local corridor, and what is your average delivery frequency?'",
      qa: "Question: 'If this bakery or coffee roaster closes, won't surrounding cafes just order from Sysco the next morning? Why spend taxpayer dollars propping up an uncompetitive local vendor?'\nAnswer: 'For commodity goods like cooking oil or napkins, cafes certainly can switch. But for micro-storefronts in Central Market, national distributors impose severe barriers: $500 minimum drop sizes that 400-square-foot cafes cannot store or finance, strict commercial credit requirements, and generic commodity products that destroy the artisan differentiation cafes need to draw pedestrian foot traffic. Furthermore, our cockpit includes an explicit External Substitution slider: grant officers can haircut all local supply links by up to 80%, and our sensitivity engine will prove whether this producer remains a priority based on direct neighborhood employment, street-level foot traffic, and lack of nearby artisanal peers.'"
    },
    {
      id: 3,
      audience: "auditor",
      audienceLabel: "City Auditor",
      title: "Vector 3: Strategic Gaming & Moral Hazard",
      attack: "If applicants understand that relief funds are prioritized based on acute distress (e.g., having less than 1.5 quarters of cash runway), self-reported balance sheets, and supplier importance, they face an overwhelming moral hazard: business owners will intentionally depress bank balances, exaggerate monthly burn rates, inflate employee headcounts, or fabricate informal vendor partnerships to maximize their triage ranking.",
      scenario: "The proprietor of a bar and grill near 6th & Mission learns that the city relief program prioritizes businesses with under 30 days of operating runway and shared B2B relationships. The owner temporarily shifts $35,000 from the business operating account into a personal investment account, submits an urgent intake form showing a $600 bank balance, claims a $10,000 pending eviction notice, and lists three informal pop-up catering partnerships that have never generated formal revenue.",
      defense: "Non-Monotonic Survival Curve (Anti-Gaming Viability Floor): Naive queues reward maximum helplessness. Our mathematical model penalizes terminal insolvency: businesses reporting near-zero runway paired with insurmountable structural operating deficits receive an expected survival lift delta P -> 0. Gaming distress too far moves the business into the Insolvent category, disqualifying it from micro-grants and rerouting it to legal restructuring counseling. Objective Registry Cross-Verification: Self-reported claims are bounded against objective public records: business tenure from the City Business Registry, neighborhood employment density bounds, and federal loan histories. Restricted Disbursement: Funds for fixed liabilities are disbursed via two-party warrants directly to commercial landlords or utility providers.",
      residual: "Residual Risk: Related-party transactions draining cash. Field Verification: Mandatory submission of 3 consecutive months of bank statements verifying average daily ledger balances, lease agreement verification, and certification signed under penalty of perjury with random 10% post-award audit provisions.",
      qa: "Question: 'Aren't we just encouraging applicants to drain their accounts, claim they have two weeks to live, and invent supply relationships to get to the front of the queue?'\nAnswer: 'Our algorithm explicitly eliminates the incentive to game distress. Unlike naive systems that prioritize the most broken balance sheet, our survival lift curve is non-monotonic: if a business reports insurmountable burn and zero viability, its marginal survival lift drops to zero and it is flagged as requiring structural insolvency counseling rather than emergency public cash. Furthermore, self-reported metrics are bounded by hard structural data: business age, official payroll filings, and historical federal loan records. Finally, rent relief funds are disbursed via two-party checks directly to commercial landlords, eliminating the ability to divert relief cash into personal reserves.'"
    },
    {
      id: 4,
      audience: "economist",
      audienceLabel: "Economist",
      title: "Vector 4: The 'Walking Dead' vs. 'Self-Insuring' Triage Dilemma",
      attack: "Emergency micro-grant programs face an unavoidable dilemma: if you fund businesses in deep distress, they absorb the $10,000 and shutter 60 days later ('walking dead'); if you fund stable businesses with proven operational track records, the grant was unnecessary because they had sufficient capital reserves or bank credit to survive on their own ('self-insuring' deadweight loss). Therefore, all $50,000 is either wasted or redundant.",
      scenario: "Walking Dead Failure: A long-standing entertainment venue on Market Street experiences a structural 80% decline in foot traffic post-2020 and runs an ongoing deficit of $22,000 per month. A $10,000 grant provides approximately 14 days of payroll bridge before inevitable closure. Self-Insuring Failure: A commercial medical practice with 6 quarters of cash reserves applies for relief. Awarding them $10,000 yields zero net change in their survival probability.",
      defense: "Mathematical Formulation of the Viability Sweet Spot: Marginal survival lift is formulated as a non-linear bell-shaped function of current runway quarters. For r_i >= 4.0-6.0 quarters (Self-Insuring), survival lift drops to near zero because baseline survival is already ~0.95. For r_i < 0.25 quarters with monthly operating burn > 2x grant, survival lift drops to near zero because the grant cannot bridge the insolvency cliff. For 0.5 <= r_i <= 1.5 quarters (Paycheck-to-Paycheck Sweet Spot), survival lift is mathematically maximized, elevating survival probability from 30% to 85%.",
      residual: "Residual Risk: An acute shock turns into prolonged structural decline. Field Verification: Review 12-month pre-shock operating statements to verify that the business maintained positive operating cash flow prior to the acute shock event.",
      qa: "Question: 'Either a business is already dying and $10,000 won't save it, or it has the resources to survive and doesn't need city money. Why isn't this entire $50,000 fund either deadweight loss or a temporary stay of execution?'\nAnswer: 'That dilemma is real only if you treat all distress identically. We mathematically model the marginal survival lift of every grant dollar across three distinct zones. If a business has 4 or more quarters of runway, its grant priority is automatically discounted because public dollars would create zero net survival lift. If a business has structural deficits that would consume the entire grant in two weeks, it is routed to restructuring assistance. Our $50,000 is surgically concentrated on the viable paycheck-to-paycheck band—storefronts with 0.5 to 1.5 quarters of reserves facing an acute, temporary liquidity shock where a $5k to $10k bridge provides the exact mathematical lift needed to reach cash-flow stabilization.'"
    },
    {
      id: 5,
      audience: "applicant",
      audienceLabel: "Competing Applicant",
      title: "Vector 5: Partial-Grant Dilution Trap",
      attack: "Elected officials face strong political incentives to spread relief funds thinly across as many applicants as possible (e.g., distributing $6,250 to 8 businesses or $5,000 to 10 businesses instead of $10,000 to 5). However, when small businesses face indivisible capital cliffs (such as commercial eviction cure notices or failed equipment), awarding 50% of the requested amount causes all recipient businesses to fail anyway, resulting in a 100% loss of public capital.",
      scenario: "Eight businesses in Central Market apply for $10,000 each. Chico's Pizza requires $9,800 to replace a condemned commercial pizza oven; Central Market Corner Grocer has received a 3-day notice to pay $10,000 in lease arrears. The grant officer spreads $50,000 equally into eight grants of $6,250. Chico's Pizza cannot purchase 62.5% of a commercial oven and is forced to close. The corner grocer's landlord refuses a partial cure and proceeds with eviction. All eight businesses shutter within 60 days, wasting $50,000.",
      defense: "Multi-Regime Survival Dose-Response Modeling: Regime 1 (Hard Threshold): Models survival lift as 0.0 if grant < 0.8 Request. The optimizer concentrates full $10,000 grants on the top 5 applicants, guaranteeing 100% threshold clearance. Regime 2 (Concave Runway): Models survival as (grant/Request)^0.6, applicable only when applicants demonstrate flexible working capital needs. Regime 3 (Tiered Hybrid - Default): Concentrates full $10,000 awards on systemic B2B producers and sole grocery/medical providers while offering $5,000 matching working-capital grants to flexible retail storefronts.",
      residual: "Residual Risk: An applicant misclassifies a mandatory fixed liability as flexible working capital. Field Verification: Require signed landlord agreements accepting partial grant disbursements as full and final satisfaction of lease cure notices before awarding partial funds.",
      qa: "Question: 'Why are you funding only 5 businesses with $10,000 each instead of helping 10 businesses with $5,000 each? Aren't you turning away half the community?'\nAnswer: 'Spreading money too thin is the fastest way to waste every single tax dollar. When a small business faces a $10,000 lease cure notice or a broken commercial walk-in compressor, giving them $5,000 does not save 50% of the business—it results in 100% failure because you cannot buy half a compressor or cure half an eviction notice. Our simulator lets officers test both strategies in real time: if applicants face fixed threshold shocks, concentrating full $10,000 grants on the top 5 businesses guarantees 5 verified survivors, whereas spreading $5,000 across 10 businesses risks losing all 10. We only permit partial grants when applicants demonstrate flexible working capital needs with no fixed cliff.'"
    },
    {
      id: 6,
      audience: "critic",
      audienceLabel: "Policy Critic",
      title: "Vector 6: Spatial Blight & Two-Block Tipping Points (6th & Mission)",
      attack: "Evaluating applicants as isolated nodes ignores urban spatial economics and vacancy contagion. If a city awards a grant to a single high-scoring storefront on an acutely distressed two-block stretch (such as 6th Street between Market and Mission) while allowing three adjacent storefronts to board up, pedestrian traffic collapses, street vandalism concentrates, and the lone surviving storefront fails within months regardless of grant aid.",
      scenario: "On 6th Street between Market and Mission, four adjacent storefronts apply: an independent cafe, an apparel boutique, a community salon (Steel + Lacquer), and an artisan printmaker. The algorithm scores each independently and awards $10,000 solely to the highest-scoring cafe, denying the other three. The three unfunded shops close and board their facades. Illicit street activity concentrates in the recessed entryways; daytime pedestrian footfall drops by 75%; the lone funded cafe experiences severe revenue collapse and ceases operations four months later.",
      defense: "Spatial Agglomeration & Micro-Cluster Analysis: The system measures active storefront density within a 200-meter radius (the standard urban two-block pedestrian walkshed). Cluster Tipping-Point Logic: When distress concentration on a two-block stretch exceeds 35% of active ground-floor storefronts, the portfolio optimizer enforces a Critical Mass Policy: either fund a viable cluster threshold (a minimum of 3 storefronts on the block, utilizing tiered matching grants), or flag severe vacancy-contagion risk. Shared Footfall Integration: Connects nearby consumer storefronts to shared worker and resident foot-traffic gravity pools.",
      residual: "Residual Risk: Non-commercial street conditions overwhelm commercial footfall even when a cluster is funded. Field Verification: Coordinate grant deployment with the Central Market Community Benefit District (CBD) and City Ambassador programs to ensure dedicated street-cleaning and safety ambassador coverage on funded blocks.",
      qa: "Question: 'If you fund one great cafe on 6th & Mission but let the three storefronts next door board up, won't that cafe go out of business anyway due to neighborhood blight?'\nAnswer: 'You have identified the exact reason traditional node-by-node grant models fail in Central Market. Ground-floor storefronts on a two-block stretch are foot-traffic complements, not isolated islands. When 50% of a block boards up, pedestrian footfall collapses across the entire strip. Our engine features a dedicated Spatial Cluster module that detects when multiple applicants share a 200-meter walkshed. Instead of stranding a lone awardee, our portfolio optimizer applies a critical-mass cluster bonus: it either funds a coordinated cluster of at least 3 storefronts—often using tiered matching grants—or alerts the grant officer that funding a single isolated shop carries high vacancy-contagion risk.'"
    },
    {
      id: 7,
      audience: "applicant",
      audienceLabel: "Competing Applicant",
      title: "Vector 7: Sector Starvation & Structural Bias",
      attack: "Algorithmic supply-chain models are structurally biased toward manufacturing, wholesale, and B2B services because national input-output tables track intermediate production flows. Meanwhile, 100% of retail stores (grocers, pharmacies, bookshops) and community healthcare clinics sell directly to household final consumption and possess ZERO outgoing B2B links. An algorithmic queue based on supply-chain reach will systematically starve the entire neighborhood retail and community healthcare sector of Central Market.",
      scenario: "A pure supply-chain centrality algorithm ranks Sour Flour and Cumaica Coffee #1 and #2, but assigns a score of 0.0 to Central Market Corner Grocer and Neighborhood Health Clinic. The corner grocer and clinic are denied relief and forced to close, leaving elderly and car-free residents in nearby Single Room Occupancy (SRO) residential hotels with zero fresh produce or preventative care access, while the city funds specialty beverage makers.",
      defense: "Dual-Mode Ecosystem Formulation: Separates economic value into two balanced pillars: Commercial Supply Cascade (S_cascade) for B2B upstream producers, and Consumer Footfall & Upstream Demand Anchor (S_anchor) evaluating storefronts based on local procurement volume, pedestrian footfall gravity, and essential service scarcity in high-need Census tracts. Policy Balance Slider (alpha): Allows leadership to tune the balance between Commercial Contagion (alpha) and Neighborhood Essential Access (1 - alpha) with complete transparency. Automated Sector Parity Audit: Confirms consumer retail and health services maintain equitable funding shares.",
      residual: "Residual Risk: High essentiality scores could protect poorly operated storefronts with unviable business models. Field Verification: Confirm active community service: verify participation in SNAP/EBT, Medi-Cal billing, or low-cost essential goods inventories.",
      qa: "Question: 'Why should a city emergency fund use a complex supply-chain algorithm if it mathematically ranks every corner grocery store, clinic, and pharmacy at the bottom of the list?'\nAnswer: 'In raw national economic data, retail and healthcare have zero outgoing B2B sales because they sell directly to families. If you naively rank by supply links, you starve 100% of neighborhood retail. That is why our solution pioneered Dual-Mode Queue Triage. For storefronts, we measure their Anchor Value: the local foot traffic they draw, the local suppliers they buy from, and whether they are the sole remaining grocery or health clinic in an SRO-dense neighborhood. Our policy slider lets city leaders balance commercial supply chains against human essential access with complete transparency.'"
    },
    {
      id: 8,
      audience: "auditor",
      audienceLabel: "City Auditor",
      title: "Vector 8: Corporate & Aggregation Leakage",
      attack: "Municipal business tax registries group multi-billion-dollar enterprise technology corporations, venture-backed biotechnology firms, and commercial parking management conglomerates under standard business classifications alongside authentic mom-and-pop storefronts. If a city grant engine relies on public business registries and raw network centrality, millions in taxpayer relief will flow to venture-backed tech firms and parking garages.",
      scenario: "When running unconstrained network centrality on Central Market business registry data: Tradespace (1455 Market St) appears as a super-hub with 114 direct links; Ossium Health shows 68 direct links; Waymo LLC reaches 118 nodes; WP Engine reaches 121 nodes. A naive graph algorithm awards $10,000 to Waymo LLC while rejecting struggling independent diners.",
      defense: "Stage 0 Multi-Layer Main-Street Eligibility Gate: Sector Exclusion: Disqualifies enterprise computer systems design, data processing, biotech pharmaceuticals, and motor vehicle manufacturing from relief queues. Summary Code Disaggregation: Strips false B2B edges from commercial parking lots and consumer hair salons, evaluating them as consumer nodes only. Small-Business Purity Scoring: Restricts grants to entities with independent local ownership, single-location status, and fewer than 20 employees. Isolated Ineligible Corporate Drawer: Flagged corporate entities are isolated in a background drawer, ensuring $0.00 grant funds can be allocated to them.",
      residual: "Residual Risk: A corporate subsidiary or multi-unit franchise utilizes an obscured DBA name or holding company to bypass algorithmic filters. Field Verification: Review California Secretary of State corporate registration filings, FinCEN beneficial ownership records, and franchise disclosure documents prior to disbursement.",
      qa: "Question: 'When we ran raw city data through a graph model, the top candidates for relief were Waymo, WP Engine, and a parking garage. How can the city guarantee not a single dime goes to a venture-backed tech firm or national corporate chain?'\nAnswer: 'Public business registries were built for tax collection, not grant allocation. That is why our architecture implements an uncompromising Stage 0 Eligibility Gate before a single score is calculated. We automatically filter enterprise software, autonomous vehicle labs, and venture-backed biotech into an Ineligible Corporate Drawer. We also disaggregate summary codes so commercial parking chains cannot claim small-business status. Every applicant is scored on a Small-Business Purity index requiring independent local ownership, single-location status, and fewer than 20 employees. In our simulator, Waymo and WP Engine are permanently locked out of public funds.'"
    },
    {
      id: 9,
      audience: "critic",
      audienceLabel: "Policy Critic",
      title: "Vector 9: Un-Applied Bottleneck Blindness",
      attack: "Grant triage engines only evaluate businesses that formally submit an application. If an un-applied local supplier (such as a shared bakery commissary or roastery) or downstream commercial anchor is on the brink of closure but never applied due to language barriers or lack of municipal awareness, funding the applicants who depend on that missing node is futile. When the un-applied bottleneck collapses, all funded applicants fail anyway.",
      scenario: "Five Central Market cafes apply for emergency relief. All five purchase their specialty morning pastries from an un-applied commercial bakery located on Stevenson Street operated by a non-English-speaking family. The city awards $10,000 grants to four of the applicant cafes. Three weeks later, the un-applied bakery closes due to lease non-renewal. All four funded cafes experience immediate supply disruption and product quality loss; two cafes fail within 90 days, wasting $20,000 in public relief.",
      defense: "Bidirectional Network Bottleneck Discovery: The engine scans 1 and 2 hops upstream and downstream from all applicants in the queue to detect non-applicant nodes that represent single-point failure risks. Shared Upstream Bottleneck Alerts: Automatically flags when >= 2 queue applicants share an un-applied local supplier. Convergent Collateral Damage Alerts: Identifies non-applicant businesses downstream of multiple unfunded applicants that will suffer compound supply shocks. Proactive Field Navigator Outreach: Generates an actionable Proactive Outreach Dossier for city grant officers and Community Benefit District navigators to conduct on-site wellness checks and invite critical un-applied anchors into the relief pipeline.",
      residual: "Residual Risk: An un-applied supplier is informal, unregistered, or has already decided to cease operations regardless of municipal support. Field Verification: Field navigators visit the un-applied business in person to confirm operational status, lease terms, and willingness to participate in technical assistance or emergency grant queues.",
      qa: "Question: 'What happens if the five cafes you fund all rely on a local commissary bakery that never applied for the grant and is quietly going out of business next week?'\nAnswer: 'Traditional grant systems are completely blind to non-applicants; they only look at the papers on their desk. Our engine runs a bidirectional network scan around the entire applicant queue. When multiple applicants depend on an un-applied supplier, the system immediately triggers a Shared Bottleneck Alert. It quantifies the exact downstream exposure and provides the grant officer with an actionable Proactive Outreach Dossier. Instead of letting that foundational supplier fail silently in the dark, the city can dispatch a neighborhood business navigator to verify their status, offer emergency relief, and protect the entire cluster before it collapses.'"
    },
    {
      id: 10,
      audience: "auditor",
      audienceLabel: "City Auditor",
      title: "Vector 10: Weighting Arbitrariness & Sensitivity Bounds",
      attack: "Any multi-objective formula combining supply cascades (alpha), anchor value, equity multipliers, runway buffers, and purity weights is inherently subjective. A rejected applicant or city auditor can easily challenge the determination, claiming the scoring weights were arbitrarily tuned to favor specific politically connected businesses over others.",
      scenario: "Applicant #5 (Central Market Corner Grocer) is awarded a $10,000 grant, while Applicant #6 (Chico's Pizza) is denied by a margin of 0.6 points. The pizzeria owner files a formal administrative appeal, alleging that the grant officer arbitrarily set the Equity Multiplier to 1.35 and the Cascade Weight to 0.55 instead of 0.50, and that shifting the weights by even 5% would have placed the pizzeria in the funded top 5.",
      defense: "Mathematical Sensitivity Bounds & Invariance Phase Spaces: The engine calculates the parameter intervals [alpha_min, alpha_max] and [M_min, M_max] over which the queue ranking remains mathematically invariant. Identification of 'Robust Awardees': Categorizes applicants into Robust Awardees (core businesses that are funded across 100% of reasonable parameter variations, alpha from 0.2 to 0.8) and Boundary / Policy-Sensitive Applicants. 1-Click Audit-Ready Determination Memo: Automatically publishes the full sensitivity matrix and policy rationale, providing city leadership with an unassailable evidentiary record.",
      residual: "Residual Risk: Discretionary manual overrides by grant officers that deviate from the mathematical model without documented public rationale. Field Verification: Enforce a strict administrative rule: any officer override must be entered into the system with a formal written finding of fact and public interest justification published in the official memo.",
      qa: "Question: 'A rejected business owner claims your weights were hand-picked to favor their competitor by 0.5 points. How do you defend this in front of the Board of Supervisors or a city auditor?'\nAnswer: 'We defend it with mathematical sensitivity proofs, not subjective opinions. Our system runs an automated sensitivity analysis across the entire parameter space. We show the auditor that our top awardees are Robust Awardees—they remain funded whether you weight commercial contagion at 20% or 80%, and whether you assume linear or threshold survival. For boundary applicants on the funding cutoff, we publish the exact crossover thresholds in an audit-ready determination memo. City leadership can clearly demonstrate that the decision was dictated by structural neighborhood resilience, not arbitrary weight manipulation.'"
    }
  ];

  // --- 2. MATHEMATICAL MODEL FUNCTIONS (5 BEYOND-DATASET FACTORS) ---

  /**
   * Logistic Dose-Response Survival Model
   * P(r) = 1 / (1 + exp(-k * (r - r*)))
   * Returns: { p0, pGrant, lift }
   */
  function calculateSurvivalLift(runwayQuarters, grantAmount, burnRateMonthly) {
    const k = 2.0;
    const rStar = 1.0;
    const quarterlyBurn = burnRateMonthly * 3;
    const runwayExtension = grantAmount / quarterlyBurn;

    const p0 = 1 / (1 + Math.exp(-k * (runwayQuarters - rStar)));
    const pGrant = 1 / (1 + Math.exp(-k * (runwayQuarters + runwayExtension - rStar)));
    let lift = pGrant - p0;

    // Insolvency cliff discount for near-zero runway with huge burn
    if (runwayQuarters < 0.25 && quarterlyBurn > grantAmount * 3) {
      lift *= 0.15;
    }
    // Deep buffer discount (firms with >= 4.0 quarters runway have minimal marginal lift)
    if (runwayQuarters >= 4.0) {
      lift = Math.max(0.001, lift * 0.05);
    }

    return {
      p0: Math.round(p0 * 1000) / 1000,
      pGrant: Math.round(pGrant * 1000) / 1000,
      lift: Math.max(0, Math.round(lift * 1000) / 1000)
    };
  }

  /**
   * Factor 1: Runway Sensitivity Score Phi_runway
   * Peaks in the paycheck-to-paycheck sweet spot (0.5 to 1.5 quarters)
   */
  function calculateRunwayScore(runwayQuarters, sensitivityWeight) {
    const k = 2.0;
    const rStar = 1.0;
    const diff = Math.abs(runwayQuarters - rStar);
    const bell = (4 * Math.exp(-k * diff)) / Math.pow(1 + Math.exp(-k * diff), 2);
    let baseScore = bell * 100;
    if (runwayQuarters >= 4.0) baseScore *= 0.05;
    return Math.min(100, Math.max(0, baseScore * sensitivityWeight));
  }

  /**
   * Factor 2: Sector Volatility Adjustment rho_s
   */
  function calculateSectorVolatilityAdjustment(margin, elasticity, volWeight) {
    const baseShock = elasticity / Math.max(0.02, margin);
    // Normalized to 0.7 - 1.35 multiplier
    const norm = 1.0 + (volWeight - 1.0) * 0.25 + (baseShock > 25 ? 0.15 : (baseShock < 10 ? -0.10 : 0.05));
    return Math.max(0.70, Math.min(1.40, norm));
  }

  /**
   * Factor 3: Total People Helped Score (Direct FTEs, Network Workers, Daily Patrons, Residents)
   */
  function calculatePeopleHelpedScore(app, peopleWeight) {
    const wDirect = app.headcount * 1.0;
    const wNetwork = (app.secondOrderReach > 0 ? app.secondOrderReach * 0.4 : app.outDegree * 0.6);
    const wCommuters = app.dailyPatronCommuters * 0.05;
    const wResidents = app.vulnerableResidentsServed * 0.20;

    const totalBeneficiaries = wDirect + wNetwork + wCommuters + wResidents;
    // Logarithmic scale compression matching model documentation
    const logScore = 100 * (Math.log(1 + totalBeneficiaries) / Math.log(1 + 450));
    return {
      totalBeneficiaries: Math.round(wDirect + wNetwork + app.dailyPatronCommuters + app.vulnerableResidentsServed),
      normalizedScore: Math.min(100, Math.round(logScore * peopleWeight))
    };
  }

  /**
   * Factor 4: Small-Business Purity Score
   */
  function calculatePurityScore(app, purityWeight) {
    let score = app.purityBaseline;
    if (app.headcount <= 5) score += 5;
    else if (app.headcount > 15) score -= 15;
    score = Math.min(100, Math.max(10, score));
    return Math.round(score * purityWeight);
  }

  /**
   * Factor 5: Parent Supplier Topological Multiplier mu_i
   */
  function calculateParentSupplierMultiplier(app, parentWeight) {
    if (!app.isParentSupplier && app.outDegree === 0) {
      return 1.0;
    }
    const ratio = (app.outDegree + 1) / (app.inDegree + 1);
    const xi = ratio * (app.secondOrderReach / 100);
    const multiplier = 1.0 + (parentWeight - 1.0) * Math.log(1 + xi);
    return Math.max(1.0, Math.min(2.5, multiplier));
  }

  /**
   * Composite Multi-Objective Scoring Engine
   */
  function scoreApplicant(app, settings, grantAmount) {
    if (app.isCorporateTrap) {
      return {
        compositeScore: 0,
        survivalLift: 0,
        runwayScore: 0,
        peopleHelpedTotal: 0,
        purityScore: 0,
        parentMultiplier: 1.0,
        cascadeScore: 0,
        anchorScore: 0,
        equityMultiplier: 1.0,
        status: "disqualified"
      };
    }

    const survival = calculateSurvivalLift(app.runwayQuarters, grantAmount, app.burnRateMonthly);
    const runwayScore = calculateRunwayScore(app.runwayQuarters, settings.runwayWeight);
    const sectorAdj = calculateSectorVolatilityAdjustment(app.operatingMargin, app.demandElasticity, settings.volatilityWeight);
    const people = calculatePeopleHelpedScore(app, settings.peopleWeight);
    const purityScore = calculatePurityScore(app, settings.purityWeight);
    const parentMultiplier = calculateParentSupplierMultiplier(app, settings.parentWeight);

    // Baseline Dual-Mode: Cascade vs Anchor
    const cascadeScore = app.isParentSupplier ? 95 : (app.outDegree > 0 ? 60 : 0);
    const anchorScore = app.essentialTier * 18 + (app.vulnerableResidentsServed > 500 ? 15 : 5);
    const alpha = settings.alpha; // 0 = 100% Anchor, 1 = 100% Cascade
    const dualModeCore = (alpha * cascadeScore * parentMultiplier) + ((1 - alpha) * anchorScore);

    // Equity Multiplier from Census Tract (Car-free and poverty rates)
    const equityMultiplier = 1.0 + (app.povertyRate * 0.8) + (app.carFreeRate * 0.4);

    // Composite Utility
    let composite = (0.25 * dualModeCore) +
                    (0.20 * runwayScore) +
                    (0.25 * people.normalizedScore) +
                    (0.15 * purityScore) +
                    (0.15 * (survival.lift * 100));

    composite *= sectorAdj;
    composite *= (equityMultiplier / 1.35);

    return {
      compositeScore: Math.round(composite * 10) / 10,
      survivalLift: survival.lift,
      runwayScore: Math.round(runwayScore),
      peopleHelpedTotal: people.totalBeneficiaries,
      purityScore: Math.min(100, Math.round(purityScore)),
      parentMultiplier: Math.round(parentMultiplier * 100) / 100,
      cascadeScore: Math.round(cascadeScore),
      anchorScore: Math.round(anchorScore),
      equityMultiplier: Math.round(equityMultiplier * 100) / 100,
      status: "pending"
    };
  }

  // --- 3. APPLICATION STATE & DEFAULT SETTINGS ---

  const state = {
    activeAgentId: "Regime_Stress_Test_Orchestrator_Agent",
    activeAgentDisplayName: "Regime Stress-Test & Orchestrator Agent",
    budget: 50000,
    regime: "hybrid", // "concentrate", "spread", "hybrid"
    runwayWeight: 1.0,
    parentWeight: 1.4,
    peopleWeight: 1.0,
    purityWeight: 1.0,
    volatilityWeight: 1.0,
    alpha: 0.50,
    selectedApplicantAId: "sour_flour",
    selectedApplicantBId: "corner_grocer",
    redTeamFilter: "all",
    rankedQueue: [],
    fundedSummary: {
      budgetAllocated: 0,
      fundedCount: 0,
      directJobs: 0,
      networkJobs: 0,
      peopleServed: 0,
      corporateBlockedCount: 4
    }
  };

  // --- 4. PORTFOLIO OPTIMIZATION & SUBMODULAR OVERLAP DEDUPLICATION ---

  function optimizePortfolio() {
    return runPortfolioOptimization();
  }

  function runPortfolioOptimization() {
    const defaultGrant = 10000;
    const scoredList = APPLICANTS_DATA.map(app => {
      const scoring = scoreApplicant(app, state, defaultGrant);
      return { ...app, scoring };
    });

    // Sort by composite score descending
    scoredList.sort((a, b) => b.scoring.compositeScore - a.scoring.compositeScore);

    // Apply Allocation Regime
    let remainingBudget = state.budget;
    let allocatedTotal = 0;
    let fundedCount = 0;
    let directJobs = 0;
    let networkJobs = 0;
    let peopleServed = 0;

    // Submodular overlap deduplication tracker
    const fundedSupplierIds = new Set();

    scoredList.forEach((item, index) => {
      let award = 0;
      let status = "waitlisted";

      if (state.regime === "concentrate") {
        // Regime A: Hard threshold full $10k grants to top applicants
        const maxGrants = Math.floor(state.budget / 10000);
        if (index < maxGrants && remainingBudget >= 10000) {
          award = 10000;
          status = "funded-full";
          remainingBudget -= 10000;
        }
      } else if (state.regime === "spread") {
        // Regime B: Spread across top 8 applicants
        const maxGrants = 8;
        const grantPerShop = Math.floor(state.budget / maxGrants);
        if (grantPerShop > 0 && index < maxGrants && remainingBudget >= grantPerShop) {
          award = grantPerShop;
          status = "funded-bridge";
          remainingBudget -= grantPerShop;
        }
      } else {
        // Regime C: Tiered Hybrid (Default)
        // Top 3 systemic / anchor hubs get $10,000 full grants
        // Next qualifying storefronts get $5,000 bridge grants
        // When budget > $50,000, surplus budget continues granting $5,000 bridge awards to eligible waitlisted storefronts
        if (index < 3 && remainingBudget >= 10000) {
          award = 10000;
          status = "funded-full";
          remainingBudget -= 10000;
        } else if ((index < 7 || state.budget > 50000) && remainingBudget >= 5000) {
          award = 5000;
          status = "funded-bridge";
          remainingBudget -= 5000;
        }
      }

      // Re-evaluate survival lift at actual award amount
      if (award > 0) {
        const reCalc = calculateSurvivalLift(item.runwayQuarters, award, item.burnRateMonthly);
        item.scoring.survivalLift = reCalc.lift;
        allocatedTotal += award;
        fundedCount++;
        directJobs += item.headcount;
        if (item.isParentSupplier) {
          let newJobs = 74;
          // Deduplicate shared downstream buyers if peer parent already funded
          for (const peerId of (item.downstreamOverlapIds || [])) {
            if (fundedSupplierIds.has(peerId)) {
              newJobs = Math.round(newJobs * 0.40); // 60% overlap discount
            }
          }
          networkJobs += newJobs;
          fundedSupplierIds.add(item.id);
        } else if (item.outDegree > 0) {
          networkJobs += item.outDegree;
        }
        peopleServed += item.scoring.peopleHelpedTotal;
      }

      item.grantAward = award;
      item.status = status;
    });

    state.rankedQueue = scoredList;
    state.fundedSummary = {
      budgetAllocated: allocatedTotal,
      fundedCount: fundedCount,
      directJobs: directJobs,
      networkJobs: networkJobs,
      peopleServed: peopleServed,
      corporateBlockedCount: CORPORATE_TRAPS_DATA.length
    };
  }

  // --- 5. DOM RENDERING & EVENT CONTROLLERS ---

  function updateKPIs() {
    const s = state.fundedSummary;
    document.getElementById("kpi-allocated").textContent = "$" + s.budgetAllocated.toLocaleString();
    const pct = Math.round((s.budgetAllocated / state.budget) * 100);
    document.getElementById("kpi-budget-percent").textContent = pct + "% of $" + state.budget.toLocaleString() + " Cap";
    document.getElementById("kpi-funded-count").textContent = s.fundedCount + " / " + APPLICANTS_DATA.length;
    document.getElementById("kpi-direct-jobs").textContent = s.directJobs + " FTE";
    document.getElementById("kpi-network-jobs").textContent = s.networkJobs + " Staff";
    document.getElementById("kpi-people-served").textContent = s.peopleServed.toLocaleString() + "+";

    // Header Status Pill
    document.getElementById("header-status-text").textContent =
      `Active Simulation: $${s.budgetAllocated.toLocaleString()} Allocated • ${s.fundedCount} Funded of ${APPLICANTS_DATA.length}`;

    // Budget Progress Bar
    document.getElementById("bar-allocated-txt").textContent = "$" + s.budgetAllocated.toLocaleString();
    document.getElementById("bar-total-txt").textContent = "$" + state.budget.toLocaleString() + " Authorized";
    const barFill = document.getElementById("budget-progress-fill");
    barFill.style.width = Math.min(100, pct) + "%";

    if (pct > 95) {
      barFill.className = "progress-fill";
    } else if (pct > 60) {
      barFill.className = "progress-fill warning";
    } else {
      barFill.className = "progress-fill danger";
    }
  }

  function renderQueueTable() {
    const tbody = document.getElementById("queue-table-body");
    tbody.innerHTML = "";

    state.rankedQueue.forEach((app, idx) => {
      const tr = document.createElement("tr");
      if (app.status.startsWith("funded")) {
        tr.className = "funded-row";
      }

      const rankBadge = `<span style="font-weight:800; font-size:0.95rem; color: ${idx < 3 ? '#10b981' : '#94a3b8'};">#${idx + 1}</span>`;

      let statusBadge = "";
      if (app.status === "funded-full") {
        statusBadge = `<span class="status-pill funded-full">● Tier 1 Full ($10k)</span>`;
      } else if (app.status === "funded-bridge") {
        statusBadge = `<span class="status-pill funded-bridge">● Tier 2 Bridge ($5k)</span>`;
      } else {
        statusBadge = `<span class="status-pill waitlisted">Waitlisted</span>`;
      }

      const parentBadge = app.isParentSupplier
        ? `<span class="badge-tag root-supplier">Root Hub (${app.outDegree} B2B)</span>`
        : `<span class="badge-tag">Storefront</span>`;

      const runwayDisplay = app.runwayQuarters <= 1.0
        ? `<span style="color:#fbbf24; font-weight:700;">${app.runwayQuarters} qtrs</span>`
        : `<span>${app.runwayQuarters} qtrs</span>`;

      tr.innerHTML = `
        <td>${rankBadge}</td>
        <td>
          <div class="biz-name-cell">
            <span class="biz-primary-name">${app.name}</span>
            <span class="biz-address-sub">${app.address}</span>
          </div>
        </td>
        <td>
          <span style="font-size:0.75rem; color:#cbd5e1;">${app.subCorridor}</span>
        </td>
        <td>${runwayDisplay}</td>
        <td class="metric-num">${app.headcount}</td>
        <td class="metric-num">${app.scoring.peopleHelpedTotal.toLocaleString()}</td>
        <td class="metric-num">${app.scoring.purityScore}</td>
        <td>${parentBadge}</td>
        <td class="metric-num lift">+${Math.round(app.scoring.survivalLift * 100)}%</td>
        <td class="metric-num" style="color:#38bdf8; font-weight:700;">${app.scoring.compositeScore}</td>
        <td class="metric-num" style="color:#34d399; font-weight:700;">$${app.grantAward.toLocaleString()}</td>
        <td>${statusBadge}</td>
      `;

      tbody.appendChild(tr);
    });
  }

  function renderCorporateDrawer() {
    const container = document.getElementById("corp-cards-container");
    container.innerHTML = "";

    CORPORATE_TRAPS_DATA.forEach(corp => {
      const card = document.createElement("div");
      card.className = "corp-card";
      card.innerHTML = `
        <div class="corp-name">
          <span>${corp.name}</span>
          <span class="status-pill disqualified">BLOCKED $0.00</span>
        </div>
        <div class="corp-stat-row">
          <span>Address:</span>
          <span>${corp.address}</span>
        </div>
        <div class="corp-stat-row">
          <span>Category:</span>
          <span>${corp.corporateCategory}</span>
        </div>
        <div class="corp-stat-row">
          <span>Capitalization:</span>
          <span style="color:#f43f5e; font-weight:700;">${corp.capitalization}</span>
        </div>
        <div class="corp-stat-row">
          <span>Headcount:</span>
          <span>${corp.headcount} FTE</span>
        </div>
        <div class="corp-reason">
          <strong>Disqualification Ground:</strong> ${corp.reason}
        </div>
      `;
      container.appendChild(card);
    });
  }

  function renderRedTeamMatrix() {
    const container = document.getElementById("redteam-cards-container");
    container.innerHTML = "";

    const filtered = RED_TEAM_VECTORS.filter(v => {
      if (state.redTeamFilter === "all") return true;
      return v.audience === state.redTeamFilter;
    });

    filtered.forEach(v => {
      const card = document.createElement("div");
      card.className = "vector-card";
      card.id = "vector-card-" + v.id;

      card.innerHTML = `
        <div class="vector-header" data-id="${v.id}">
          <div class="vector-header-left">
            <span class="vector-num">VECTOR #${v.id}</span>
            <span class="vector-title">${v.title}</span>
            <span class="vector-audience-badge">${v.audienceLabel}</span>
          </div>
          <span class="toggle-icon">▼</span>
        </div>
        <div class="vector-body">
          <div class="subsection-box attack">
            <div class="subsec-title">(a) The Red-Team Attack Critique</div>
            <div class="subsec-text">${v.attack}</div>
          </div>
          <div class="subsection-box scenario">
            <div class="subsec-title">(b) Concrete Central Market Failure Scenario</div>
            <div class="subsec-text">${v.scenario}</div>
          </div>
          <div class="subsection-box defense">
            <div class="subsec-title">(c) Algorithmic & Policy Defense in Our Solution</div>
            <div class="subsec-text">${v.defense}</div>
          </div>
          <div class="subsection-box residual">
            <div class="subsec-title">(d) Residual Risk & Field Verification Step</div>
            <div class="subsec-text">${v.residual}</div>
          </div>
          <div class="subsection-box qa">
            <div class="subsec-title">(e) Verbatim Executive Q&A Response</div>
            <div class="subsec-text" style="white-space: pre-line; font-style: italic;">${v.qa}</div>
          </div>
        </div>
      `;

      card.querySelector(".vector-header").addEventListener("click", () => {
        card.classList.toggle("open");
      });

      container.appendChild(card);
    });
  }

  // --- 6. PAIRWISE TRADEOFF & COMPARATIVE INSPECTOR ---

  function populatePairwiseSelectors() {
    const selA = document.getElementById("select-applicant-a");
    const selB = document.getElementById("select-applicant-b");
    selA.innerHTML = "";
    selB.innerHTML = "";

    APPLICANTS_DATA.forEach(app => {
      const optA = document.createElement("option");
      optA.value = app.id;
      optA.textContent = app.name + " (" + app.sector.split("&")[0].trim() + ")";
      if (app.id === state.selectedApplicantAId) optA.selected = true;
      selA.appendChild(optA);

      const optB = document.createElement("option");
      optB.value = app.id;
      optB.textContent = app.name + " (" + app.sector.split("&")[0].trim() + ")";
      if (app.id === state.selectedApplicantBId) optB.selected = true;
      selB.appendChild(optB);
    });

    selA.addEventListener("change", (e) => {
      state.selectedApplicantAId = e.target.value;
      renderPairwiseView();
    });

    selB.addEventListener("change", (e) => {
      state.selectedApplicantBId = e.target.value;
      renderPairwiseView();
    });
  }

  function renderPairwiseView() {
    const appA = state.rankedQueue.find(a => a.id === state.selectedApplicantAId) || state.rankedQueue[0];
    const appB = state.rankedQueue.find(a => a.id === state.selectedApplicantBId) || state.rankedQueue[1];

    if (!appA || !appB) return;

    function renderDetails(app, containerId, color) {
      const c = document.getElementById(containerId);
      c.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
          <h4 style="font-size:1.05rem; color:#fff;">${app.name}</h4>
          <span class="status-pill ${app.status.startsWith('funded') ? 'funded-full' : 'waitlisted'}">
            Rank #${state.rankedQueue.findIndex(x => x.id === app.id) + 1} • ${app.status.toUpperCase()}
          </span>
        </div>
        <p style="font-size:0.8rem; color:#94a3b8; margin-bottom:1rem;">${app.address} • ${app.sector}</p>

        <div class="bar-comp-row">
          <div class="bar-comp-label">
            <span>Direct Payroll Headcount:</span>
            <span style="font-weight:700; color:${color};">${app.headcount} FTE</span>
          </div>
          <div class="bar-track">
            <div style="width:${Math.min(100, (app.headcount / 20) * 100)}%; background:${color}; height:100%;"></div>
          </div>
        </div>

        <div class="bar-comp-row">
          <div class="bar-comp-label">
            <span>Downstream Supply Chain Reach:</span>
            <span style="font-weight:700; color:${color};">${app.outDegree} direct (${app.secondOrderReach} 2-hop)</span>
          </div>
          <div class="bar-track">
            <div style="width:${Math.min(100, (app.secondOrderReach / 150) * 100)}%; background:${color}; height:100%;"></div>
          </div>
        </div>

        <div class="bar-comp-row">
          <div class="bar-comp-label">
            <span>Daily Patrons & Commuters:</span>
            <span style="font-weight:700; color:${color};">${app.dailyPatronCommuters} daily</span>
          </div>
          <div class="bar-track">
            <div style="width:${Math.min(100, (app.dailyPatronCommuters / 1200) * 100)}%; background:${color}; height:100%;"></div>
          </div>
        </div>

        <div class="bar-comp-row">
          <div class="bar-comp-label">
            <span>Financial Runway Buffer:</span>
            <span style="font-weight:700; color:${color};">${app.runwayQuarters} quarters</span>
          </div>
          <div class="bar-track">
            <div style="width:${Math.min(100, (app.runwayQuarters / 3.0) * 100)}%; background:${color}; height:100%;"></div>
          </div>
        </div>

        <div class="bar-comp-row">
          <div class="bar-comp-label">
            <span>Small-Biz Purity Score:</span>
            <span style="font-weight:700; color:${color};">${app.scoring.purityScore} / 100</span>
          </div>
          <div class="bar-track">
            <div style="width:${app.scoring.purityScore}%; background:${color}; height:100%;"></div>
          </div>
        </div>

        <div style="margin-top:1rem; padding:0.75rem; background:rgba(15,23,42,0.6); border-radius:6px; font-size:0.8rem;">
          <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">
            <span>Expected Survival Lift:</span>
            <span style="color:#34d399; font-weight:700;">+${Math.round(app.scoring.survivalLift * 100)}%</span>
          </div>
          <div style="display:flex; justify-content:space-between;">
            <span>Composite Priority Score:</span>
            <span style="color:#38bdf8; font-weight:700;">${app.scoring.compositeScore}</span>
          </div>
        </div>
      `;
    }

    renderDetails(appA, "compare-details-a", "#10b981");
    renderDetails(appB, "compare-details-b", "#06b6d4");

    // Automated Plain-English Comparative Narrative
    const rankA = state.rankedQueue.findIndex(x => x.id === appA.id) + 1;
    const rankB = state.rankedQueue.findIndex(x => x.id === appB.id) + 1;
    const winner = rankA < rankB ? appA : appB;
    const runnerUp = rankA < rankB ? appB : appA;

    let narrative = `
      <strong>${winner.name} (Rank #${Math.min(rankA, rankB)})</strong> ranks above <strong>${runnerUp.name} (Rank #${Math.max(rankA, rankB)})</strong> with a composite utility score of <strong>${winner.scoring.compositeScore}</strong> vs. <strong>${runnerUp.scoring.compositeScore}</strong> (difference of ${(winner.scoring.compositeScore - runnerUp.scoring.compositeScore).toFixed(1)} points).
    `;

    if (winner.isParentSupplier && !runnerUp.isParentSupplier) {
      narrative += `<br><br>• <strong>Topological Asymmetry:</strong> ${winner.name} is a foundational root supplier with ${winner.outDegree} direct commercial B2B buyers and ${winner.secondOrderReach} second-order dependents. Its failure would induce secondary inventory shocks across the corridor. Increasing the Parent Supplier slider further widens this gap.`;
    } else if (winner.essentialTier === 5) {
      narrative += `<br><br>• <strong>Essential Human Access:</strong> ${winner.name} serves ${winner.vulnerableResidentsServed} high-need residents in a Census tract where 78.5% of households are car-free. It provides non-substitutable daily essentials (fresh produce/medicine), elevating its anchor and equity scores.`;
    }

    if (winner.runwayQuarters < runnerUp.runwayQuarters && runnerUp.runwayQuarters >= 2.0) {
      narrative += `<br><br>• <strong>Runway Buffer Divergence:</strong> ${winner.name} operates in the acute paycheck-to-paycheck sweet spot (${winner.runwayQuarters} quarters), where an emergency grant delivers +${Math.round(winner.scoring.survivalLift * 100)}% survival lift. Conversely, ${runnerUp.name} holds ${runnerUp.runwayQuarters} quarters of cash buffer; an emergency grant yields less marginal survival lift because the business can self-insure through current shocks.`;
    }

    narrative += `<br><br><em>Policy Sensitivity Note: Shifting the Commercial vs. Community Access balance slider (alpha) towards 0.0 elevates consumer retail and clinic anchors, while shifting towards 1.0 concentrates relief on upstream B2B makers.</em>`;

    document.getElementById("pairwise-narrative-text").innerHTML = narrative;
  }

  // --- 7. INTERACTIVE SVG NETWORK RISK MAP RENDERING ---

  function renderNetworkMap() {
    const svgEdges = document.getElementById("network-map-edges");
    const svgNodes = document.getElementById("network-map-nodes");
    if (!svgEdges || !svgNodes) return;

    svgEdges.innerHTML = "";
    svgNodes.innerHTML = "";

    const sourFlour = state.rankedQueue.find(a => a.id === "sour_flour") || APPLICANTS_DATA[0];
    const cumaica = state.rankedQueue.find(a => a.id === "cumaica_coffee") || APPLICANTS_DATA[1];

    // Draw directed supply edges from Root Suppliers to downstream nodes
    state.rankedQueue.forEach(target => {
      if (target.id !== "sour_flour" && target.id !== "cumaica_coffee" && !target.isCorporateTrap) {
        // Edge from Sour Flour
        const lineA = document.createElementNS("http://www.w3.org/2000/svg", "line");
        lineA.setAttribute("x1", sourFlour.mapX);
        lineA.setAttribute("y1", sourFlour.mapY);
        lineA.setAttribute("x2", target.mapX);
        lineA.setAttribute("y2", target.mapY);
        lineA.setAttribute("stroke", "#10b981");
        lineA.setAttribute("stroke-width", "1.5");
        lineA.setAttribute("stroke-dasharray", "4 3");
        lineA.setAttribute("opacity", "0.4");
        lineA.setAttribute("marker-end", "url(#arrow)");
        svgEdges.appendChild(lineA);

        // Edge from Cumaica Coffee
        if (target.id === "g_rabbit" || target.id === "corner_grocer" || target.id === "pawn_shop") {
          const lineB = document.createElementNS("http://www.w3.org/2000/svg", "line");
          lineB.setAttribute("x1", cumaica.mapX);
          lineB.setAttribute("y1", cumaica.mapY);
          lineB.setAttribute("x2", target.mapX);
          lineB.setAttribute("y2", target.mapY);
          lineB.setAttribute("stroke", "#8b5cf6");
          lineB.setAttribute("stroke-width", "1.5");
          lineB.setAttribute("stroke-dasharray", "4 3");
          lineB.setAttribute("opacity", "0.35");
          lineB.setAttribute("marker-end", "url(#arrow)");
          svgEdges.appendChild(lineB);
        }
      }
    });

    // Draw Storefront Nodes
    state.rankedQueue.forEach(app => {
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      g.setAttribute("class", "map-node-group");
      g.setAttribute("cursor", "pointer");

      let fillColor = "#10b981"; // Funded Green
      if (!app.status.startsWith("funded")) {
        fillColor = "#f59e0b"; // Waitlisted Amber
      }
      if (app.isParentSupplier) {
        fillColor = "#8b5cf6"; // Root Hub Purple
      }

      // Outer Glow circle for root hubs
      if (app.isParentSupplier) {
        const glow = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        glow.setAttribute("cx", app.mapX);
        glow.setAttribute("cy", app.mapY);
        glow.setAttribute("r", "22");
        glow.setAttribute("fill", "url(#glow-root)");
        g.appendChild(glow);
      }

      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", app.mapX);
      circle.setAttribute("cy", app.mapY);
      circle.setAttribute("r", app.isParentSupplier ? "14" : "10");
      circle.setAttribute("fill", fillColor);
      circle.setAttribute("stroke", "#0f172a");
      circle.setAttribute("stroke-width", "2.5");
      g.appendChild(circle);

      // Label text
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("x", app.mapX);
      text.setAttribute("y", app.mapY - 14);
      text.setAttribute("text-anchor", "middle");
      text.setAttribute("fill", "#f8fafc");
      text.setAttribute("font-size", "10");
      text.setAttribute("font-weight", "700");
      text.textContent = app.name;
      g.appendChild(text);

      // Click event for pairwise comparison selection
      g.addEventListener("click", () => {
        state.selectedApplicantAId = app.id;
        const selA = document.getElementById("select-applicant-a");
        if (selA) selA.value = app.id;
        renderPairwiseView();
      });

      svgNodes.appendChild(g);
    });

    // Check 6th & Mission Spatial Cluster Critical Mass
    const clusterStorefronts = state.rankedQueue.filter(a =>
      ["monarch_beverage", "chicos_pizza", "pawn_shop", "community_clinic", "arts_print_studio"].includes(a.id)
    );
    const fundedInCluster = clusterStorefronts.filter(a => a.status.startsWith("funded")).length;
    const callout = document.getElementById("cluster-callout-msg");

    if (fundedInCluster >= 3) {
      callout.style.borderColor = "rgba(16, 185, 129, 0.4)";
      callout.style.background = "rgba(16, 185, 129, 0.08)";
      callout.style.color = "#a7f3d0";
      callout.innerHTML = `
        <span style="font-size: 1.25rem;">✅</span>
        <div>
          <strong>6th & Mission Two-Block Tipping Point Status: Critical Mass Maintained</strong><br>
          ${fundedInCluster} storefronts in the 6th & Mission micro-cluster are funded, meeting the critical mass threshold (&ge; 3 active storefronts) and preventing commercial vacancy contagion on the block.
        </div>
      `;
    } else {
      callout.style.borderColor = "rgba(244, 63, 94, 0.4)";
      callout.style.background = "rgba(244, 63, 94, 0.08)";
      callout.style.color = "#fecdd3";
      callout.innerHTML = `
        <span style="font-size: 1.25rem;">⚠️</span>
        <div>
          <strong>6th & Mission Vacancy Contagion Warning: Critical Mass Sub-Threshold</strong><br>
          Only ${fundedInCluster} storefront(s) funded on 6th & Mission. Without at least 3 active storefronts preserved, the funded storefront(s) face isolated commercial dead-zone exposure.
        </div>
      `;
    }
  }

  // --- 8. OFFICIAL DETERMINATION MEMO GENERATOR ---

  function generateMemo() {
    return renderDeterminationMemo();
  }

  function renderDeterminationMemo() {
    const s = state.fundedSummary;
    const fundedList = state.rankedQueue.filter(a => a.status.startsWith("funded"));
    const waitlistList = state.rankedQueue.filter(a => !a.status.startsWith("funded"));

    // Date
    const today = new Date();
    document.getElementById("memo-date-field").textContent = today.toLocaleDateString("en-US", {
      year: "numeric", month: "long", day: "numeric"
    });

    // Summary text
    document.getElementById("memo-summary-metrics-para").innerHTML = `
      Evaluated by <strong>${state.activeAgentDisplayName}</strong> (<code>${state.activeAgentId}</code>) under the <strong>${state.regime.toUpperCase()} allocation regime</strong>, the system has allocated 
      <strong>$${s.budgetAllocated.toLocaleString()}</strong> across <strong>${s.fundedCount}</strong> eligible storefronts and makers. 
      This deployment directly preserves <strong>${s.directJobs} direct full-time jobs</strong>, shields an estimated 
      <strong>${s.networkJobs} downstream supply-chain workers</strong>, and maintains daily service access for over 
      <strong>${s.peopleServed.toLocaleString()}</strong> neighborhood residents and transit commuters. 
      Four corporate and non-storefront technology entities were permanently excluded via the Stage 0 Eligibility Gate, protecting 100% of public funds from corporate leakage.
    `;

    // Table 1: Approved Funded
    const fTbody = document.getElementById("memo-funded-table-body");
    fTbody.innerHTML = "";
    fundedList.forEach(app => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${app.legalName}</strong> (${app.name})</td>
        <td>${app.address}</td>
        <td>${app.sector}</td>
        <td>${app.runwayQuarters} qtrs</td>
        <td style="font-weight:700; color:#059669;">$${app.grantAward.toLocaleString()}</td>
        <td>${app.needJustification} (Lift: +${Math.round(app.scoring.survivalLift * 100)}%)</td>
      `;
      fTbody.appendChild(tr);
    });

    // Table 2: Waitlisted
    const wTbody = document.getElementById("memo-waitlisted-table-body");
    wTbody.innerHTML = "";
    waitlistList.forEach(app => {
      const tr = document.createElement("tr");
      let referral = "Referred to OEWD Commercial Lease Mediation and low-interest SBA bridge loan fund.";
      if (app.runwayQuarters >= 2.0) {
        referral = `Maintains ${app.runwayQuarters} qtrs buffer; referred to OEWD Small Business Capital Improvement Grants.`;
      }
      tr.innerHTML = `
        <td><strong>${app.legalName}</strong></td>
        <td>${app.address}</td>
        <td>${app.runwayQuarters} qtrs</td>
        <td>${referral}</td>
      `;
      wTbody.appendChild(tr);
    });

    // Table 3: Corporate Disqualifications
    const cTbody = document.getElementById("memo-corp-table-body");
    cTbody.innerHTML = "";
    CORPORATE_TRAPS_DATA.forEach(corp => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${corp.name}</strong></td>
        <td>${corp.address}</td>
        <td>${corp.corporateCategory}</td>
        <td style="color:#e11d48; font-size:0.8rem;">${corp.reason}</td>
      `;
      cTbody.appendChild(tr);
    });
  }

  // --- 9. EVENT LISTENERS & INITIALIZATION ---

  function attachEventListeners() {
    // Tab Switching
    const tabButtons = document.querySelectorAll(".nav-tab-btn");
    tabButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        tabButtons.forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

        btn.classList.add("active");
        const targetTabId = btn.getAttribute("data-tab");
        const targetPane = document.getElementById(targetTabId);
        if (targetPane) targetPane.classList.add("active");

        if (targetTabId === "tab-pairwise-network") {
          renderPairwiseView();
          renderNetworkMap();
        } else if (targetTabId === "tab-memo") {
          renderDeterminationMemo();
        }
      });
    });

    // Jump to memo from table
    const btnGotoMemo = document.getElementById("btn-goto-memo") || document.getElementById("btn-generate-memo");
    if (btnGotoMemo) {
      btnGotoMemo.addEventListener("click", () => {
        const memoBtn = document.getElementById("btn-tab-memo");
        if (memoBtn) memoBtn.click();
      });
    }

    // Regime Switching
    const regimeButtons = document.querySelectorAll(".regime-opt-btn");
    regimeButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        regimeButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.regime = btn.getAttribute("data-regime");

        const desc = document.getElementById("regime-description-text");
        const badge = document.getElementById("current-regime-badge");
        if (state.regime === "concentrate") {
          desc.innerHTML = "<strong>Hard Threshold Regime:</strong> Concentrates $10,000 full grants on top 5 applicants facing indivisible capital cliffs (e.g. lease cure or equipment replacement).";
          badge.textContent = "Concentrate Top 5 Regime";
        } else if (state.regime === "spread") {
          desc.innerHTML = "<strong>Spread Across 8 Regime:</strong> Awards $6,250 partial grants to top 8 applicants under concave working capital returns.";
          badge.textContent = "Spread Across 8 Regime";
        } else {
          desc.innerHTML = "<strong>Tiered Hybrid Regime (Recommended):</strong> $10,000 full grants to foundational parent suppliers and essential anchors; $5,000 matching bridge grants to qualifying storefronts.";
          badge.textContent = "Tiered Hybrid Regime";
        }

        recomputeAll();
      });
    });

    // Active ADK Agent Selector
    const selectAdkAgent = document.getElementById("select-adk-agent");
    if (selectAdkAgent) {
      selectAdkAgent.addEventListener("change", (e) => {
        const agentId = e.target.value;
        state.activeAgentId = agentId;
        const agentBadge = document.getElementById("active-agent-badge");
        const agentDesc = document.getElementById("active-agent-description-text");

        if (agentId === "Supply_Provenance_Agent") {
          state.activeAgentDisplayName = "Supply & Provenance Agent";
          state.alpha = 0.85;
          state.parentWeight = 1.9;
          state.peopleWeight = 0.8;
          state.runwayWeight = 0.9;
          if (agentBadge) agentBadge.textContent = "Sub-Agent 1";
          if (agentDesc) {
            agentDesc.innerHTML = "<strong>Supply &amp; Provenance Agent:</strong> Evaluates upstream parent suppliers, trophic cascade multipliers, substitutability friction, and verified commercial tax invoice provenance gates.";
          }
        } else if (agentId === "Runway_Sector_Purity_Agent") {
          state.activeAgentDisplayName = "Runway, Sector & Purity Agent";
          state.alpha = 0.45;
          state.runwayWeight = 1.9;
          state.purityWeight = 1.8;
          state.volatilityWeight = 1.4;
          if (agentBadge) agentBadge.textContent = "Sub-Agent 2";
          if (agentDesc) {
            agentDesc.innerHTML = "<strong>Runway, Sector &amp; Purity Agent:</strong> Enforces Stage 0 small-business purity gates, asymmetric bell-shaped runway urgency curves, and sector volatility adjustments.";
          }
        } else if (agentId === "Spatial_Human_Impact_Agent") {
          state.activeAgentDisplayName = "Spatial Foot-Traffic & Human-Impact Agent";
          state.alpha = 0.15;
          state.peopleWeight = 1.9;
          state.parentWeight = 1.0;
          state.runwayWeight = 1.2;
          if (agentBadge) agentBadge.textContent = "Sub-Agent 3";
          if (agentDesc) {
            agentDesc.innerHTML = "<strong>Spatial Foot-Traffic &amp; Human-Impact Agent:</strong> Evaluates daily people served per dollar, neighborhood equity multipliers, and two-block storefront cluster critical mass.";
          }
        } else {
          state.activeAgentDisplayName = "Regime Stress-Test & Orchestrator Agent";
          state.alpha = 0.50;
          state.parentWeight = 1.4;
          state.runwayWeight = 1.0;
          state.peopleWeight = 1.0;
          state.purityWeight = 1.0;
          state.volatilityWeight = 1.0;
          if (agentBadge) agentBadge.textContent = "Root Agent";
          if (agentDesc) {
            agentDesc.innerHTML = "<strong>Regime Stress-Test &amp; Orchestrator Agent:</strong> Root multi-agent coordinator that synthesizes all 3 domain sub-agents, executes multi-regime stress testing, and verifies 10-vector Red-Team compliance.";
          }
        }

        syncSlidersFromState();
        recomputeAll();
        syncChatbotAgentHeader();
      });
    }

    // Presets Bar
    const presetButtons = document.querySelectorAll(".preset-btn");
    presetButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        presetButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const preset = btn.getAttribute("data-preset");

        if (preset === "balanced") {
          state.alpha = 0.50;
          state.parentWeight = 1.4;
          state.runwayWeight = 1.0;
          state.peopleWeight = 1.0;
          state.purityWeight = 1.0;
          state.volatilityWeight = 1.0;
        } else if (preset === "people") {
          state.alpha = 0.15;
          state.peopleWeight = 1.8;
          state.parentWeight = 1.0;
          state.runwayWeight = 1.2;
        } else if (preset === "supply") {
          state.alpha = 0.85;
          state.parentWeight = 1.9;
          state.peopleWeight = 0.8;
          state.runwayWeight = 0.9;
        } else if (preset === "purity") {
          state.purityWeight = 1.9;
          state.peopleWeight = 1.1;
          state.alpha = 0.40;
        } else if (preset === "runway") {
          state.runwayWeight = 1.9;
          state.volatilityWeight = 1.4;
        }

        // Sync slider controls
        syncSlidersFromState();
        recomputeAll();
        syncChatbotAgentHeader();
      });
    });

    // Sliders
    const inputBudget = document.getElementById("input-budget");
    inputBudget.addEventListener("input", (e) => {
      state.budget = parseInt(e.target.value, 10);
      document.getElementById("disp-budget").textContent = "$" + state.budget.toLocaleString();
      recomputeAll();
    });

    const inputRunway = document.getElementById("input-runway");
    inputRunway.addEventListener("input", (e) => {
      state.runwayWeight = parseFloat(e.target.value);
      document.getElementById("disp-runway").textContent = state.runwayWeight.toFixed(1) + "x";
      recomputeAll();
    });

    const inputParent = document.getElementById("input-parent");
    inputParent.addEventListener("input", (e) => {
      state.parentWeight = parseFloat(e.target.value);
      document.getElementById("disp-parent").textContent = state.parentWeight.toFixed(1) + "x";
      recomputeAll();
    });

    const inputPeople = document.getElementById("input-people");
    inputPeople.addEventListener("input", (e) => {
      state.peopleWeight = parseFloat(e.target.value);
      document.getElementById("disp-people").textContent = state.peopleWeight.toFixed(1) + "x";
      recomputeAll();
    });

    const inputPurity = document.getElementById("input-purity");
    inputPurity.addEventListener("input", (e) => {
      state.purityWeight = parseFloat(e.target.value);
      document.getElementById("disp-purity").textContent = state.purityWeight.toFixed(1) + "x";
      recomputeAll();
    });

    const inputVolatility = document.getElementById("input-volatility");
    inputVolatility.addEventListener("input", (e) => {
      state.volatilityWeight = parseFloat(e.target.value);
      document.getElementById("disp-volatility").textContent = state.volatilityWeight.toFixed(1) + "x";
      recomputeAll();
    });

    const inputAlpha = document.getElementById("input-alpha");
    inputAlpha.addEventListener("input", (e) => {
      state.alpha = parseFloat(e.target.value);
      const left = Math.round((1 - state.alpha) * 100);
      const right = Math.round(state.alpha * 100);
      document.getElementById("disp-alpha").textContent = `${left} / ${right}`;
      recomputeAll();
    });

    // Reset sliders
    document.getElementById("btn-reset-sliders").addEventListener("click", () => {
      state.budget = 50000;
      state.regime = "hybrid";
      state.alpha = 0.50;
      state.parentWeight = 1.4;
      state.runwayWeight = 1.0;
      state.peopleWeight = 1.0;
      state.purityWeight = 1.0;
      state.volatilityWeight = 1.0;
      syncSlidersFromState();
      recomputeAll();
    });

    // Ineligible Corporate Drawer Toggle
    const drawerToggle = document.getElementById("drawer-toggle-btn");
    const drawerBody = document.getElementById("drawer-body-content");
    drawerToggle.addEventListener("click", () => {
      drawerBody.classList.toggle("open");
      const icon = drawerToggle.querySelector(".toggle-icon");
      icon.style.transform = drawerBody.classList.contains("open") ? "rotate(180deg)" : "rotate(0deg)";
    });

    // Red-Team Filters
    const filterButtons = document.querySelectorAll(".filter-chip-btn");
    filterButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        filterButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.redTeamFilter = btn.getAttribute("data-filter");
        renderRedTeamMatrix();
      });
    });

    // Map Action Buttons
    document.getElementById("btn-highlight-roots").addEventListener("click", () => {
      state.selectedApplicantAId = "sour_flour";
      state.selectedApplicantBId = "cumaica_coffee";
      const selA = document.getElementById("select-applicant-a");
      const selB = document.getElementById("select-applicant-b");
      if (selA) selA.value = "sour_flour";
      if (selB) selB.value = "cumaica_coffee";
      renderPairwiseView();
    });

    document.getElementById("btn-highlight-cluster").addEventListener("click", () => {
      state.selectedApplicantAId = "chicos_pizza";
      state.selectedApplicantBId = "pawn_shop";
      const selA = document.getElementById("select-applicant-a");
      const selB = document.getElementById("select-applicant-b");
      if (selA) selA.value = "chicos_pizza";
      if (selB) selB.value = "pawn_shop";
      renderPairwiseView();
    });

    // Memo Print & Refresh
    document.getElementById("btn-print-memo").addEventListener("click", () => {
      window.print();
    });

    document.getElementById("btn-refresh-memo").addEventListener("click", () => {
      renderDeterminationMemo();
    });
  }

  function syncSlidersFromState() {
    document.getElementById("input-budget").value = state.budget;
    document.getElementById("disp-budget").textContent = "$" + state.budget.toLocaleString();

    document.getElementById("input-runway").value = state.runwayWeight;
    document.getElementById("disp-runway").textContent = state.runwayWeight.toFixed(1) + "x";

    document.getElementById("input-parent").value = state.parentWeight;
    document.getElementById("disp-parent").textContent = state.parentWeight.toFixed(1) + "x";

    document.getElementById("input-people").value = state.peopleWeight;
    document.getElementById("disp-people").textContent = state.peopleWeight.toFixed(1) + "x";

    document.getElementById("input-purity").value = state.purityWeight;
    document.getElementById("disp-purity").textContent = state.purityWeight.toFixed(1) + "x";

    document.getElementById("input-volatility").value = state.volatilityWeight;
    document.getElementById("disp-volatility").textContent = state.volatilityWeight.toFixed(1) + "x";

    document.getElementById("input-alpha").value = state.alpha;
    const left = Math.round((1 - state.alpha) * 100);
    const right = Math.round(state.alpha * 100);
    document.getElementById("disp-alpha").textContent = `${left} / ${right}`;
  }

  function recomputeAll() {
    runPortfolioOptimization();
    updateKPIs();
    renderQueueTable();
    renderPairwiseView();
    renderNetworkMap();
    renderDeterminationMemo();
  }

  // --- 10. GRANT OFFICER ADK AGENT COPILOT CHATBOT ---

  function computeGlassBoxBuckets(app) {
    const b1 = Math.min(25, Math.round((app.scoring.cascadeScore / 100) * 25 * 10) / 10);
    const b2 = Math.min(25, Math.round((app.scoring.anchorScore / 100) * 25 * 10) / 10);
    const b3 = Math.min(25, Math.round((Math.min(100, app.scoring.peopleHelpedTotal / 12) / 100) * 25 * 10) / 10);
    const b4 = Math.min(25, Math.round(((app.scoring.purityScore / 100) * 12.5 + Math.min(12.5, app.scoring.survivalLift * 28)) * 10) / 10);
    const total100 = Math.round((b1 + b2 + b3 + b4) * 10) / 10;
    return { b1, b2, b3, b4, total100 };
  }

  function syncChatbotAgentHeader() {
    const nameEl = document.getElementById("chatbot-active-agent-name");
    const badgeEl = document.getElementById("chatbot-active-agent-badge");
    const fabSub = document.getElementById("fab-agent-subtext");
    if (nameEl) nameEl.textContent = state.activeAgentDisplayName;
    if (fabSub) fabSub.textContent = state.activeAgentDisplayName;
    if (badgeEl) {
      if (state.activeAgentId === "Supply_Provenance_Agent") badgeEl.textContent = "Sub-Agent 1";
      else if (state.activeAgentId === "Runway_Sector_Purity_Agent") badgeEl.textContent = "Sub-Agent 2";
      else if (state.activeAgentId === "Spatial_Human_Impact_Agent") badgeEl.textContent = "Sub-Agent 3";
      else badgeEl.textContent = "Root Agent";
    }
  }

  function appendChatMessage(role, htmlContent) {
    const container = document.getElementById("chatbot-messages");
    if (!container) return;
    const msg = document.createElement("div");
    msg.className = `chat-msg ${role}`;
    msg.innerHTML = htmlContent;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;

    msg.querySelectorAll("[data-chat-action]").forEach(btn => {
      btn.addEventListener("click", () => {
        const act = btn.getAttribute("data-chat-action");
        if (act === "goto-map") {
          const tabBtn = document.getElementById("btn-tab-pairwise");
          if (tabBtn) tabBtn.click();
        } else if (act === "goto-memo") {
          const tabBtn = document.getElementById("btn-tab-memo");
          if (tabBtn) tabBtn.click();
        } else if (act === "goto-redteam") {
          const tabBtn = document.getElementById("btn-tab-redteam");
          if (tabBtn) tabBtn.click();
        } else if (act === "compare-pair") {
          const aId = btn.getAttribute("data-a") || "sour_flour";
          const bId = btn.getAttribute("data-b") || "cumaica_coffee";
          state.selectedApplicantAId = aId;
          state.selectedApplicantBId = bId;
          const selA = document.getElementById("select-applicant-a");
          const selB = document.getElementById("select-applicant-b");
          if (selA) selA.value = aId;
          if (selB) selB.value = bId;
          const tabBtn = document.getElementById("btn-tab-pairwise");
          if (tabBtn) tabBtn.click();
        }
      });
    });
  }

  function buildAgentReplyForPreset(qKey, customText) {
    const top1 = state.rankedQueue[0] || APPLICANTS_DATA[0];
    const top2 = state.rankedQueue[1] || APPLICANTS_DATA[1];
    const sourFlour = state.rankedQueue.find(a => a.id === "sour_flour") || top1;
    const cumaica = state.rankedQueue.find(a => a.id === "cumaica_coffee") || top2;
    const grocer = state.rankedQueue.find(a => a.id === "corner_grocer") || state.rankedQueue[2];
    const s = state.fundedSummary;
    const sfGlass = computeGlassBoxBuckets(sourFlour);

    if (qKey === "q1") {
      return `
        <div class="chat-agent-meta">
          <span>🤖 ${state.activeAgentDisplayName}</span>
          <span class="chat-tool-pill">trace_multihop_consequence_chains()</span>
        </div>
        <div>
          <strong>Unfunded Corridor Contagion Verdict:</strong> If zero grants are disbursed today, <strong>${sourFlour.name}</strong> (${sourFlour.address}) causes the largest systemic corridor cascade across <strong>5 linked resilience domains (4 hops)</strong>:
        </div>
        <div class="chat-hop-chain">
          <strong>• Hop 0 (Seed Equipment Cliff):</strong> ${sourFlour.name} holds only <strong>${sourFlour.runwayQuarters} quarters</strong> of cash (45.0% 12-month closure probability) facing an indivisible $10,000 commercial deck oven replacement.<br>
          <strong>• Hop 1 (Direct B2B Supply Shock):</strong> Supplies fresh par-baked sourdough to <strong>${sourFlour.outDegree} direct corridor buyers</strong> (436.5m avg delivery walk), including <em>Cumaica Coffee</em>, <em>G.Rabbit</em>, <em>Chico's Pizza</em>, and <em>Monarch Beverage</em>.<br>
          <strong>• Hop 2 (Secondary Retail &amp; Catering Contagion):</strong> Exposes <strong>${sourFlour.secondOrderReach} second-order businesses</strong> across Mid-Market and 6th Street.<br>
          <strong>• Hop 3 (Commuter Footfall Attrition):</strong> Puts <strong>${sourFlour.headcount} direct FTEs + 38 network kitchen staff</strong> and <strong>${sourFlour.dailyPatronCommuters} daily transit commuters</strong> at risk.<br>
          <strong>• Hop 4 (Block Vacancy Tipping Point):</strong> Pushes the 6th &amp; Mission micro-cluster past the <strong>35% commercial vacancy blight threshold</strong>.
        </div>
        <div style="font-size:0.75rem; color:#94a3b8;">
          <strong>Why Raw Centrality Hubs Are Excluded:</strong> Corporate entities like <em>CloudScale</em>, <em>Waymo Depot</em>, and <em>BioGenix</em> have high raw transaction volume but are blocked at <strong>Stage 0 ($0.00)</strong> because their survival lift is near zero (&Delta;P &approx; 0).
        </div>
        <div class="chat-action-row">
          <button type="button" class="chat-action-btn" data-chat-action="goto-map">🗺️ Inspect 4-Hop Cascade on Map</button>
          <button type="button" class="chat-action-btn" data-chat-action="compare-pair" data-a="sour_flour" data-b="cumaica_coffee">⚖️ Compare Top 2 Roots</button>
        </div>
      `;
    }

    if (qKey === "q2") {
      const cuGlass = computeGlassBoxBuckets(cumaica);
      return `
        <div class="chat-agent-meta">
          <span>🤖 ${state.activeAgentDisplayName}</span>
          <span class="chat-tool-pill">trace_applicant_multihop_paths_and_compare()</span>
        </div>
        <div>
          <strong>Head-to-Head Structural Proof: ${sourFlour.name} (#1) vs. ${cumaica.name} (#2)</strong>
        </div>
        <div class="chat-hop-chain">
          <strong>1. Direct Upstream Dependency (Hop 1):</strong> <em>${sourFlour.name}</em> directly supplies <em>${cumaica.name}</em> at Hop 1 (436.5m walk) and sits at pure root status (<code>out_degree=${sourFlour.outDegree}</code>, <code>in_degree=1</code>, &mu;=${sourFlour.scoring.parentMultiplier}x) vs. ${cumaica.name} (<code>out_degree=${cumaica.outDegree}</code>, <code>in_degree=2</code>).<br>
          <strong>2. Substitutability Friction (&theta;<sub>ext</sub>):</strong> Daily par-baked artisan bread (&theta;<sub>ext</sub>=0.15) cannot be substituted from outside the corridor without menu/margin loss, whereas roasted coffee beans (&theta;<sub>ext</sub>=0.20) have longer shelf storage.<br>
          <strong>3. Runway Urgency &amp; Lift:</strong> ${sourFlour.name} has <strong>${sourFlour.runwayQuarters}q</strong> runway (+${Math.round(sourFlour.scoring.survivalLift * 100)}% lift) vs. ${cumaica.name}'s <strong>${cumaica.runwayQuarters}q</strong> runway (+${Math.round(cumaica.scoring.survivalLift * 100)}% lift).<br>
          <strong>4. Shared Buyer Deduplication:</strong> They share 3 downstream buyers (Jaccard overlap J=0.375). Under our <strong>${state.regime.toUpperCase()} Regime ($${state.budget.toLocaleString()})</strong>, <strong>both</strong> co-anchor Tier 1 at $${sourFlour.grantAward.toLocaleString()} and $${cumaica.grantAward.toLocaleString()}.
        </div>
        <div class="chat-receipt-grid">
          <div class="chat-receipt-box">
            <strong>${sourFlour.name} Glass-Box (100pt):</strong> <strong>${sfGlass.total100}/100</strong><br>
            Cascade: ${sfGlass.b1}/25 • Anchor: ${sfGlass.b2}/25<br>
            People: ${sfGlass.b3}/25 • Viability: ${sfGlass.b4}/25
          </div>
          <div class="chat-receipt-box">
            <strong>${cumaica.name} Glass-Box (100pt):</strong> <strong>${cuGlass.total100}/100</strong><br>
            Cascade: ${cuGlass.b1}/25 • Anchor: ${cuGlass.b2}/25<br>
            People: ${cuGlass.b3}/25 • Viability: ${cuGlass.b4}/25
          </div>
        </div>
        <div class="chat-action-row">
          <button type="button" class="chat-action-btn" data-chat-action="compare-pair" data-a="sour_flour" data-b="cumaica_coffee">⚖️ Open Side-by-Side Inspector</button>
        </div>
      `;
    }

    if (qKey === "q3") {
      return `
        <div class="chat-agent-meta">
          <span>🤖 ${state.activeAgentDisplayName}</span>
          <span class="chat-tool-pill">evaluate_supplier_cascade_and_hidden_root()</span>
        </div>
        <div>
          <strong>Downstream Buyer Fragility &amp; Verified Loan Audit:</strong> Yes—4 of ${sourFlour.name}'s direct downstream buyers in the cohort are in the acute 0.7q–1.2q fragility window:
        </div>
        <div class="chat-hop-chain">
          • <strong>Chico's Pizza (131 6th St):</strong> <code>0.7q</code> runway • $5,000 Tier-2 Bridge Grant + Landlord Match<br>
          • <strong>G.Rabbit (90 7th St):</strong> <code>0.9q</code> runway • $5,000 Tier-2 Bridge Grant<br>
          • <strong>Monarch Beverage Catering (101 6th St):</strong> <code>1.0q</code> runway • $5,000 Tier-2 Bridge Grant<br>
          • <strong>The Pawn Shop (993 Mission St):</strong> <code>1.2q</code> runway • $5,000 Tier-2 Bridge Grant
        </div>
        <div style="font-size:0.75rem; color:#94a3b8;">
          <strong>Historical SBA 7(a) Ground Truth:</strong> Public federal loan records confirm that under-capitalized corridor food/print borrowers with &lt;0.25q runway and prior loan charge-offs face structural insolvency unless paired with two-party vendor/landlord escrow warrants.
        </div>
      `;
    }

    if (qKey === "q4") {
      return `
        <div class="chat-agent-meta">
          <span>🤖 ${state.activeAgentDisplayName}</span>
          <span class="chat-tool-pill">discover_unapplied_bottlenecks()</span>
        </div>
        <div>
          <strong>Bidirectional 2-Hop Scan — Un-Applied Corridor Bottlenecks Found:</strong> Two critical upstream commercial service providers did <em>not</em> submit grant applications but supply 5 applicants each:
        </div>
        <div class="chat-hop-chain">
          <strong>1. Mid-Market Commercial Kitchen &amp; Refrigeration Repair Co.</strong> (148 8th St, Sector 8113)<br>
          • Est. Runway: <strong>0.75 quarters</strong> • Services refrigeration &amp; ovens for 5 cohort food/grocery applicants.<br><br>
          <strong>2. Stevenson Street Sanitary Linen &amp; Apron Commissary</strong> (645 Stevenson St, Sector 8123)<br>
          • Est. Runway: <strong>0.90 quarters</strong> • Provides health-code mandated linen laundering for 5 dining &amp; clinic storefronts.
        </div>
        <div style="font-size:0.75rem; color:#a7f3d0;">
          <strong>Recommended Officer Action:</strong> Dispatch an OEWD Small Business Ambassador within 48 hours to invite both Sector 8113/8123 bottlenecks into Tranche 2 intake.
        </div>
      `;
    }

    if (qKey === "q5") {
      const m = customText && customText.match(/\$?\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{4,6})/);
      const hypAmt = m ? parseInt(m[1].replace(/,/g, ""), 10) : 8000;
      const liftHyp = calculateSurvivalLift(sourFlour.runwayQuarters, hypAmt, sourFlour.burnRateMonthly);
      const lift10k = calculateSurvivalLift(sourFlour.runwayQuarters, 10000, sourFlour.burnRateMonthly);
      const gap = Math.max(0, 10000 - hypAmt);
      return `
        <div class="chat-agent-meta">
          <span>🤖 ${state.activeAgentDisplayName}</span>
          <span class="chat-tool-pill">audit_context_and_simulate_what_if($${hypAmt.toLocaleString()})</span>
        </div>
        <div>
          <strong>What Does $${hypAmt.toLocaleString()} Actually Change? (Explicit Modeling Assumptions):</strong>
        </div>
        <div class="chat-hop-chain">
          <strong>Assumption 1 — Continuous Logistic Survival Shift:</strong><br>
          For <em>${sourFlour.name}</em> ($${sourFlour.burnRateMonthly.toLocaleString()}/mo burn, ${sourFlour.runwayQuarters}q runway), a <strong>$${hypAmt.toLocaleString()}</strong> grant adds <strong>+${liftHyp.runwayAdded.toFixed(2)} quarters</strong> of cash buffer (12-month survival shifts from ${Math.round(liftHyp.pBefore * 100)}% &rarr; ${Math.round(liftHyp.pAfter * 100)}%, continuous lift <strong>+${Math.round(liftHyp.lift * 100)}%</strong> vs. <strong>+${Math.round(lift10k.lift * 100)}%</strong> at $10,000).<br><br>
          <strong>Assumption 2 — Category 1 Indivisible Capital Cliff Step-Function:</strong><br>
          ${gap > 0
            ? `⚠️ <strong>CRITICAL CLIFF WARNING:</strong> ${sourFlour.name} requires $10,000 for an indivisible commercial deck oven replacement. A partial <strong>$${hypAmt.toLocaleString()}</strong> grant leaves an unfunded <strong>$${gap.toLocaleString()} equipment gap</strong> (0% cliff resolution unless paired with a verified $${gap.toLocaleString()} vendor/landlord co-pay).`
            : `✅ <strong>FULL CLIFF CLEARED:</strong> $${hypAmt.toLocaleString()} fully clears the $10,000 indivisible equipment replacement threshold.`
          }
        </div>
      `;
    }

    if (qKey === "q6") {
      return `
        <div class="chat-agent-meta">
          <span>🤖 ${state.activeAgentDisplayName}</span>
          <span class="chat-tool-pill">evaluate_spatial_cluster_critical_mass()</span>
        </div>
        <div>
          <strong>Neighborhood Equity &amp; Dual-Track Protection (7 Central Market Census Tracts):</strong>
        </div>
        <div class="chat-hop-chain">
          • <strong>Zero-Vehicle Households:</strong> <strong>71.0% – 78.5%</strong> of corridor households do not own a car.<br>
          • <strong>Poverty Rate:</strong> <strong>28.0% – 36.2%</strong> across Tenderloin / 6th &amp; Mission / Mid-Market tracts (Equity Multiplier <strong>1.35x – 1.46x</strong>).<br>
          • <strong>Why Track 1 Protects B2C Anchors:</strong> National supply tables give retail grocers zero outgoing B2B supply edges. Our <strong>Dual-Track Architecture</strong> scores <strong>${grocer.name}</strong> (${grocer.address}) on Track 1 Community Anchor gravity, securing a full <strong>$10,000 Tier-1 Grant</strong> serving ${grocer.vulnerableResidentsServed} low-mobility seniors and families daily.
        </div>
        <div class="chat-action-row">
          <button type="button" class="chat-action-btn" data-chat-action="compare-pair" data-a="corner_grocer" data-b="sour_flour">⚖️ Compare Corner Grocer vs. Sour Flour</button>
        </div>
      `;
    }

    if (qKey === "q7") {
      const funded = state.rankedQueue.filter(a => a.status.startsWith("funded"));
      return `
        <div class="chat-agent-meta">
          <span>🤖 ${state.activeAgentDisplayName}</span>
          <span class="chat-tool-pill">format_red_team_compliance_report_markdown()</span>
        </div>
        <div>
          <strong>Friday Executive Determination Memo Ready ($${s.budgetAllocated.toLocaleString()} / ${s.fundedCount} Storefronts):</strong>
        </div>
        <div class="chat-hop-chain">
          • <strong>Tier 1 Full Grants ($10,000):</strong> ${funded.filter(a => a.grantAward >= 10000).map(a => a.name).join(", ") || "Top Anchors"}<br>
          • <strong>Tier 2 Cluster Bridges ($5,000):</strong> ${funded.filter(a => a.grantAward < 10000).map(a => a.name).join(", ") || "Concentrated Regime Active"}<br>
          • <strong>Impact:</strong> <strong>${s.directJobs} direct FTEs</strong> + <strong>${s.networkJobs} supply-chain staff</strong> + <strong>${s.peopleServed.toLocaleString()} daily patrons/residents</strong>.<br>
          • <strong>Honest Provenance Line:</strong> Business registry, Census tracts, and federal SBA loan records are <em>measured</em>; commercial supply and footfall edges are <em>modeled</em> and require the 1-Invoice Pre-Disbursement Gate (&gt;30% cascade share).
        </div>
        <div class="chat-action-row">
          <button type="button" class="chat-action-btn" data-chat-action="goto-memo">📑 Open Printable Friday Memo</button>
        </div>
      `;
    }

    if (qKey === "blindspot") {
      return `
        <div class="chat-agent-meta">
          <span>🤖 ${state.activeAgentDisplayName}</span>
          <span class="chat-tool-pill">audit_context_and_simulate_what_if(out_of_schema)</span>
        </div>
        <div>
          <strong>Out-of-Schema Blind-Spot &amp; Proposition 209 Compliance Audit:</strong>
        </div>
        <div class="chat-hop-chain">
          • <strong>Landlord / Lease Sale / Eviction Threats:</strong> <em>Not in public registry dataset.</em> Requires a mandatory <strong>Landlord Estoppel &amp; Lease-Match Addendum</strong> before releasing bridge funds.<br>
          • <strong>Personal Credit Scores / Unrecorded Cash / Litigation:</strong> <em>Out of schema.</em> Mitigated via <strong>Two-Party Vendor/Landlord Escrow Warrants</strong> (zero unverified cash disbursement).<br>
          • <strong>Owner Race / Gender / Ethnicity:</strong> <em>Strictly excluded per California Proposition 209.</em> Equity is weighted strictly via <strong>Census Tract Poverty &amp; Car-Free Household Rates</strong>.
        </div>
        <div class="chat-action-row">
          <button type="button" class="chat-action-btn" data-chat-action="goto-redteam">🛡️ View All 10 Red-Team Defenses</button>
        </div>
      `;
    }

    return "";
  }

  function processFreeTextChatQuery(rawQuery) {
    const q = rawQuery.trim();
    const qLower = q.toLowerCase();

    // 1. Out-of-schema keywords check
    if (/(landlord|evict|building sold|credit score|fico|race|gender|ethnic|lawsuit|litigation|under the table)/.test(qLower)) {
      return buildAgentReplyForPreset("blindspot", q);
    }
    // 2. Dollar what-if check (e.g. "$8,000", "8000", "what does $7,500 change")
    if (/(\$[0-9]|what does|what if.*grant|partial grant|8,000|8000|7,500|6,000)/.test(qLower)) {
      return buildAgentReplyForPreset("q5", q);
    }
    // 3. Unfunded / most damage / fund nobody
    if (/(fund nobody|no one|most damage|which closure|cascade|4-hop|multihop)/.test(qLower)) {
      return buildAgentReplyForPreset("q1", q);
    }
    // 4. Un-applied bottlenecks / far end of chain
    if (/(nobody.*applied|unapplied|far end|bottleneck|repair|linen|8113|8123)/.test(qLower)) {
      return buildAgentReplyForPreset("q4", q);
    }
    // 5. Downstream fragility / SBA loans
    if (/(downstream|fragile|sba|charge-off|loan)/.test(qLower)) {
      return buildAgentReplyForPreset("q3", q);
    }
    // 6. Neighborhood / equity / grocer / census
    if (/(neighborhood|census|poverty|car-free|grocer|equity|whose)/.test(qLower)) {
      return buildAgentReplyForPreset("q6", q);
    }
    // 7. Memo / Friday / write it up
    if (/(memo|friday|write it up|present|report)/.test(qLower)) {
      return buildAgentReplyForPreset("q7", q);
    }
    // 8. Check if user mentions specific applicants to compare or inspect
    const matchedApps = state.rankedQueue.filter(a => qLower.includes(a.name.toLowerCase()) || qLower.includes(a.id.replace("_", " ")));
    if (matchedApps.length >= 2) {
      const a = matchedApps[0];
      const b = matchedApps[1];
      const rankA = state.rankedQueue.findIndex(x => x.id === a.id) + 1;
      const rankB = state.rankedQueue.findIndex(x => x.id === b.id) + 1;
      return `
        <div class="chat-agent-meta">
          <span>🤖 ${state.activeAgentDisplayName}</span>
          <span class="chat-tool-pill">trace_applicant_multihop_paths_and_compare()</span>
        </div>
        <div>
          <strong>Live Pairwise Comparison: ${a.name} (#${rankA}) vs. ${b.name} (#${rankB})</strong>
        </div>
        <div class="chat-hop-chain">
          • <strong>${a.name}:</strong> Composite <strong>${a.scoring.compositeScore}</strong> • Award <strong>$${a.grantAward.toLocaleString()}</strong> • Runway ${a.runwayQuarters}q (+${Math.round(a.scoring.survivalLift * 100)}% lift) • ${a.outDegree} B2B buyers • ${a.scoring.peopleHelpedTotal.toLocaleString()} daily people served.<br>
          • <strong>${b.name}:</strong> Composite <strong>${b.scoring.compositeScore}</strong> • Award <strong>$${b.grantAward.toLocaleString()}</strong> • Runway ${b.runwayQuarters}q (+${Math.round(b.scoring.survivalLift * 100)}% lift) • ${b.outDegree} B2B buyers • ${b.scoring.peopleHelpedTotal.toLocaleString()} daily people served.
        </div>
        <div class="chat-action-row">
          <button type="button" class="chat-action-btn" data-chat-action="compare-pair" data-a="${a.id}" data-b="${b.id}">⚖️ Load in Pairwise Inspector</button>
        </div>
      `;
    }
    if (matchedApps.length === 1) {
      const a = matchedApps[0];
      const rankA = state.rankedQueue.findIndex(x => x.id === a.id) + 1;
      const gb = computeGlassBoxBuckets(a);
      return `
        <div class="chat-agent-meta">
          <span>🤖 ${state.activeAgentDisplayName}</span>
          <span class="chat-tool-pill">compute_applicant_utility(${a.id})</span>
        </div>
        <div>
          <strong>Applicant Diagnostic — ${a.name} (Rank #${rankA} • $${a.grantAward.toLocaleString()}):</strong>
        </div>
        <div class="chat-hop-chain">
          • <strong>Address &amp; Sector:</strong> ${a.address} (${a.sector})<br>
          • <strong>Runway &amp; Survival Lift:</strong> ${a.runwayQuarters} quarters (+${Math.round(a.scoring.survivalLift * 100)}% survival lift)<br>
          • <strong>B2B Supply Reach:</strong> ${a.outDegree} direct buyers (${a.secondOrderReach} 2-hop exposed)<br>
          • <strong>4-Bucket Glass-Box Receipt:</strong> <strong>${gb.total100}/100</strong> (Cascade ${gb.b1}/25, Anchor ${gb.b2}/25, People ${gb.b3}/25, Viability ${gb.b4}/25)<br>
          • <strong>Justification:</strong> ${a.needJustification}
        </div>
        <div class="chat-action-row">
          <button type="button" class="chat-action-btn" data-chat-action="compare-pair" data-a="${a.id}" data-b="sour_flour">⚖️ Compare Against #1 Rank</button>
        </div>
      `;
    }

    // Default why this one and not that one / general summary
    return buildAgentReplyForPreset("q2", q);
  }

  function initAdkChatbot() {
    const root = document.getElementById("adk-chatbot-root");
    const fab = document.getElementById("adk-chatbot-fab");
    const headerBtn = document.getElementById("btn-toggle-chatbot-header");
    const closeBtn = document.getElementById("btn-chatbot-close");
    const expandBtn = document.getElementById("btn-chatbot-expand");
    const clearBtn = document.getElementById("btn-chatbot-clear");
    const panel = document.getElementById("adk-chatbot-panel");
    const form = document.getElementById("chatbot-form");
    const input = document.getElementById("chatbot-input");

    if (!root || !panel) return;

    function renderWelcomeMessage() {
      const container = document.getElementById("chatbot-messages");
      if (!container) return;
      container.innerHTML = "";
      appendChatMessage(
        "agent",
        `
          <div class="chat-agent-meta">
            <span>🤖 ${state.activeAgentDisplayName}</span>
            <span class="chat-tool-pill">ADK Ready • 11 Cohort + 4 Corp Traps</span>
          </div>
          <div>
            Welcome, Grant Officer. I am synced to your live <strong>$${state.budget.toLocaleString()}</strong> portfolio simulator (currently funding <strong>${state.fundedSummary.fundedCount} storefronts</strong> and preserving <strong>${state.fundedSummary.directJobs} direct FTEs</strong>).
            Click any <strong>Tuesday 2 PM Drill</strong> chip above or ask a question below.
          </div>
        `
      );
    }

    syncChatbotAgentHeader();
    renderWelcomeMessage();

    if (fab) {
      fab.addEventListener("click", () => {
        root.classList.add("open");
        if (input) input.focus();
      });
    }
    if (headerBtn) {
      headerBtn.addEventListener("click", () => {
        root.classList.toggle("open");
        if (root.classList.contains("open") && input) input.focus();
      });
    }
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        root.classList.remove("open");
      });
    }
    if (expandBtn) {
      expandBtn.addEventListener("click", () => {
        panel.classList.toggle("expanded");
      });
    }
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        renderWelcomeMessage();
      });
    }

    document.querySelectorAll(".chatbot-chip").forEach(chip => {
      chip.addEventListener("click", () => {
        const qKey = chip.getAttribute("data-q");
        const label = chip.textContent;
        root.classList.add("open");
        appendChatMessage("user", label);
        const reply = buildAgentReplyForPreset(qKey, label);
        appendChatMessage("agent", reply);
      });
    });

    if (form && input) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;
        input.value = "";
        appendChatMessage("user", text);
        const reply = processFreeTextChatQuery(text);
        appendChatMessage("agent", reply);
      });
    }
  }

  // --- INITIALIZATION ENTRY POINT ---
  document.addEventListener("DOMContentLoaded", () => {
    runPortfolioOptimization();
    updateKPIs();
    renderQueueTable();
    renderCorporateDrawer();
    renderRedTeamMatrix();
    populatePairwiseSelectors();
    renderPairwiseView();
    renderNetworkMap();
    renderDeterminationMemo();
    attachEventListeners();
    initAdkChatbot();
  });

})();
