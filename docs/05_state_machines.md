# SOUSS AGRI-PACK SARL — OPERATIONAL STATE MACHINES & LIFECYCLE WORKFLOWS
**Document ID**: `DOC-05-FSM`  
**Version**: 1.0.0 (Phase 1 Formal Specification)  
**System Architecture**: Deterministic Finite State Machines (FSM) with Ledger Side-Effects & Rollback Mechanisms  
**Applicable Frameworks**: Plan Comptable Marocain (PCM), Code de Commerce (Loi 15-95, Loi 69-21), CGI 2025/2026, Dahir CNSS 1972, Code des Douanes ADII.

---

## 1. Executive Summary & Orchestration Principles

Every business transaction and operational lifecycle in the Souss Agri-Pack SARL simulation executes under strict **Finite State Machine (FSM)** semantics. The orchestration architecture guarantees:
1. **Deterministic State Transitions**: Transitions occur if and only if explicit guard conditions evaluate to `TRUE`.
2. **Synchronized Ledger Mutations**: State transitions trigger discrete business events that map 1:1 to balanced PCM journal templates.
3. **Rollback & Quarantine Isolation**: Any validation or operational failure (credit breaches, quality defects, customs holds) triggers safe quarantine states or explicit rollback compensation.

```
+--------------------------------------------------------------------------------------------------+
| OPERATIONAL STATE MACHINES SUMMARY                                                               |
+----+--------------------------------+----------------------+--------------------+----------------+
| #  | Operational Cycle Name         | Scope / Flow         | States Count       | Error Handling |
+----+--------------------------------+----------------------+--------------------+----------------+
| 1  | Order-to-Cash (O2C)            | Sales -> Cash        | 10 Active States   | Credit Hold    |
| 2  | Procure-to-Pay & Import (P2P)  | PO -> Clearance-> Pay| 11 Active States   | Quarantine/Dem.|
| 3  | Payroll & Social Security      | Timeclock -> Remit   | 6 Active States    | SMIG Guard     |
| 4  | Tax & Regulatory Compliance    | Period -> SIMPL File | 8 Active States    | Late Penalty   |
| 5  | Year-End Closing & Roll-Over   | Cut-Off -> RAN Open  | 9 Active States    | Audit Check    |
| 6  | Risk & Stochastic Engine       | Shock -> Mitigate    | 6 Active States    | Solvency Guard |
+----+--------------------------------+----------------------+--------------------+----------------+
```

---

## 2. Cycle 1: Order-to-Cash (O2C) State Machine

### 2.1 ASCII State Transition Diagram

```
                   ┌───────────────────────────┐
                   │          QUOTED           │
                   └─────────────┬─────────────┘
                                 │ Trigger: Customer Purchase Order
                                 ▼
                   ┌───────────────────────────┐
                   │      ORDER_CONFIRMED      │
                   └─────────────┬─────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │ Guard: Outst + Ord <= Limit   │ Guard: Outst + Ord > Limit
                 ▼                               ▼
     ┌───────────────────────┐       ┌───────────────────────┐
     │  CREDIT_CHECK_PASSED  │       │      CREDIT_HOLD      │
     └───────────┬───────────┘       └───────────┬───────────┘
                 │                               │ Trigger: DAF Override / Cash Pay
                 │                               ▼
                 │                   ┌───────────────────────┐
                 │◄──────────────────│     CREDIT_CLEARED    │
                 │                   └───────────────────────┘
                 │ Trigger: Factory Scheduling
                 ▼
     ┌───────────────────────┐
     │ PRODUCTION_SCHEDULED  │
     └───────────┬───────────┘
                 │ Trigger: Converting & Palletizing
                 ▼
     ┌───────────────────────┐
     │  FINISHED_GOODS_REC   │
     └───────────┬───────────┘
                 │ Trigger: Outbound Carrier BL
                 ▼
     ┌───────────────────────┐
     │     DISPATCHED_BL     │
     └───────────┬───────────┘
                 │ Trigger: Invoicing (EVT-SAL-003 Domestic / EVT-SAL-004 Export)
                 ▼
     ┌───────────────────────┐
     │       INVOICED        │ (Journal VEN: 3421 Dr / 7121 Cr, 4455 Cr)
     └───────────┬───────────┘
                 │
       ┌─────────┴───────────────────────────────┐
       │ Settlement: LCN Traite 60-90d           │ Settlement: Virement / Cheque
       ▼                                         ▼
┌──────────────┐                         ┌────────────────┐
│  LCN_ISSUED  │ (EVT-BNK-001: 3424/3421)│ FUNDS_RECEIVED │ (Journal BQ: 5141/3421)
└──────┬───────┘                         └───────┬────────┘
       │ Trigger: Remittance (EVT-BNK-002)       │
       ▼                                         │
┌──────────────┐                                 │
│LCN_DISCOUNTED│ (EVT-BNK-003: 5141,6318/5520)   │
└──────┬───────┘                                 │
       │                                         │
       ├─────────────────────────┐               │
       │ Due Date (EVT-BNK-004)  │ Protest/Impayé│
       ▼                         ▼               │
┌──────────────┐         ┌───────────────┐       │
│FUNDS_SETTLED │◄────────┤ LCN_PROTESTED │       │
└──────────────┘         └───────┬───────┘       │
       ▲                         │ EVT-BNK-005   │
       │                         ▼               │
       │                 ┌───────────────┐       │
       │                 │DOUBTFUL_DEBTOR│◄──────┘ (Overdue > 180d: EVT-SAL-007)
       │                 └───────┬───────┘
       │                         │ Legal Recovery / Write-Off
       └─────────────────────────┴───────────────► [CLOSED]
```

### 2.2 Transition Table & Ledger Mutation Rules

```
+-----------------------------------------------------------------------------------------------------------------------+
| ORDER-TO-CASH (O2C) TRANSITION TABLE                                                                                  |
+---------------------+-------------------+-------------------------------+---------------------+-----------------------+
| Source State        | Trigger Event     | Guard Condition               | Target State        | Ledger Side-Effects   |
+---------------------+-------------------+-------------------------------+---------------------+-----------------------+
| QUOTED              | Client PO Rec.    | Client active in master       | ORDER_CONFIRMED     | None                  |
| ORDER_CONFIRMED     | Credit Engine     | Receivables + Order <= Limit  | CREDIT_CHECK_PASSED | None                  |
| ORDER_CONFIRMED     | Credit Engine     | Receivables + Order > Limit   | CREDIT_HOLD         | None                  |
| CREDIT_HOLD         | DAF Resolution    | Guarantees / Down-payment     | CREDIT_CLEARED      | None                  |
| CREDIT_CHECK_PASSED | Scheduler Release | Paper inventory available     | PRODUCTION_SCHED.   | Reserve BOM inventory |
| PRODUCTION_SCHED.   | Machine Finished  | QA Burst/BCT test passed      | FINISHED_GOODS_REC  | EVT-INV-002 (3151/713)|
| FINISHED_GOODS_REC  | Truck Dispatch    | Signed Delivery Slip (BL)     | DISPATCHED_BL       | Stock Outbound Log    |
| DISPATCHED_BL       | Billing Trigger   | Domestic (20% TVA)            | INVOICED            | EVT-SAL-003 (VEN)     |
| DISPATCHED_BL       | Billing Trigger   | Direct EU Export (0% Art 92)  | INVOICED            | EVT-SAL-004 (VEN)     |
| INVOICED            | LCN Acceptance    | Signed commercial bill        | LCN_ISSUED          | EVT-BNK-001 (3424/3421|
| LCN_ISSUED          | Treasury Need     | AWB line headroom available   | LCN_DISCOUNTED      | EVT-BNK-002 / 003     |
| LCN_DISCOUNTED      | Bill Maturity     | Drawee honors payment         | FUNDS_SETTLED       | EVT-BNK-004 (5520/5115|
| LCN_DISCOUNTED      | Maturity Protest  | Drawee dishonors / rejects    | LCN_PROTESTED       | EVT-BNK-005 (3421/5141|
| LCN_PROTESTED       | Formal Notice     | Overdue > 180 days            | DOUBTFUL_DEBTOR     | EVT-SAL-007 (3425/3942|
+---------------------+-------------------+-------------------------------+---------------------+-----------------------+
```

---

## 3. Cycle 2: Procure-to-Pay & Inbound Import (P2P) State Machine

### 3.1 ASCII State Transition Diagram

```
       ┌───────────────────────────┐
       │        REQ_CREATED        │
       └─────────────┬─────────────┘
                     │ Trigger: MRP Reorder Point (Stock < 45d buffer)
                     ▼
       ┌───────────────────────────┐
       │        PO_APPROVED        │
       └─────────────┬─────────────┘
       ┌─────────────┴─────────────────────────────┐
       │ (Domestic Paper Mills GPC/CMCP)           │ (EU Importation CIF Agadir)
       ▼                                           ▼
┌──────────────┐                           ┌─────────────────┐
│ PO_DISPATCHED│                           │ VESSEL_EN_ROUTE │
└──────┬───────┘                           └────────┬────────┘
       │                                            │ Trigger: Vessel Berth Agadir Port
       │                                            ▼
       │                                   ┌─────────────────┐
       │                                   │ CUSTOMS_PORT_DUM│ (Port Free Time: Days 1-7)
       │                                   └────────┬────────┘
       │                                            │
       │                   ┌────────────────────────┴────────────────────────┐
       │                   │ Clearance <= 7 days                             │ Dwell > 7 days
       │                   ▼                                                 ▼
       │           ┌─────────────────┐                             ┌───────────────────┐
       │           │ CUSTOMS_CLEARED │ (EVT-PUR-004 EUR.1 0% DI)   │PORT_DEMURRAGE_HOLD│ (EVT-RSK-002)
       │           └────────┬────────┘                             └─────────┬─────────┘
       │                    │                                                │ Demurrage Paid
       │                    │◄───────────────────────────────────────────────┘
       └───────────┬────────┘
                   │ Trigger: Truck Inbound Ait Melloul Gate
                   ▼
          ┌─────────────────┐
          │ GOODS_INSPECTED │ (Moisture check & burst strength testing)
          └────────┬────────┘
                   │
           ┌───────┴───────────────────────────────┐
           │ Moisture <= 8.5%                      │ Moisture > 12% (Defective)
           ▼                                       ▼
  ┌─────────────────┐                     ┌───────────────────┐
  │ GOODS_ACCEPTED  │ (EVT-PUR-002)       │QUARANTINE_REJECTED│──► [RETURN_TO_SUPPLIER]
  └────────┬────────┘                     └───────────────────┘
           │ Trigger: 3-Way Match (PO + BR + Supplier Invoice)
           ▼
  ┌─────────────────┐
  │ INVOICE_MATCHED │ (EVT-PUR-003 local / 006 utility in Journal ACH)
  └────────┬────────┘
           │ Trigger: Payment Schedule Maturity (60-90d DPO)
           ▼
  ┌─────────────────┐
  │ PAYMENT_APPROVED│
  └────────┬────────┘
           │ Trigger: Bank Wire Transfer (EVT-BNK-006)
           ▼
  ┌─────────────────┐
  │     SETTLED     │ (Journal BQ-AWB: 4411 Dr / 51411 Cr)
  └─────────────────┘
```

### 3.2 Transition Table & Rollback Paths

```
+-----------------------------------------------------------------------------------------------------------------------+
| PROCURE-TO-PAY & IMPORT (P2P) TRANSITION TABLE                                                                        |
+---------------------+-------------------+-------------------------------+---------------------+-----------------------+
| Source State        | Trigger Event     | Guard Condition               | Target State        | Ledger Side-Effects   |
+---------------------+-------------------+-------------------------------+---------------------+-----------------------+
| REQ_CREATED         | MRP Run           | Stock <= Safety buffer        | PO_APPROVED         | None                  |
| PO_APPROVED         | Domestic Supplier | Supplier active in master     | PO_DISPATCHED       | None                  |
| PO_APPROVED         | Foreign Mill (EU) | Proforma CIF Agadir confirmed | VESSEL_EN_ROUTE     | None                  |
| VESSEL_EN_ROUTE     | Port Discharge    | Container discharged at dock  | CUSTOMS_PORT_DUM    | Port log registered   |
| CUSTOMS_PORT_DUM    | ADII Liquidation  | Dwell <= 7 days + EUR.1 valid | CUSTOMS_CLEARED     | EVT-PUR-004 (ACH)     |
| CUSTOMS_PORT_DUM    | Clearance Delay   | Dwell > 7 days                | PORT_DEMURRAGE_HOLD | EVT-RSK-002 (Demurrage|
| PORT_DEMURRAGE_HOLD | Demurrage Settled | Marsa Maroc fee paid          | CUSTOMS_CLEARED     | EVT-PUR-004 / 005     |
| CUSTOMS_CLEARED     | Factory Delivery  | Truck arrived at plant        | GOODS_INSPECTED     | None                  |
| GOODS_INSPECTED     | QA Lab Test       | Moisture <= 8.5%              | GOODS_ACCEPTED      | CUMP Stock Updated    |
| GOODS_INSPECTED     | QA Lab Test       | Moisture > 12.0%              | QUARANTINE_REJECTED | Claim issued; no stock|
| GOODS_ACCEPTED      | Invoice Match     | 3-Way Price & Qty Match       | INVOICE_MATCHED     | EVT-PUR-003 (ACH)     |
| INVOICE_MATCHED     | Due Date Schedule | Payment term reached (60-90d) | PAYMENT_APPROVED    | None                  |
| PAYMENT_APPROVED    | Bank Transfer     | Cash / Overdraft available    | SETTLED             | EVT-BNK-006 (BQ-AWB)  |
+---------------------+-------------------+-------------------------------+---------------------+-----------------------+
```

---

## 4. Cycle 3: Payroll, Social Security & Statutory Remuneration State Machine

### 4.1 ASCII State Transition Diagram

```
                 ┌───────────────────────────┐
                 │      ATTENDANCE_OPEN      │
                 └─────────────┬─────────────┘
                               │ Trigger: Month-End Timeclock Close (25th of month)
                               ▼
                 ┌───────────────────────────┐
                 │      HOURS_VALIDATED      │ (22 Permanent + 5 Seasonal Workers)
                 └─────────────┬─────────────┘
                               │ Trigger: Payroll Calculation Engine
                               ▼
                 ┌───────────────────────────┐
                 │     PAYROLL_CALCULATED    │ (Gross, CNSS 6.74%, AMO, IR LF 2025)
                 └─────────────┬─────────────┘
                               │ Trigger: Journal Posting (EVT-PAY-001, 002, 003)
                               ▼
                 ┌───────────────────────────┐
                 │      JOURNAL_POSTED       │ (Journal PAI: 6171, 6174 Dr / 4432, 4441 Cr)
                 └─────────────┬─────────────┘
                               │ Trigger: Salary Transfer Date (28th of month)
                               ▼
                 ┌───────────────────────────┐
                 │    SALARIES_DISBURSED     │ (EVT-PAY-004: 4432 Dr / 51411 Cr)
                 └─────────────┬─────────────┘
             ┌─────────────────┴─────────────────┐
             │ 10th of Month M+1                 │ Last Day of Month M+1
             ▼                                   ▼
     ┌───────────────┐                   ┌───────────────┐
     │ CNSS_DECLARED_│                   │ SIMPL_IR_FILED│
     │     PAID      │ (EVT-PAY-005)     │     PAID      │ (EVT-PAY-006)
     └───────────────┘                   └───────────────┘
```

### 4.2 Transition Table & Statutory Guards

```
+-----------------------------------------------------------------------------------------------------------------------+
| PAYROLL & SOCIAL SECURITY TRANSITION TABLE                                                                            |
+---------------------+-------------------+-------------------------------+---------------------+-----------------------+
| Source State        | Trigger Event     | Guard Condition               | Target State        | Ledger Side-Effects   |
+---------------------+-------------------+-------------------------------+---------------------+-----------------------+
| ATTENDANCE_OPEN     | 25th of Month     | All timecards submitted       | HOURS_VALIDATED     | None                  |
| HOURS_VALIDATED     | Calc Engine       | SMIG compliance verified      | PAYROLL_CALCULATED  | None                  |
| PAYROLL_CALCULATED  | Approval Signature| Reconciles with labour budget | JOURNAL_POSTED      | EVT-PAY-001/002/003   |
| JOURNAL_POSTED      | 28th of Month     | Bank funds available          | SALARIES_DISBURSED  | EVT-PAY-004 (BQ-AWB)  |
| SALARIES_DISBURSED  | 10th of M+1       | DAMANCOM portal submission    | CNSS_DECLARED_PAID  | EVT-PAY-005 (BQ-AWB)  |
| SALARIES_DISBURSED  | End of M+1        | SIMPL-IR portal submission    | SIMPL_IR_FILED_PAID | EVT-PAY-006 (BQ-AWB)  |
+---------------------+-------------------+-------------------------------+---------------------+-----------------------+
```

---

## 5. Cycle 4: Tax & Regulatory Compliance State Machine

### 5.1 ASCII State Transition Diagram

```
                 ┌───────────────────────────┐
                 │      PERIOD_CLOSING       │
                 └─────────────┬─────────────┘
                               │ Trigger: Month-End / Quarter-End / Year-End
                               ▼
                 ┌───────────────────────────┐
                 │      DATA_EXTRACTED       │
                 └─────────────┬─────────────┘
           ┌───────────────────┼───────────────────┐
           │ Monthly (TVA)     │ Quarterly (IS/L69)│ Annual (IS / TP / TSC)
           ▼                   ▼                   ▼
   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
   │ SIMPL_TVA_RUN │   │IS_ACOMPTE_RUN │   │ ANNUAL_IS_RUN │
   └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
           │                   │                   │
           ▼                   ▼                   ▼
   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
   │ TVA_LIQUIDATED│   │ ACOMPTE_PAID  │   │ LIASSE_FISCALE│ (Tableau de Passage:
   │ (EVT-TAX-001) │   │ (EVT-TAX-003) │   │   FINALIZED   │  Résultat Fiscal 530k)
   └───────┬───────┘   └───────────────┘   └───────┬───────┘
           │                                       │
           ▼                                       ▼
   ┌───────────────┐                       ┌───────────────┐
   │ TVA_TELEPAID  │                       │ IS_LIQUIDATED │ (EVT-TAX-004:
   │ (EVT-TAX-002) │                       │ (Reliquat due)│  6701/34531/4453)
   └───────────────┘                       └───────────────┘
```

---

## 6. Cycle 5: Year-End Closing & Dynamic Roll-Over State Machine

### 6.1 ASCII State Transition Diagram

```
              ┌───────────────────────────┐
              │ PRE_CLOSING_TRIAL_BALANCE │
              └─────────────┬─────────────┘
                            │ Step 1: DDA Amortizations (EVT-CLS-001: 380k MAD)
                            ▼
              ┌───────────────────────────┐
              │   DDA_AND_PROVISIONS_RUN  │
              └─────────────┬─────────────┘
                            │ Step 2: Cut-Offs (CCA: EVT-CLS-002 / FAE: EVT-CLS-003)
                            ▼
              ┌───────────────────────────┐
              │     CUTOFFS_ADJUSTED      │
              └─────────────┬─────────────┘
                            │ Step 3: Fiscal Reconciliation & Corporate Tax
                            ▼
              ┌───────────────────────────┐
              │    TAX_LIQUIDATION_RUN    │ (IS Dû = 98,500 MAD > CM 27,327 MAD)
              └─────────────┬─────────────┘
                            │ Step 4: Expense & Revenue Clearance to CPC
                            ▼
              ┌───────────────────────────┐
              │    CPC_ACCOUNTS_CLOSED    │ (EVT-CLS-004 Class 6 / EVT-CLS-005 Class 7)
              └─────────────┬─────────────┘
                            │ Step 5: Net Profit Determination (EVT-CLS-006 -> 1191)
                            ▼
              ┌───────────────────────────┐
              │  BALANCE_SHEET_BALANCED   │ (Actif == Passif = 10,233,700 MAD)
              └─────────────┬─────────────┘
                            │ Step 6: AGM Profit Allocation & Vintage RAS
                            ▼
              ┌───────────────────────────┐
              │   RESERVES_AND_DIVIDENDS  │ (EVT-TAX-006: 15% pre-2023 vs glide path)
              └─────────────┬─────────────┘
                            │ Step 7: Roll-Over to FY 2026 Opening Ledger
                            ▼
              ┌───────────────────────────┐
              │    JOURNAL_RAN_OPENED     │ (EVT-CLS-007: Journal des À-Nouveaux)
              └───────────────────────────┘
```

---

## 7. Cycle 6: Risk & Stochastic Events Engine State Machine

### 7.1 ASCII State Transition Diagram

```
              ┌───────────────────────────┐
              │   STOCHASTIC_EVALUATION   │
              └─────────────┬─────────────┘
                            │ Monte Carlo Seed Step (Seeds 42001–42007)
                            ▼
              ┌───────────────────────────┐
              │    EVENT_INSTANTIATED     │
              └─────────────┬─────────────┘
        ┌───────────────────┼───────────────────┐
        │ Paper Spoilage    │ Agadir Demurrage  │ Cash Limit Breach
        ▼                   ▼                   ▼
 ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
 │ EVT-RSK-001 │     │ EVT-RSK-002 │     │ EVT-RSK-003 │
 └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │ Automated Journal Posting (OD / ACH)
                            ▼
              ┌───────────────────────────┐
              │    SOLVENCY_PRESERVED     │ (BAM Overdraft Ceiling Enforced)
              └───────────────────────────┘
```

### 7.2 Deterministic Risk Matrix & Seed Governance

```
+-----------------------------------------------------------------------------------------------------------------------+
| RISK & RANDOM DISTRIBUTIONS SPECIFICATION                                                                             |
+-----------+-----------------------+-----------------------+-------------------+-----------------------+---------------+
| Event ID  | Risk Description      | Distribution / Model  | Probability / Int.| Financial Impact      | PRNG Seed     |
+-----------+-----------------------+-----------------------+-------------------+-----------------------+---------------+
| RSK-01    | Machine Breakdown     | Poisson (λ = 0.50/qtr)| ~15% per quarter  | 25k–65k MAD repair    | 42001         |
| RSK-02    | Paper Moisture Loss   | Bernoulli (p = 0.08)  | ~8% annual risk   | 31k–93k MAD scrap loss| 42002         |
| RSK-03    | Client Insolvency     | Beta (α = 2, β = 38)  | ~5% default risk  | 50k–250k MAD bad debt | 42003         |
| RSK-04    | Port Customs Delay    | Bernoulli (p = 0.12)  | ~12% of shipments | 1.05k–4.2k MAD demur. | 42004         |
| RSK-05    | BAM FX Currency Walk  | Gaussian (μ=10.74, σ) | Clamped [-5%, +5%]| Realized FX Gain/Loss | 42005         |
| RSK-06    | Law 69-21 Delays      | Deterministic rule    | Days > statutory  | BAM + 0.25% + 0.85%/m | 42006         |
| RSK-07    | 2026 SMIG Shock       | Step Function (+5.0%) | Effective 01/01/26| +156.62 MAD/m/worker  | 42007         |
+-----------+-----------------------+-----------------------+-------------------+-----------------------+---------------+
```
