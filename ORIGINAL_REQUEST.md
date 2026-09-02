# Original User Request

## 2026-09-01T19:14:45Z

Comprehensive system design, large-scale relational world-building architecture, closed economic costing model, effective-dated multi-year transition engine (FY 2025 baseline -> FY 2026 evolution), and formal verification rulebook for **Souss Agri-Pack SARL** (a realistic, deeply interconnected Moroccan agricultural packaging SME simulation based on LF 2023-2025, CGI, CNSS, BAM, ADII, and Plan Comptable Marocain accounting standards).

Working directory: `C:\Users\Salaheddine\.gemini\antigravity\scratch\souss_agripack_sim`
Integrity mode: development

---

## 1. Project Boundaries, Non-Goals & Primary Source Rule

- **Primary Source Priority Rule**: All tax rates, thresholds, and parameters stated in this prompt represent baseline engineering hypotheses. The implementing agents must verify every parameter against authoritative Moroccan primary legal texts (CGI 2025/2026, Loi de Finances 2023/2024/2025, Décret SMIG, BAM official bulletins, ADII Customs Tariff). **In any conflict, the verified primary legal source takes absolute precedence over this prompt.** Every parameter in `config/parameters.yaml` must carry an authoritative article citation and as-of date; use `[TO VERIFY]` for any unconfirmed value.
- **Scope Boundary (Phase 1 vs Phase 2)**: Phase 1 is **strictly a design, specification, schema, and verification rulebook delivery**. Phase 1 does NOT generate row-level synthetic transaction datasets or build UI dashboards (these belong exclusively to Phase 2). The only executable code in Phase 1 is the validation script `scripts/verify_specs.py`.
- **Fictional-Yet-Format-Valid Identifiers**: All company, client, supplier, bank, and employee identifiers (ICE, IF, RC, TP, CNSS, RIB, CIN) are **fictional but structurally format-valid** (e.g., 15-digit ICE format, valid RIB 24-digit structure and checksum modulo 97). Do not alter designated simulation keys.
- **Language Conventions**: English for system architecture, schemas, and specifications; French for Moroccan accounting terms, legal mentions, PCM account titles, and official tax/social vocabulary.
- **Legal Accuracy on SARL Governance**: M. Youssef Bennani (60% majority shareholder) is the statutory Managing Director (*Gérant associé majoritaire*). Gérant liability is limited for ordinary corporate risks, but **joint and personal liability** (*responsabilité solidaire et personnelle*) applies specifically for fiscal fraud/infractions (CGI Art. 182), non-remittance of employee social contributions (CNSS Dahir 1972), and gross management negligence leading to insolvency (*action en comblement de passif*, Code de Commerce Law 15-95).

---

## 2. Deliverables & Output Manifest

All deliverables must be written to `C:\Users\Salaheddine\.gemini\antigravity\scratch\souss_agripack_sim/` with the following explicit structure:

```
souss_agripack_sim/
├── docs/
│   ├── 01_world_architecture.md            # Complete multi-tiered world graph, actors, governance & BOM specs
│   ├── 02_regulatory_engines.md            # Tax, Social, Customs, Banking, and Law 69-21 math models
│   ├── 03_event_catalog.md                 # Human-readable rendering of the numbered business event catalog
│   ├── 04_pcm_journal_matrix.md            # Human-readable rendering of zero-fault PCM double-entry templates
│   ├── 05_state_machines.md                # Lifecycle workflows for all 6 business operational cycles
│   └── 06_verification_rulebook.md         # Invariant algebra, audit tests & Phase 2 acceptance contract
├── schemas/
│   ├── entities.json                       # JSON Schema for all entity types (clients, suppliers, banks)
│   ├── events.json                         # JSON Schema for all transactional event payloads
│   ├── journal_entries.json                # JSON Schema for double-entry PCM journal records
│   └── schema.sql                          # Canonical PostgreSQL DDL (with best-effort SQLite compatibility)
├── config/
│   ├── business_plan.yaml                  # Revenue target, P&L envelope, capacity, pricing & BOM costing
│   ├── payroll_grid.yaml                   # Headcount (22 perm + 5 seasonal), job roles, gross wages & CNSS
│   ├── parameters.yaml                     # Effective-dated parameter table with legal article citations
│   ├── chart_of_accounts.yaml              # Authoritative Moroccan PCM chart of accounts (4-8 digits)
│   ├── events.yaml                         # Machine-readable numbered transaction & event definitions
│   ├── journal_templates.yaml              # Machine-readable double-entry PCM debit/credit journal templates
│   ├── fixed_assets_depreciation.yaml      # Asset register, acquisition dates, lifespan, linear depreciation
│   ├── inventory_policies.yaml             # CUMP valuation method, BOM per m2, scrap/waste rates
│   ├── opening_balance_sheet.yaml          # Balanced 01/01/2025 accounts (with vintage-split retained earnings)
│   └── risk_events_probabilities.yaml      # Probabilistic tables with deterministic pseudo-random seeds
└── scripts/
    └── verify_specs.py                     # Standalone Python verification script checking all schemas & math
```

---

## 3. Requirements

### R1. Large-Scale Multi-Tiered World Graph, Economic Model & Closed Costing Chain
Formalize the relational graph, physical production models, closed economic model, and data schemas:

1. **Core Enterprise & Governance**:
   - Souss Agri-Pack SARL (Zone Industrielle Ait Melloul, Agadir; ICE `002345678000091`, IF `45127890`, RC `28451`, TP `30145280`, CNSS `9127456`, Capital 800,000 MAD).
   - Shareholders: M. Youssef Bennani (60%, Gérant associé majoritaire), Mme Fatima Zahra Amri (25%, DAF / Associée), M. Hassan Oulhaj (15%, Directeur Commercial / Associé).

2. **Closed Costing Chain & Product Pricing (`config/business_plan.yaml`)**:
   - **Bill of Materials (BOM) & Material Cost**:
     - Single-wall corrugated board consumption: 150 g/m2 outer kraftliner + 120 g/m2 fluting (take-up factor 1.48) + 150 g/m2 inner testliner = 477 g/m2 paper consumed.
     - Blended paper cost: ~6.20 MAD/kg -> Paper cost = 2.957 MAD/m2.
     - Auxiliaries (industrial starch glue ~25 g/m2 dry, flexo inks, stitching wire, packaging) = ~0.150 MAD/m2.
     - Technical scrap/waste rate = 8.0%.
     - **Direct Material Cost ($C_{\text{mat}}$)**: Round((2.957 + 0.150) / (1 - 0.08), 3) = **3.377 MAD/m2** (or ~3.10 MAD/m2 net).
   - **Product Catalog & Pricing**:
     - Weighted average selling price = **5.753 MAD/m2** (~1.85x direct material cost).
     - Product SKUs (P001 Citrus 10kg, P002 Heavy Tomato box, P003 Premium Avocado tray, P004 Berry punnet, P005 Custom industrial packaging) priced proportionally to board surface and conversion complexity.
   - **Production Volume, Capacity & Turnover**:
     - Annual Production Volume: **1,900,000 m2/year**.
     - FY 2025 Target Turnover (CA): $1,900,000 \times 5.753 = \mathbf{10,930,700\text{ MAD HT}}$ (falls within the 10M-50M MAD Law 69-21 tier).
     - Converting Plant Capacity: **2,400,000 m2/year** -> Nominal Load Factor: **79.2%**.
     - FY 2026 Growth Projection: Volume +4% (1,976,000 m2), Price +2% (5.868 MAD/m2) -> CA ~11,595,000 MAD HT.

3. **Target P&L Skeleton & Guaranteed Fiscal Activation (`config/business_plan.yaml`)**:
   - **P&L Envelope (FY 2025)**:
     - Chiffre d'Affaires (Turnover HT): 10,930,700 MAD.
     - Consommation Matières Premières & Fournitures: ~5,900,000 MAD (54.0% of CA).
     - Charges de Personnel (Gross Wages + CNSS + AT): ~2,580,000 MAD (23.6% of CA).
     - Énergie & Fluides (ONEE Electricity MV + Water + Diesel): ~480,000 MAD (4.4% of CA).
     - Autres Charges Externes (Transport, Entretien, Assurances, Honoraires, Télécom): ~850,000 MAD.
     - Dotations aux Amortissements (DDA): ~380,000 MAD.
     - Charges Financières (Agios d'escompte, intérêts découverts/emprunts): ~245,000 MAD.
     - **Résultat Courant Avant Impôt (Pre-tax Accounting Profit)**: $\approx \mathbf{495,700\text{ MAD}}$.
     - Réintégrations Fiscales (amendes, cadeaux > 100 MAD, provisions non déductibles, pénalités): $\approx +34,300\text{ MAD}$.
     - **Résultat Fiscal (Taxable Profit)**: $\approx \mathbf{530,000\text{ MAD}}$.
     - **IS Dû (Progressive Barème 2025)**:
       - Tranche 1 (0 to 300,000 MAD at 17.50%): 52,500 MAD.
       - Tranche 2 (300,001 to 530,000 MAD = 230,000 MAD at 20.00%): 46,000 MAD.
       - **Total IS = 98,500 MAD**.
     - Cotisation Minimale (CM): $0.25\% \times 10,930,700 = \mathbf{27,327\text{ MAD}}$.
     - **Fiscal Invariant**: $\mathbf{\text{IS} > \text{CM}}$ by $3.6\times$ (guaranteeing that progressive IS barème, 2025->2026 slice 1 rate hike ($17.5\% \to 20\%$, delta +7,500 MAD), 4 quarterly acomptes, dividend distribution, and vintage WHT rules are fully active and testable).

4. **Normalized Seasonality Curve & Cash Planning**:
   - Normalized Monthly Multipliers ($\sum_{m=1}^{12} M_m = 12.00$, $\text{Monthly\_CA}_m = \frac{\text{Annual\_CA}}{12} \times M_m$):
     - Oct: 1.15, Nov: 1.35, Dec: 1.45, Jan: 1.35, Feb: 1.45, Mar: 1.25 (Harvest peak sum = 8.00).
     - Apr: 0.90, May: 0.70, Jun: 0.50, Jul: 0.40, Aug: 0.50, Sep: 0.95 (Low season sum = 4.00).

5. **Headcount & Payroll Grid (`config/payroll_grid.yaml`)**:
   - Headcount: **22 permanent employees + 5 seasonal operators**.
   - Total Annual Gross Payroll: **2,089,586 MAD**.
   - Reconciles 1:1 with P&L labour line: $\text{Gross} + \text{CNSS Employer } (21.09\%) + \text{AT Insurance } (3.80\%) = \mathbf{2,580,000\text{ MAD}}$.
   - Seasonal workers sit exactly at SMIG (17.10 MAD/h in 2025 -> 17.92 MAD/h in 2026), creating a quantifiable +5% wage shock on 01/01/2026.

6. **Working Capital (BFR) & Credit-Line Sizing**:
   - Receivables (DSO weighted ~90 days across segments): $\approx 2,730,000\text{ MAD}$.
   - Inventory (Raw materials 45 days + Finished goods 15 days): $\approx 1,160,000\text{ MAD}$.
   - Payables (DPO supplier paper mills ~60-90 days): $\approx 1,250,000\text{ MAD}$.
   - **Peak BFR (High Season Oct-Mar)**: $\approx \mathbf{3,400,000\text{ to } 3,600,000\text{ MAD}}$.
   - Fonds de Roulement (FR) from opening balance sheet: $\approx \mathbf{1,900,000\text{ MAD}}$.
   - **Authorized Bank Facilities (Sizing)**:
     - Ligne d'escompte commerciale (AWB): **1,500,000 MAD**.
     - Facilité de caisse / Découvert autorisé (AWB): **600,000 MAD**.
     - Crédit de campagne agricole (CAM, Sep-Mar): **400,000 MAD**.
     - **Treasury Invariant**: Bank balance must never breach authorized overdraft ceilings.

7. **Commercial Client Ecosystem (6 market segments)**:
   - Agri-Exporters 42%, Modern Retail / GMS 26%, Souk/Traditional Wholesale 12%, Agro-Industrial Processors 10%, Direct EU Exports 6%, Cooperatives 4%.

8. **Supply Chain & Customs Tariff Engine**:
   - European Union Origin (`origin: EU`): **0% Droit d'Importation (DI)** under Morocco-EU Association Agreement (with EUR.1 proof of origin).
   - Non-EU Origin (MFN Chapter 48 `[TO VERIFY]`): Kraftliner 10%, Fluting 2.5%, Corrugated board 25%.
   - All imports: 0.25% TPI + 20% Import TVA on (CIF + DI + TPI).

---

## 4. Requirements: Rules, Accounting Matrix, State Machines & Invariants

### R2. Effective-Dated Domain Rules & Multi-Year Transition Engine (FY2025 -> FY2026)
Encode all mathematical models into structured **effective-dated parameter tables** (`parameter_name`, `value`, `valid_from`, `valid_to`, `source_citation`). Every parameter must cite its legal source:
- **Corporate Income Tax (IS) - Progressive Barème Method**:
  - Slice <= 300,000 MAD: 17.50% (2025) -> 20.00% (2026).
  - Slice 300,001 to 1,000,000 MAD: 20.00% (2025) -> 20.00% (2026).
  - Slice 1,000,001 to 100,000,000 MAD: 22.75% (2025, per LF 2023 linear convergence) -> 20.00% (2026).
  - Upper Slice >= 100,000,000 MAD: 34.00% (2025) -> 35.00% (2026).
  - Cotisation Minimale Base (CGI Art. 144): 0.25% of (CA HT + Produits accessoires + Produits financiers excluding dividends + Subventions/dons), floor 3,000 MAD.
  - 4 Acomptes provisionnels (25% each of prior-year IS) due Mar 31, Jun 30, Sep 30, Dec 31; regularization by Mar 31 N+1.
- **Accounting Result -> Fiscal Result Reconciliation (*Tableau de passage*) & Dual Cash Rules**:
  - *Reintegrations*: Non-deductible tax/social penalties, advertising gifts > 100 MAD, non-deductible provisions.
  - *CGI Cash Rules (Dual-Sided)*:
    1. **Purchases Cash Ceiling (CGI Art. 11-II & Art. 106-II)**: Supplier expenses paid in cash exceeding 5,000 MAD TTC (monthly supplier cap 50,000 MAD) are non-deductible from IS, and input TVA is 100% non-recoverable.
    2. **Sales Cash Collection Penalty (CGI Art. 193)**: Client settlements received in cash exceeding statutory limit (baseline: 20,000 MAD `[TO VERIFY]`) trigger a statutory sanction/penalty on the selling company (6% to 15% on excess cash amount).
- **Value Added Tax (TVA) - LF 2024 Multi-Year Convergence**:
  - Standard rate: 20%; Industrial Electricity (ONEE MV): 18% (2025) -> 20% (2026); Industrial Water: 9% (2025) -> 10% (2026); Banking operations & agios: 10% (CGI Art. 99-3); Transport: 14% -> 16% `[TO VERIFY]`; Direct Exports: 0% with deduction right (CGI Art. 92).
  - Declaration Regime: Monthly e-filing (SIMPL-TVA) due by the **last day of month M+1**.
- **Personal Income Tax (IR) & Social Deductions (LF 2025 Updates)**:
  - Baseline IR Annual Barème: 0-40k: 0%; 40k-60k: 10% (ded. 4,000); 60k-80k: 20% (ded. 10,000); 80k-100k: 30% (ded. 18,000); 100k-180k: 34% (ded. 22,000); >180k: 37% (ded. 27,400) `[TO VERIFY]`.
  - Professional expenses abatement: apply LF 2025 updated ceiling.
  - Dependent deduction: 500 MAD/year per dependent (LF 2025), max 6 dependents (3,000 MAD/year).
  - SIMPL-IR monthly e-filing due by the **last day of month M+1**.
- **Social Contributions & Minimum Wage (SMIG)**:
  - SMIG: 17.10 MAD/h (3,266.10 MAD/m) in 2025 -> 17.92 MAD/h (3,422.72 MAD/m) on 01/01/2026.
  - CNSS Employer: 21.09% (8.98% prestations capped at 6,000 MAD/month, 6.40% allocations familiales, 1.60% formation pro, 2.26% AMO, 1.85% solidarite AMO).
  - CNSS Employee: 6.74% (4.48% prestations capped at 6,000 MAD/month, 2.26% AMO).
  - Mandatory AT Insurance: ~3.80% of gross payroll.
- **Withholding Taxes (Retenues a la Source) - Vintage Rule**:
  - Dividends to resident shareholders: 11.25% in 2025 (LF 2023 linear glide: 15% -> 13.75% -> 12.50% -> 11.25% in 2025 -> 10.00% in 2026; CGI Art. 73-II).
  - Vintage Rule: Retained earnings from pre-2023 profits taxed at 15.00%; distributions from 2023+ earnings taxed at reduced glide rate (11.25% in 2025 / 10.00% in 2026).
- **Local Taxes (TP & TSC)**:
  - TP 5-year initial exemption (2020-2024); first taxable year in 2025.
  - Rental Value (*Valeur Locative - VL*): 3% of historical gross acquisition cost of land/buildings + 3% of equipment gross cost.
  - TP Rate: 10% (Class 2 industrial rate `[TO VERIFY]`); TSC Rate: 10.50% in urban municipal area.
- **Treasury, Banking & Law 69-21**:
  - BAM key rate: effective-dated series in `config/parameters.yaml`.
  - Discounting agio: `Agio = (Nominal * Rate * Days)/360 + Endos Commission + Service Fees + TVA 10% on fees`.
  - Law 69-21 Tier: 10M to 50M MAD CA Tier (quarterly declarations); Penalties: BAM key rate + 0.25% month 1 + 0.85% additional months.
- **Customs & FX Clamped Engine**:
  - Port of Agadir surestaries: Days 1-7: 0; Days 8-14: 150 MAD/d; Days 15-21: 300 MAD/d; Day 22+: 500 MAD/d.
  - FX Engine: Monthly random walk clamped strictly within BAM's +/-5% currency basket fluctuation band (EUR/MAD base 10.74, sigma 0.008; USD/MAD base 9.30, sigma 0.012).

### R3. Machine-Readable Event Catalog & Zero-Fault PCM Journal Matrix
1. **Machine-Readable Event Catalog (`config/events.yaml` & `docs/03_event_catalog.md`)**:
   - Numbered event catalog (`EVT-SAL-xxx`, `EVT-PUR-xxx`, `EVT-PAY-xxx`, `EVT-BNK-xxx`, `EVT-TAX-xxx`, `EVT-INV-xxx`, `EVT-RSK-xxx`, `EVT-CLS-xxx`) with triggers, preconditions, and postconditions.
2. **Machine-Readable Zero-Fault PCM Journal Matrix (`config/journal_templates.yaml` & `docs/04_pcm_journal_matrix.md`)**:
   - Every event maps 1:1 to a balanced journal template.
   - Journal Codes: `RAN` (A-nouveaux), `ACH` (Achats), `VEN` (Ventes), `BQ-AWB`, `BQ-BP`, `BQ-CAM`, `BQ-BMCE`, `CAI`, `PAI`, `OD`.
   - Balanced accounting invariant: `Sum(Debits) == Sum(Credits)` for every template.

### R4. Transaction Orchestration & State Machine Design
Finite state machines for all 6 operational cycles: Order-to-Cash, Procure-to-Pay & Import, Payroll & Social Security, Tax & Compliance, Year-End Closing & Dynamic Roll-Over, Risk & Random Events Engine.

---

## 5. Phase 1 Acceptance Criteria & 12-Point Programmatic Verification Suite

### Blueprint & Artifact Quality
- [ ] **Complete Deliverables Manifest**: All 6 documentation files (`docs/01` to `06`), 4 schema files (`schemas/*.json`, `schemas/schema.sql`), 10 config files (`config/*.yaml`), and 1 verification script (`scripts/verify_specs.py`) exist in the working directory and are fully populated.
- [ ] **Closed Economic Model & Business Plan**: `config/business_plan.yaml` models BOM material costing (3.10 MAD/m2), selling price (5.753 MAD/m2), 1.9M m2 volume, 2.4M m2 capacity (79.2% load factor), target P&L envelope with IS > CM, and normalized seasonality summing to 12.00.
- [ ] **Detailed Payroll Grid**: `config/payroll_grid.yaml` enumerates 22 permanent + 5 seasonal workers, reconciling to 2,089,586 MAD annual gross payroll and 2.58M MAD P&L labour line.
- [ ] **Historical Opening Balance Sheet**: `config/opening_balance_sheet.yaml` reconciles 5-year asset depreciation history and explicitly partitions retained earnings into pre-2023 and 2023+ tranches.
- [ ] **Authoritative Chart of Accounts & Asset Register**: `config/chart_of_accounts.yaml` contains complete PCM account listings, and `config/fixed_assets_depreciation.yaml` details all opening assets, useful lives, and linear depreciation rates.
- [ ] **Primary Source Citations & Origin Rules**: 100% of fiscal, social, and banking rates in `config/parameters.yaml` include explicit legal citations (CGI, LF, Décret, BAM), with EU 0% preferential customs tariffs and effective-dated BAM series.
- [ ] **Syntactic & Referential Integrity**: All JSON schemas validate against JSON Schema Draft-07/2020-12, and canonical `schemas/schema.sql` compiles cleanly in PostgreSQL (with foreign key constraints).

### Automated Verification Test Suite (`scripts/verify_specs.py`)
- **Execution Contract**: Standalone Python script requiring only Python stdlib + `PyYAML` + `jsonschema`. Emits a structured `verify_report.json` and exits with code `0` on 100% pass (non-zero on any failure).
- **The 12 Mandatory Programmatic Checks**:
  1. *Account Referential Integrity*: Every account referenced in `config/journal_templates.yaml` exists in `config/chart_of_accounts.yaml`.
  2. *1:1 Event Coverage*: Every event in `config/events.yaml` maps to exactly one template in `config/journal_templates.yaml` and vice-versa.
  3. *Zero Journal Imbalance*: Every template in `config/journal_templates.yaml` is mathematically balanced (`Sum(Debits) == Sum(Credits)`).
  4. *Effective-Dated Parameter Integrity*: For every parameter in `config/parameters.yaml`, validity intervals (`valid_from` to `valid_to`) have **zero gaps and zero overlaps** across `2025-01-01` to `2026-12-31`.
  5. *Business Plan Algebra*: Verifies that `Sum(volume * price * segment_mix) == Target_CA` within 0.1% tolerance, and monthly seasonality multipliers sum to exactly 12.00.
  6. *Costing & Margin Consistency*: Verifies that weighted selling price >= 1.5x direct material cost from BOM.
  7. *P&L Envelope & Fiscal Invariant*: Verifies that target pre-tax result > 0 and computed `IS > CM` (by at least 2.5x).
  8. *Payroll Reconciliation*: Verifies that sum of gross wages in `config/payroll_grid.yaml` plus employer contributions equals the P&L labour line within 1.0% tolerance.
  9. *Credit-Line Sufficiency*: Verifies that authorized facilities (escompte 1.5M + découvert 600k + campaign 400k) exceed peak high-season monthly BFR deficit.
  10. *Balance Sheet Equilibrium*: Verifies that opening balance sheet satisfies `Actif == Passif` and `FR - BFR == TN`.
  11. *Retained Earnings Vintage Partition*: Verifies that sum of pre-2023 and 2023+ retained earnings equals account 1191 in opening balance sheet.
  12. *Audit Metrics*: Reports total verified parameters and count of `[TO VERIFY]` flags in `verify_report.json`.
