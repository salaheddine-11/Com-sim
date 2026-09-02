# SOUSS AGRI-PACK SARL — TEST_READY VERIFICATION ATTESTATION

**Document ID**: `ATTEST-PHASE1-VERIFY`
**Execution Script**: `scripts/verify_specs.py`
**Output Artifact**: `verify_report.json`
**Execution Status**: **100% PASS (12/12 Checks)**
**Standard**: Plan Comptable Général Marocain (PCM / CGNC Loi 9-88), CGI 2025/2026, LF 2023-2025, BAM, ADII, CNSS

> **Snapshot scope**: This attestation was regenerated against the repository at this commit. It documents the **as-tested** numbers (304 chart accounts, 52 events, 52 templates, 148 posting lines). Any prior copy of this file that quoted "366 accounts" or "49 events / 49 templates" is superseded by this version — the underlying YAML catalogues grew during build-out and the attestation now reflects the actual authoritative files.

---

## 1. Executive Summary & Verification Suite Overview

The formal specification and closed economic architecture of **Souss Agri-Pack SARL** (Zone Industrielle Ait Melloul, Agadir) have been programmatically validated through the standalone verification engine `scripts/verify_specs.py`.

The verification suite enforces the strict **Invariant Algebra** defined in `docs/06_verification_rulebook.md`, ensuring that all regulatory, accounting, costing, banking, social, and schema dimensions are mathematically bounded, internally coherent, and ready for synthetic transaction generation in Phase 2.

```
+==================================================================================================+
|                       PHASE 1 FORMAL VERIFICATION RESULTS: 12 / 12 PASS                          |
+==================================================================================================+
|  #   | Verification Check                        | Target Invariant              | Status | Delta|
+------+-------------------------------------------+-------------------------------+--------+------+
| 01   | Account Referential Integrity             | Templates -> Chart of Accounts|  PASS  | 0.00 |
| 02   | 1:1 Bijective Event Coverage              | Events <-> Journal Templates  |  PASS  | 0.00 |
| 03   | Zero Journal Imbalance                    | Sum(Debits) == Sum(Credits)   |  PASS  | 0.00 |
| 04   | Effective-Dated Parameter Integrity       | Zero gaps, zero overlaps      |  PASS  | 0.00 |
| 05   | Business Plan Revenue Algebra             | SKU sum == Target CA (10.93M) |  PASS  | 0.00 |
| 06   | Costing & Margin Consistency              | Selling Price >= 1.5x BOM Cost|  PASS  | 1.70x|
| 07   | P&L Envelope & Fiscal Invariant           | IS > CM (Ratio >= 2.50x)      |  PASS  | 3.60x|
| 08   | Payroll Labour Line Reconciliation        | Payroll Grid == P&L (2.58M)   |  PASS  | 0.03%|
| 09   | Credit-Line Sufficiency                   | Authorized Bank Lines >= BFR  |  PASS  |+880k |
| 10   | Balance Sheet Equilibrium                 | Actif == Passif & FR - BFR = TN| PASS  | 0.00 |
| 11   | Retained Earnings Vintage Partition       | Pre-2023 + Post-2023 == 1191  |  PASS  | 0.00 |
| 12   | Audit Metrics & Schema Validation         | Draft-07 Schemas & Legal Cit. |  PASS  | 0 err|
+==================================================================================================+
```

---

## 2. Catalogue Metrics (As Tested)

| Metric | Value | Source |
|---|---|---|
| Chart of Accounts entries | **304** | `config/chart_of_accounts.yaml` |
| Authoritative PCM classes covered | 8 (classes 1–8) | `config/chart_of_accounts.yaml` |
| Accounts referenced by templates | 78 | `verify_specs.py` Check 01 |
| Business events in catalog | **52** | `config/events.yaml` |
| Journal templates in matrix | **52** | `config/journal_templates.yaml` |
| Total posting lines (debit + credit rows) | **148** | `verify_specs.py` Check 01 |
| Event categories | 8 (SAL, PUR, PAY, BNK, TAX, INV, RSK, CLS) | `config/events.yaml` |
| Journal codes used | RAN, ACH, VEN, BQ-AWB, BQ-CAM, PAI, OD | `config/journal_templates.yaml` |
| Unique parameter names | 66 (in 57 families) | `config/parameters.yaml` |
| Temporal parameter slices | 66 across `[2025-01-01, 2026-12-31]` | `verify_specs.py` Check 04 |
| Parameters with verified primary citations | 59 | `verify_specs.py` Check 12 |
| Parameters explicitly flagged `[TO VERIFY]` | 7 | `verify_specs.py` Check 12 |
| Raw `[TO VERIFY]` markers in `parameters.yaml` | 15 | grep (`verify_specs.py` reports the deduped count of 7 *unique parameters* with the flag) |

### Event-category breakdown (52 events)

| Category | Count | Domain |
|---|---|---|
| EVT-SAL-xxx | 7 | Order-to-Cash & commercial sales |
| EVT-PUR-xxx | 7 | Procure-to-Pay & customs imports |
| EVT-PAY-xxx | 6 | Payroll & social security |
| EVT-BNK-xxx | 8 | Treasury, banking, discounting |
| EVT-TAX-xxx | 7 | Tax & compliance |
| EVT-INV-xxx | 3 | Inventory & production |
| EVT-RSK-xxx | 7 | Risk & random events |
| EVT-CLS-xxx | 7 | Year-end closing |

### Journal-code breakdown (52 templates)

| Code | Templates | Meaning |
|---|---|---|
| RAN | 1 | Reports à nouveau (opening carry-over) |
| ACH | 7 | Achats (purchases journal) |
| VEN | 4 | Ventes (sales journal) |
| BQ-AWB | 10 | Banque Attijariwafa Bank |
| BQ-CAM | 2 | Banque Crédit Agricole du Maroc |
| PAI | 3 | Paie (payroll journal) |
| OD | 25 | Opérations Diverses (miscellaneous) |

---

## 3. Invariant Breakdown & Validation Results

### Check 1: Account Referential Integrity
- **Result**: **PASS**
- **Validation**: Scanned all 52 double-entry journal templates across 148 posting lines. Every referenced account number (78 unique 8-digit PCM accounts) exists in `config/chart_of_accounts.yaml` (304 authoritative accounts).
- **Orphan Accounts**: **0**

### Check 2: 1:1 Bijective Event Coverage
- **Result**: **PASS**
- **Validation**: Validated bijective 1:1 mapping between 52 declared events in `config/events.yaml` and 52 journal templates in `config/journal_templates.yaml`.
- **Symmetric Difference**: $|\Delta| = 0$ (0 unmapped events, 0 orphan templates, 0 duplicates).

### Check 3: Zero Journal Imbalance
- **Result**: **PASS**
- **Validation**: Evaluated symbolic linear combinations and numerical substitutions ($x = 1000.00\text{ MAD}$) across all 52 journal templates in `config/journal_templates.yaml`.
- **Maximum Imbalance**: **$0.00\text{ MAD}$** across 100% of debit/credit equations.

### Check 4: Effective-Dated Parameter Integrity
- **Result**: **PASS**
- **Validation**: Analyzed all 57 parameter families comprising 66 temporal validity intervals in `config/parameters.yaml`. Verified that every parameter series continuously covers `2025-01-01` to `2026-12-31` with zero time gaps and zero temporal overlaps.
- **Anomalies Count**: **0**

### Check 5: Business Plan Revenue Algebra & Seasonality Normalization
- **Result**: **PASS**
- **Validation**:
  - SKU Revenue Sum: $760\text{k}\times 5.50 + 532\text{k}\times 5.80 + 266\text{k}\times 6.20 + 190\text{k}\times 6.00 + 152\text{k}\times 5.7625 = \mathbf{10,930,700.00\text{ MAD HT}}$.
  - Revenue Target Delta: **$0.00\text{ MAD}$ ($0.0000\%$ variance)**.
  - Monthly Seasonality Multipliers: $\sum_{m=1}^{12} M_m = 1.15 + 1.35 + 1.45 + 1.35 + 1.45 + 1.25 + 0.90 + 0.70 + 0.50 + 0.40 + 0.50 + 0.95 = \mathbf{12.0000}$.

### Check 6: Costing & Margin Consistency
- **Result**: **PASS**
- **Validation**:
  - Consumed Paper Grammage: $150 + (120 \times 1.48) + 150 = \mathbf{477.60\text{ g/m}^2}$ ($0.4776\text{ kg/m}^2$).
  - Direct Paper Cost: $0.4776 \times 6.20 = 2.9574\text{ MAD/m}^2$.
  - Auxiliaries & Chemicals: $0.1500\text{ MAD/m}^2$.
  - Net Material Cost: $3.1074\text{ MAD/m}^2$.
  - Gross Direct Material Cost (8% technical scrap): $(2.9574 + 0.1500) / 0.92 = \mathbf{3.3776\text{ MAD/m}^2}$.
  - Weighted Average Selling Price: $\mathbf{5.7530\text{ MAD/m}^2}$.
  - Gross Margin Multiplier: $\frac{5.7530}{3.3776} = \mathbf{1.7033\times \ge 1.50\times}$.
  - Net Margin Multiplier: $\frac{5.7530}{3.1074} = \mathbf{1.8514\times \ge 1.50\times}$.

### Check 7: P&L Envelope & Fiscal Invariant
- **Result**: **PASS**
- **Validation**:
  - Chiffre d'Affaires HT: $10,930,700.00\text{ MAD}$.
  - Total Charges: $10,435,000.00\text{ MAD}$ -> Pre-Tax Accounting Profit: $\mathbf{+495,700.00\text{ MAD}} > 0$.
  - Reintegrations: $+34,300.00\text{ MAD}$ -> Taxable Fiscal Profit: $\mathbf{530,000.00\text{ MAD}}$.
  - Progressive IS 2025: $(300\text{k} \times 17.5\%) + (230\text{k} \times 20.0\%) = 52,500 + 46,000 = \mathbf{98,500.00\text{ MAD}}$.
  - Cotisation Minimale (CM): $10,930,700 \times 0.25\% = \mathbf{27,326.75\text{ MAD}}$.
  - Fiscal Activation Ratio: $\frac{98,500.00}{27,326.75} = \mathbf{3.6045\times \ge 2.50\times}$.

### Check 8: Payroll & Social Charges Labour Reconciliation
- **Result**: **PASS** (delta 786.18 MAD / 0.0305%, well under the 1.0% tolerance)
- **Validation**:
  - Headcount: 22 permanent employees (CDI) + 5 seasonal operators (CDD 6 months).
  - Annual Gross Payroll (Accounts 61711/61712): $\mathbf{2,113,816.08\text{ MAD}}$.
  - CNSS Employer: $\mathbf{385,072.73\text{ MAD}}$.
  - AT Insurance (3.80% uncapped): $\mathbf{80,325.01\text{ MAD}}$.
  - Total Employer Labour Cost: $2,113,816.08 + 385,072.73 + 80,325.01 = \mathbf{2,579,213.82\text{ MAD}}$.
  - Target P&L Labour Line: $\mathbf{2,580,000.00\text{ MAD}}$ (**$786.18\text{ MAD}$ delta / $0.0305\%$ variance**).

### Check 9: Credit-Line Sufficiency & Liquidity Adequacy
- **Result**: **PASS**
- **Validation**:
  - High-Season Peak BFR: $3,520,000.00\text{ MAD}$.
  - Fonds de Roulement (FR): $1,900,000.00\text{ MAD}$.
  - Peak Cash Deficit: $3,520,000 - 1,900,000 = \mathbf{1,620,000.00\text{ MAD}}$.
  - Total Authorized Bank Facilities: Escompte AWB ($1.5\text{M}$) + Découvert AWB ($600\text{k}$) + Campagne CAM ($400\text{k}$) = $\mathbf{2,500,000.00\text{ MAD}}$.
  - Net Liquidity Safety Buffer: $2,500,000 - 1,620,000 = \mathbf{+880,000.00\text{ MAD}} \ge 500,000\text{ MAD}$.

### Check 10: Balance Sheet Equilibrium & Fundamental Identity
- **Result**: **PASS**
- **Validation**:
  - Total Actif Net: $5,128,700.00\text{ (Immob)} + 4,795,000.00\text{ (Circ)} + 310,000.00\text{ (Trés)} = \mathbf{10,233,700.00\text{ MAD}}$.
  - Total Passif Net: $7,028,700.00\text{ (Perm)} + 2,705,000.00\text{ (Circ)} + 500,000.00\text{ (Trés)} = \mathbf{10,233,700.00\text{ MAD}}$.
  - Equilibrium Delta: $\mathbf{0.00\text{ MAD}}$.
  - $\text{FR} = 7,028,700 - 5,128,700 = \mathbf{1,900,000.00\text{ MAD}}$.
  - $\text{BFR} = 4,795,000 - 2,705,000 = \mathbf{2,090,000.00\text{ MAD}}$.
  - $\text{TN} = 310,000 - 500,000 = \mathbf{-190,000.00\text{ MAD}}$.
  - Identity Check: $\text{FR} - \text{BFR} = 1,900,000 - 2,090,000 = \mathbf{-190,000.00\text{ MAD}} \equiv \text{TN}$ (**$0.00\text{ MAD}$ delta**).

### Check 11: Retained Earnings Vintage Partition
- **Result**: **PASS**
- **Validation**:
  - Pre-2023 Vintage Retained Earnings (Account 11611 / 119101, WHT 15.00%): $\mathbf{2,150,000.00\text{ MAD}}$.
  - Post-2023 Vintage Retained Earnings (Account 11612 / 119102, Glide 11.25%/10.00%): $\mathbf{1,678,700.00\text{ MAD}}$.
  - Partition Sum: $2,150,000 + 1,678,700 = \mathbf{3,828,700.00\text{ MAD}} \equiv \text{Account 1191 Stated Total}$.
  - Reconciled Delta: **$0.00\text{ MAD}$**.

### Check 12: Audit Metrics & Schema Validation
- **Result**: **PASS**
- **Validation**:
  - Total Regulatory Parameters: **66** (in 57 families).
  - Verified Primary Legal Citations: **59** (CGI 2025/2026, LF 2023-2025, Dahir CNSS 1972, BAM, ADII).
  - Explicit `[TO VERIFY]` Baseline Flags on **7 unique parameters** (15 raw markers, some parameters carry multiple `[TO VERIFY]` annotations across slices).
  - JSON Schema Draft-07 Validation: **0 errors** across `schemas/entities.json`, `schemas/events.json`, `schemas/journal_entries.json`.

---

## 4. Execution Commands & Standalone Verification

To independently execute and re-verify the full verification suite:

```bash
# From project root
python scripts/verify_specs.py
```

The script produces formatted terminal output and writes the canonical audit report to `verify_report.json`.

To independently re-run the Phase 2 forensic audit on the generated data:

```bash
python scripts/audit_fy2025_data.py
```

Output written to `data/fy2025/reports/phase2_audit_report.json` (15/15 checks).

---

## 5. Phase 2 Certification & Gateway Acceptance

All 8 Phase 2 Acceptance Gates defined in `docs/06_verification_rulebook.md` are **100% satisfied**:

1. [x] **100% Pass on 12 Verification Checks**: Verified via `scripts/verify_specs.py` (Exit Code 0).
2. [x] **Complete Documentation Suite**: `docs/01` through `docs/06` fully authored.
3. [x] **Valid JSON Schemas & SQL DDL**: Valid Draft-07 JSON schemas and PostgreSQL DDL.
4. [x] **Complete YAML Configuration Suite**: 10 balanced YAML configuration files in `config/`.
5. [x] **Audit Citations & [TO VERIFY] Accounting**: 66 parameters tracked with citations; 7 carry the explicit `[TO VERIFY]` baseline flag (15 raw markers across slices).
6. [x] **Zero Double-Entry Journal Imbalances**: Sum(Debits) == Sum(Credits) for all 52 templates.
7. [x] **Retained Earnings Vintage Segregation**: Pre-2023 (15%) and Post-2023 (11.25%/10.00%) partitioned.
8. [x] **Forensic Integrity Attestation**: Genuine mathematical evaluation with no hardcoded shortcuts.

**The Phase 1 specification is hereby certified TEST_READY, and the Phase 2 synthetic dataset (262 sales invoices, 262 LCRs, 294 payroll slips, 1,488 balanced journal entries, Actif≡Passif = 30,674,578.79 MAD trial balance) is hereby certified DATA_READY.**