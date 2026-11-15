# Souss Agri-Pack SARL — High-Fidelity Moroccan Industrial & Accounting Simulation

A closed-economy, multi-cycle synthetic data generation engine and formal double-entry accounting ledger system modeled after Moroccan regulatory standards (**Plan Comptable Marocain / CGNC, CGI 2025/2026, LF 2023–2025, BAM, ADII, Dahir CNSS 1972, Loi 69-21**).

---

## 🏢 Company Profile

- **Entity**: Souss Agri-Pack SARL
- **Address:** Lotissement Industriel 45, Zone Industrielle Ait Melloul, 80150 Agadir, Morocco *(single identity, aligned with `config/business_plan.yaml`)*
- **Legal Identifiers**:
  - **ICE**: `002345678000091`
  - **IF**: `45127890`
  - **RC**: `28451` (Tribunal de Commerce d'Agadir)
  - **TP**: `30145280`
  - **CNSS**: `9127456`
- **Capital**: 800,000 MAD (8,000 parts de 100 MAD)
- **Activity**: Corrugated cardboard packaging manufacturing for the Souss-Massa agricultural export corridor (Citrus, Tomatoes, Berries, Avocados).

---

## 📂 Repository Structure

```
souss_agripack_sim/
├── config/                          # Machine-readable formal configurations
│   ├── business_plan.yaml           # Revenue target (10.93M MAD), BOM costing, pricing, capacity & seasonality
│   ├── chart_of_accounts.yaml       # 304 PCM Moroccan accounts (4 to 8 digits, 8 classes)
│   ├── events.yaml                  # Numbered transactional event catalog (57 events, 8 categories)
│   ├── fixed_assets_depreciation.yaml # Asset register with linear depreciation schedules
│   ├── inventory_policies.yaml      # CUMP valuation, scrap rates, and BOM definitions
│   ├── journal_templates.yaml       # Zero-fault double-entry debit/credit posting templates
│   ├── opening_balance_sheet.yaml   # Balanced 01/01/2025 opening accounts (10.23M MAD)
│   ├── parameters.yaml              # Effective-dated fiscal/social parameters with legal citations
│   ├── payroll_grid.yaml            # Headcount (22 CDI + 5 Seasonal), gross salaries, CNSS & IR
│   └── risk_events_probabilities.yaml # PRNG seeds and operational risk distributions
├── data/
│   └── fy2025/                      # Generated FY 2025 synthetic datasets
│       ├── accounting/              # General journal & 6-column trial balance
│       ├── database/                # SQLite database (souss_sim_2025.db)
│       ├── operational/             # Sales invoices, purchase invoices, payroll slips, LCNs
│       └── reports/                 # Bilan, CPC, Liasse Fiscale, Audit reports
├── docs/                            # Comprehensive domain architecture documentation
│   ├── 01_world_architecture.md
│   ├── 02_regulatory_engines.md
│   ├── 03_event_catalog.md
│   ├── 04_pcm_journal_matrix.md
│   ├── 05_state_machines.md
│   └── 06_verification_rulebook.md
├── generator/                       # Core simulation & ledger posting modules (11 modules + __init__.py)
│   ├── closing_generator.py         # Year-end linear DDA, fiscal reconciliation, IS liquidation
│   ├── financial_reports.py         # Moroccan Bilan, CPC & Tableau de Passage generator
│   ├── models.py                    # Data structures with Decimal monetary precision
│   ├── parameters_engine.py         # Effective-dated temporal parameter resolver
│   ├── payroll_generator.py         # Monthly payroll engine (CNSS, AMO, IR barème 2025)
│   ├── pcm_ledger_engine.py         # Dynamic template posting & balance validation engine
│   ├── purchase_generator.py        # Domestic paper, EU import DUMs, utilities (ONEE)
│   ├── sales_generator.py           # Order-to-Cash, delivery notes, 15-digit ICE sales invoices
│   ├── simulation_clock.py          # Daily clock management with business days
│   ├── tax_compliance_generator.py  # IS liquidation, TVA returns, IR/CNSS filings, 4 acomptes IS
│   └── treasury_generator.py        # LCN discounting (AWB), agios, maturities, settlements
├── schemas/                         # Formal JSON & SQL data contracts
│   ├── entities.json
│   ├── events.json
│   ├── journal_entries.json
│   └── schema.sql
└── scripts/
    ├── audit_fy2025_data.py         # 15-point programmatic invariant forensic audit suite
    ├── run_simulation_fy2025.py     # Master 365-day simulation runner
    └── verify_specs.py              # 12-point formal specification verification suite
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- `PyYAML`
- `jsonschema`

```bash
pip install pyyaml jsonschema
```

### 1. Run Formal Specifications Verification
```bash
python scripts/verify_specs.py
```
> Validates all 12 mathematical invariants, chart of accounts referential integrity, parameter continuity, linear BOM costing, and credit line adequacy.

### 2. Execute FY 2025 Master Simulation
```bash
python scripts/run_simulation_fy2025.py
```
> Generates 365 days of operational transactions, posts double-entry journals dynamically, executes year-end tax liquidation, and compiles Moroccan financial statements.

### 3. Run Forensic Data Audit Suite
```bash
python scripts/audit_fy2025_data.py
```
> Audits all 15 accounting identities ($Actif \equiv Passif$, $FR - BFR \equiv TN$, double-entry balance with $0.00\text{ MAD}$ delta, ICE compliance, and CNSS ceiling adherence).

---

## 📊 Key Simulation Results (FY 2025)

- **Turnover (Chiffre d'Affaires HT)**: `10,885,818.20 MAD`
- **Total Invoices**: `262 Sales Invoices` (100% valid 15-digit ICE)
- **Commercial Bills (LCN)**: `262 LCNs drawn and discounted`
- **Payroll**: `294 Monthly Payslips` across 27 employees (`2.58M MAD` labour line)
- **Pre-Tax Accounting Profit**: `904,251.34 MAD`
- **Corporate Tax (IS 2025)**: `179,350.27 MAD` ($\text{IS} > \text{CM}$ by $6.6\times$)
- **Net Profit**: `724,901.07 MAD`
- **Total Actif Net $\equiv$ Total Passif**: `16,292,460.59 MAD` ($\Delta = 0.00\text{ MAD}$)
- **FR ($3,004,901.07$) - BFR ($-602,189.08$) $\equiv$ TN ($3,607,090.15\text{ MAD}$)**

### Numbering conventions in this repo

- **Trial-balance sum vs published Bilan net**: The raw sum of `total_debit` / `total_credit` columns across all 304 accounts in `data/fy2025/accounting/balance_generale.csv` equals **30,674,578.79 MAD** — this is the *gross* trial-balance aggregate that double-counts DDA amortizations across the year. The `16,292,460.59 MAD` figure published in the Bilan is the *net closing* position after netting DDA against 28 amortization accounts. Both are correct; refer to `data/fy2025/reports/bilan_2025.md` for the net figures and the balance générale for trial-balance aggregates.
- **`verify_report.json`** at the repo root is a **build artifact** regenerated by `scripts/verify_specs.py`. Treat it as a snapshot, not as a manually-edited source-of-truth.
- **`[TO VERIFY]` flag counting**: The number reported in the README/TEST_READY ("7") counts *unique parameter names* carrying the flag; `grep -c '\[TO VERIFY\]' config/parameters.yaml` returns 15 because some flagged parameters carry multiple markers across temporal slices.

### Repository-at-a-glance (as of latest verify run)

| Metric | Value | Source |
|---|---|---|
| Chart of accounts | 304 entries, 8 PCM classes | `config/chart_of_accounts.yaml` |
| Business events | 57 across 8 categories | `config/events.yaml` |
| Journal templates | 57 templates, 158 posting lines | `config/journal_templates.yaml` |
| Regulatory parameters | 66 (57 families, 7 `[TO VERIFY]`) | `config/parameters.yaml` |
| Generator modules | 11 modules + `__init__.py` (3 of them load YAML via PyYAML) | `generator/` |
| Phase 1 checks | 12 / 12 PASS | `verify_specs.py` |
| Phase 2 forensic checks | 15 / 15 PASS | `audit_fy2025_data.py` |
| Generated journal entries | 1,488 (all balanced, Δ = 0.00) | `data/fy2025/accounting/journal_general.csv` |
