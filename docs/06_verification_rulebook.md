# SOUSS AGRI-PACK SARL — FORMAL VERIFICATION RULEBOOK & INVARIANT ALGEBRA
**Document ID**: `DOC-06-VRULE`  
**Version**: 1.0.0 (Phase 1 Formal Specification)  
**Execution Script**: `scripts/verify_specs.py`  
**Output Artifact**: `verify_report.json`  
**Execution Contract**: Standalone Python 3.10+ execution with standard library + `PyYAML` + `jsonschema`. Exits with code `0` on 100% pass, non-zero on any failure.

---

## 1. Executive Summary & Verification Philosophy

The Souss Agri-Pack SARL simulation engine is anchored in a formal **Invariant Algebra**. Every economic, regulatory, social, banking, and accounting module is mathematically bounded and programmatically verifiable.

The verification rulebook governs:
1. **The 12 Mandatory Programmatic Checks**: Formal mathematical proofs and algorithmic checks executed by `scripts/verify_specs.py`.
2. **Syntactic & Schema Validity**: Strict validation against JSON Schema Draft-07/2020-12 and ANSI-SQL DDL standards.
3. **Phase 2 Acceptance Contract**: The non-negotiable gateway criteria required before generating row-level synthetic transaction datasets.

```
+==================================================================================================+
|                                12-POINT VERIFICATION ARCHITECTURE                                |
+==================================================================================================+
|                                                                                                  |
|   SYNTACTIC & REFERENTIAL INTEGRITY             ECONOMIC & COSTING INTEGRITY                     |
|  ┌────────────────────────────────────────┐    ┌──────────────────────────────────────────────┐  |
|  │ Check 1: Account Referential Integrity │    │ Check 5: Business Plan Revenue Algebra       │  |
|  │ Check 2: 1:1 Bijective Event Coverage  │    │ Check 6: Costing & Margin Consistency (>=1.5x)│  |
|  │ Check 3: Zero Journal Imbalance        │    │ Check 7: P&L Envelope & Fiscal Invariant     │  |
|  │ Check 4: Effective-Dated Gaps/Overlaps │    │ Check 8: Payroll Labour Line Reconciliation  │  |
|  └────────────────────────────────────────┘    └──────────────────────────────────────────────┘  |
|                                                                                                  |
|   FINANCIAL & BALANCE SHEET EQUILIBRIUM         AUDIT METRICS & GOVERNANCE                       |
|  ┌────────────────────────────────────────┐    ┌──────────────────────────────────────────────┐  |
|  │ Check 9: Bank Facility Sufficiency     │    │ Check 12: Citations Audit & [TO VERIFY] Count│  |
|  │ Check 10: Balance Sheet (FR - BFR = TN)│    │                                              │  |
|  │ Check 11: Retained Earnings Vintage    │    │ Output: verify_report.json (Exit Code 0)     │  |
|  └────────────────────────────────────────┘    └──────────────────────────────────────────────┘  |
+==================================================================================================+
```

---

## 2. Formal Mathematical Definitions of the 12 Programmatic Checks

### Check 1: Account Referential Integrity
- **Mathematical Invariant**:
  Let $S_{\text{coa}} = \{ a \mid a \in \text{config/chart\_of\_accounts.yaml} \}$ be the set of all authoritative Moroccan PCM accounts.  
  Let $A_{\text{tpl}} = \bigcup_{t \in \text{journal\_templates}} \{ \text{line.account\_number} \mid \text{line} \in t.\text{lines} \}$ be the set of accounts referenced in journal templates.
  $$\forall a \in A_{\text{tpl}}, \quad a \in S_{\text{coa}} \iff A_{\text{tpl}} \subseteq S_{\text{coa}}$$
- **Algorithmic Validation**:
  1. Parse `config/chart_of_accounts.yaml` and collect all `account_number` strings.
  2. Parse `config/journal_templates.yaml` and iterate over every line in every template.
  3. Assert that every referenced account exists in $S_{\text{coa}}$.
  4. Flag any orphan account with fatal error status.
- **Pass Threshold**: $\text{Orphan Accounts Count} \equiv 0$.

---

### Check 2: 1:1 Bijective Event Coverage
- **Mathematical Invariant**:
  Let $E = \{ e.\text{event\_id} \mid e \in \text{config/events.yaml} \}$ be the set of declared business events.  
  Let $T = \{ t.\text{event\_id} \mid t \in \text{config/journal\_templates.yaml} \}$ be the set of events mapped in templates.
  $$E \setminus T = \emptyset \quad \land \quad T \setminus E = \emptyset \quad \land \quad |E| = |T|$$
- **Algorithmic Validation**:
  1. Extract unique event IDs from `config/events.yaml`.
  2. Extract unique event IDs from `config/journal_templates.yaml`.
  3. Compute symmetric difference: $\Delta = (E \setminus T) \cup (T \setminus E)$.
  4. Assert $|\Delta| == 0$.
- **Pass Threshold**: Bijective 1:1 mapping with 0 unmapped events and 0 orphan templates.

---

### Check 3: Zero Journal Imbalance
- **Mathematical Invariant**:
  For every template $t \in \text{config/journal\_templates.yaml}$ with lines $L_t$:
  $$\left| \sum_{l \in L_t} \text{Debit}(l) - \sum_{l \in L_t} \text{Credit}(l) \right| = 0.00\text{ MAD}$$
- **Algorithmic Validation**:
  1. For static numerical templates (e.g. `TPL-CLS-001`, `TPL-CLS-007`): compute $\sum \text{Debit} - \sum \text{Credit}$.
  2. For parameterized formulas: substitute standard test vectors ($x = 1000.00$) into symbolic debit and credit expressions.
  3. Assert mathematical equality to 2 decimal places ($0.00$ delta).
- **Pass Threshold**: Maximum allowable imbalance across all templates is $\mathbf{0.00\text{ MAD}}$.

---

### Check 4: Effective-Dated Parameter Tree Integrity
- **Mathematical Invariant**:
  For every effective-dated parameter $P$ with temporal slices $\{ [s_1, e_1], [s_2, e_2], \dots, [s_n, e_n] \}$ ordered by start date:
  $$s_1 \le \text{2025-01-01} \quad \land \quad e_n \ge \text{2026-12-31}$$
  $$\forall i \in [1, n-1], \quad e_i + 1\text{ day} = s_{i+1}$$
- **Algorithmic Validation**:
  1. Traverse all parameters in `config/parameters.yaml`.
  2. For each parameter series, sort slices chronologically.
  3. Verify that the earliest start date covers `2025-01-01` and latest end date covers `2026-12-31`.
  4. Check that no time gaps ($s_{i+1} > e_i + 1$) and no temporal overlaps ($s_{i+1} \le e_i$) exist.
- **Pass Threshold**: 100% gap-free, overlap-free validity coverage over the full two-year horizon.

---

### Check 5: Business Plan Revenue Algebra & Seasonality Normalization
- **Mathematical Invariant**:
  $$\text{Target CA} = \sum_{i=1}^5 \left( \text{Volume}_i \times P_{\text{unit}, i} \right) = \text{Total Volume} \times \bar{P} = 1,900,000\text{ m}^2 \times 5.7530\text{ MAD/m}^2 = \mathbf{10,930,700.00\text{ MAD}}$$
  $$\left| \frac{\sum_{i=1}^5 (\text{Volume}_i \times P_i) - 10930700.00}{10930700.00} \right| < 0.001 \quad (0.1\%)$$
  $$\sum_{m=1}^{12} M_m = 1.15 + 1.35 + 1.45 + 1.35 + 1.45 + 1.25 + 0.90 + 0.70 + 0.50 + 0.40 + 0.50 + 0.95 = \mathbf{12.0000}$$
- **Algorithmic Validation**:
  1. Parse SKU volumes and prices from `config/business_plan.yaml` and calculate total product turnover.
  2. Sum the 12 monthly seasonality multipliers.
  3. Assert multiplier sum equals $12.0000 \pm 0.0001$.
- **Pass Threshold**: Revenue delta $\le 1.00\text{ MAD}$ and seasonality sum $\equiv 12.0000$.

---

### Check 6: Costing & Margin Consistency
- **Mathematical Invariant**:
  $$\text{Paper Consumed} = m_{\text{outer}} (150\text{ g}) + [m_{\text{fluting}} (120\text{ g}) \times 1.4800] + m_{\text{inner}} (150\text{ g}) = \mathbf{477.60\text{ g/m}^2} = 0.4776\text{ kg/m}^2$$
  $$C_{\text{mat, gross}} = \frac{(0.4776 \times 6.2000) + 0.1500}{1 - 0.0800} = \frac{2.9574 + 0.1500}{0.92} = \mathbf{3.3776\text{ MAD/m}^2}$$
  $$\text{Margin Multiplier} = \frac{\bar{P}}{C_{\text{mat, gross}}} = \frac{5.7530}{3.3776} = \mathbf{1.7033\times} \ge 1.50\times$$
  $$\left(\text{or } \frac{5.7530}{3.1074\text{ net}} = \mathbf{1.8514\times} \ge 1.50\times\right)$$
- **Algorithmic Validation**:
  1. Verify BOM grammage calculations and take-up factor $k = 1.4800$.
  2. Compute gross direct material cost factoring 8.00% technical scrap.
  3. Assert that weighted average selling price ($\bar{P} = 5.7530\text{ MAD}$) exceeds direct material cost by at least $1.50\times$.
- **Pass Threshold**: $\text{Margin Multiplier} \ge 1.5000\times$.

---

### Check 7: P&L Envelope & Fiscal Invariant
- **Mathematical Invariant**:
  $$\text{Pre-Tax Accounting Profit} = \text{CA} (10,930,700) - \text{Total Charges} (10,435,000) = \mathbf{+495,700.00\text{ MAD}} > 0$$
  $$\text{Résultat Fiscal} = 495,700.00 + \text{Réintégrations} (34,300.00) = \mathbf{530,000.00\text{ MAD}}$$
  $$\text{IS}_{\text{2025}} = (300,000 \times 17.50\%) + (230,000 \times 20.00\%) = 52,500 + 46,000 = \mathbf{98,500.00\text{ MAD}}$$
  $$\text{CM} = 10,930,700.00 \times 0.0025 = \mathbf{27,326.75\text{ MAD}}$$
  $$\text{Fiscal Ratio} = \frac{\text{IS}_{\text{2025}}}{\text{CM}} = \frac{98,500.00}{27,326.75} = \mathbf{3.6045\times} \ge 2.50\times$$
- **Algorithmic Validation**:
  1. Validate line-by-line P&L sum in `config/business_plan.yaml`.
  2. Compute progressive IS liability and Cotisation Minimale.
  3. Assert $\text{IS} / \text{CM} \ge 2.50\times$.
- **Pass Threshold**: Fiscal activation ratio $\ge 2.50\times$, guaranteeing progressive barème execution.

---

### Check 8: Payroll & Social Charges Labour Reconciliation
- **Mathematical Invariant**:
  $$\text{Gross Payroll (61711/61712)} = \sum_{i=1}^{27} \text{Annual Gross}_i = \mathbf{2,089,586.00\text{ MAD}}$$
  $$\text{CNSS Patronale (61741/61742)} = \sum_{i=1}^{27} \text{CNSS Employer}_i = \mathbf{411,010.00\text{ MAD}}$$
  $$\text{AT Insurance (61761)} = 2,089,586.00 \times 0.0380 = \mathbf{79,404.00\text{ MAD}}$$
  $$\text{Total Labour Cost} = 2,089,586.00 + 411,010.00 + 79,404.00 = \mathbf{2,580,000.00\text{ MAD}}$$
  $$\left| \frac{\text{Computed Labour} - 2580000.00}{2580000.00} \right| \le 0.010 \quad (1.0\% \text{ tolerance})$$
- **Algorithmic Validation**:
  1. Parse all 27 roles (22 permanent + 5 seasonal) from `config/payroll_grid.yaml`.
  2. Recompute capped prestations (6,000 MAD/month) and uncapped allocations/AMO.
  3. Compare total employer cost to P&L Labour Line ($2,580,000\text{ MAD}$).
- **Pass Threshold**: Exact $0.00\text{ MAD}$ delta ($0.0\%$ variance $\le 1.0\%$).

---

### Check 9: Bank Facility Sizing & Liquidity Adequacy
- **Mathematical Invariant**:
  $$\text{Peak BFR Deficit} = \text{Peak BFR} (3,520,000\text{ MAD}) - \text{Fonds de Roulement} (1,900,000\text{ MAD}) = \mathbf{1,620,000.00\text{ MAD}}$$
  $$\sum \text{Authorized Bank Facilities} = \text{Escompte} (1.5\text{M}) + \text{Découvert} (600\text{k}) + \text{Campagne CAM} (400\text{k}) = \mathbf{2,500,000.00\text{ MAD}}$$
  $$\text{Liquidity Buffer} = 2,500,000.00 - 1,620,000.00 = \mathbf{+880,000.00\text{ MAD}} > 0$$
- **Algorithmic Validation**:
  1. Parse bank lines from `config/opening_balance_sheet.yaml` / `schemas/entities.json`.
  2. Calculate high-season peak cash requirement.
  3. Assert total facilities exceed peak deficit by at least $500,000\text{ MAD}$.
- **Pass Threshold**: Positive liquidity buffer guaranteeing no unauthorized overdraft breach.

---

### Check 10: Balance Sheet Equilibrium & Fundamental Identity
- **Mathematical Invariant**:
  $$\text{Total Actif Net} = 5,128,700.00 + 4,795,000.00 + 310,000.00 = \mathbf{10,233,700.00\text{ MAD}}$$
  $$\text{Total Passif Net} = 7,028,700.00 + 2,705,000.00 + 500,000.00 = \mathbf{10,233,700.00\text{ MAD}}$$
  $$\Delta(\text{Actif} - \text{Passif}) = \mathbf{0.00\text{ MAD}}$$
  $$\text{FR} (1,900,000.00) - \text{BFR} (2,090,000.00) = \mathbf{-190,000.00\text{ MAD}} \equiv \text{Trésorerie Nette (TN)}$$
- **Algorithmic Validation**:
  1. Sum all asset and liability accounts in `config/opening_balance_sheet.yaml`.
  2. Compute $\text{FR} = \text{Financement Permanent} - \text{Actif Immobilisé Net}$.
  3. Compute $\text{BFR} = \text{Actif Circulant} - \text{Passif Circulant}$.
  4. Compute $\text{TN} = \text{Trésorerie Actif} - \text{Trésorerie Passif}$.
  5. Assert $\text{Actif} == \text{Passif}$ and $\text{FR} - \text{BFR} == \text{TN}$.
- **Pass Threshold**: $\Delta \text{Equilibrium} \equiv 0.00\text{ MAD}$.

---

### Check 11: Retained Earnings Vintage Partition
- **Mathematical Invariant**:
  $$\text{Retained Earnings Pre-2023 (Compte 11611000 / 119101)} = \mathbf{2,150,000.00\text{ MAD}} \quad (\text{WHT 15.00\%})$$
  $$\text{Retained Earnings Post-2023 (Compte 11612000 / 119102)} = \mathbf{1,678,700.00\text{ MAD}} \quad (\text{WHT 11.25\% / 10.00\%})$$
  $$\text{Sum} = 2,150,000.00 + 1,678,700.00 = \mathbf{3,828,700.00\text{ MAD}} \equiv \text{Account 1191 / 1161 Total}$$
- **Algorithmic Validation**:
  1. Extract vintage sub-accounts from `config/opening_balance_sheet.yaml`.
  2. Verify that pre-2023 and 2023+ tranches sum exactly to total retained earnings.
- **Pass Threshold**: Exact $0.00\text{ MAD}$ reconciliation.

---

### Check 12: Audit Metrics & Quality Gate
- **Mathematical Invariant**:
  Let $N_{\text{param}}$ be the total count of regulatory parameters in `config/parameters.yaml`.  
  Let $N_{\text{verified}}$ be the count of parameters carrying authentic primary legal citations (CGI, LF, Décret, BAM, ADII).  
  Let $N_{\text{to\_verify}}$ be the count of unresolved `[TO VERIFY]` flags.
  $$N_{\text{to\_verify}} \equiv 0 \quad \land \quad N_{\text{verified}} = N_{\text{param}}$$
- **Algorithmic Validation**:
  1. Scan all fields in `config/parameters.yaml` for `[TO VERIFY]` tags or missing citations.
  2. Validate all JSON schemas against JSON Schema Draft-07 meta-schema.
  3. Emit structured test metrics to `verify_report.json`.
- **Pass Threshold**: $N_{\text{to\_verify}} == 0$ and $0$ schema validation errors.

---

## 3. Automated Test Execution & JSON Report Schema

When `python scripts/verify_specs.py` is invoked, it produces the canonical `verify_report.json` conforming to the schema below:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SoussAgriPackVerificationReport",
  "type": "object",
  "required": [
    "timestamp",
    "overall_status",
    "checks_passed",
    "checks_failed",
    "total_checks",
    "checks",
    "audit_metrics"
  ],
  "properties": {
    "timestamp": { "type": "string", "format": "date-time" },
    "overall_status": { "type": "string", "enum": ["PASS", "FAIL"] },
    "checks_passed": { "type": "integer" },
    "checks_failed": { "type": "integer" },
    "total_checks": { "type": "integer", "enum": [12] },
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["check_id", "check_name", "status", "message", "metrics"],
        "properties": {
          "check_id": { "type": "integer" },
          "check_name": { "type": "string" },
          "status": { "type": "string", "enum": ["PASS", "FAIL"] },
          "message": { "type": "string" },
          "metrics": { "type": "object" }
        }
      }
    },
    "audit_metrics": {
      "type": "object",
      "required": ["total_parameters", "verified_parameters_count", "to_verify_count", "schema_validation_errors"],
      "properties": {
        "total_parameters": { "type": "integer" },
        "verified_parameters_count": { "type": "integer" },
        "to_verify_count": { "type": "integer" },
        "schema_validation_errors": { "type": "integer" }
      }
    }
  }
}
```

---

## 4. Phase 2 Acceptance Contract & Verification Gate

The handover from **Phase 1 (Specification & Verification Suite)** to **Phase 2 (Synthetic Transaction Generation & Engine Execution)** is strictly governed by the following quality gates:

```
+--------------------------------------------------------------------------------------------------+
| PHASE 2 ACCEPTANCE CONTRACT CHECKLIST                                                            |
+----+----------------------------------------------+----------------------------------+-----------+
| #  | Verification Gate Requirement                | Acceptance Standard              | Status    |
+----+----------------------------------------------+----------------------------------+-----------+
| 1  | 100% Pass on 12 Verification Checks          | scripts/verify_specs.py exit 0   | MANDATORY |
| 2  | Complete Documentation Suite (`docs/01-06`)   | 6 markdown files fully authored  | MANDATORY |
| 3  | Valid JSON Schemas & SQL DDL (`schemas/*`)   | Draft-07 valid & SQL executable  | MANDATORY |
| 4  | Complete YAML Configuration Suite (`config/*`)| 10 config files balanced to 0.00 | MANDATORY |
| 5  | Zero Unresolved Legal Citations              | 0 [TO VERIFY] flags remaining    | MANDATORY |
| 6  | Zero Double-Entry Journal Imbalances         | Sum(Dr) == Sum(Cr) for all TPL   | MANDATORY |
| 7  | Retained Earnings Vintage Segregation        | Pre-2023 (15%) / 2023+ (glide)   | MANDATORY |
| 8  | Forensic Integrity Attestation               | No hardcoded shortcuts or facades| MANDATORY |
+----+----------------------------------------------+----------------------------------+-----------+
```

When all 8 acceptance gates are satisfied, the Phase 1 specification is certified for synthetic transaction dataset generation in Phase 2.
