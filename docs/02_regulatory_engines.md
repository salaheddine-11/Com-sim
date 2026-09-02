# SOUSS AGRI-PACK SARL — REGULATORY ENGINES & MATHEMATICAL MODELS
**Document ID**: `DOC-02-REG`  
**Version**: 1.0.0 (Phase 1 Formal Specification)  
**Target Period**: 2025-01-01 to 2026-12-31  
**Primary Legal Frameworks**: Code Général des Impôts (CGI 2025/2026), Lois de Finances (LF 2023 n° 50-22, LF 2024 n° 55-23, LF 2025 n° 60-24), Dahir CNSS 1972 (Dahir n° 1-72-184), Code du Travail (Loi n° 65-99), Loi n° 69-21 sur les délais de paiement, Code des Douanes ADII, Loi n° 47-06 sur la fiscalité locale, Circulaires Bank Al-Maghrib.

---

## 1. Executive Summary & Legal Hierarchy Framework

All fiscal, social, banking, customs, and municipal tax engines in the Souss Agri-Pack SARL simulation adhere strictly to authentic Moroccan positive law. In accordance with the **Primary Source Priority Rule**:
1. Every formula, threshold, rate, ceiling, and deadline is anchored in a verified Moroccan statutory article.
2. The simulation executes a continuous multi-year transition engine across **FY 2025 (Baseline)** and **FY 2026 (Full Convergence)**.
3. Every parameter entry establishes continuous, gap-free, overlap-free validity intervals $[d_{\text{start}}, d_{\text{end}}]$ over `[2025-01-01, 2026-12-31]`.

```
                    ┌────────────────────────────────────────────────────────┐
                    │               MOROCCAN STATUTORY HIERARCHY             │
                    ├────────────────────────────────────────────────────────┤
                    │ 1. Dahirs & National Codes (Loi 15-95, 65-99, 47-06)   │
                    │ 2. Code Général des Impôts (CGI 2025/2026)             │
                    │ 3. Annual Finance Acts (LF 2023, LF 2024, LF 2025)     │
                    │ 4. Executive Decrees & Ministerial Orders (SMIG, ANP)  │
                    │ 5. Bank Al-Maghrib Directives & ADII Customs Circulars │
                    └────────────────────────────────────────────────────────┘
```

---

## 2. Direct Corporate Taxation & Fiscal Reconciliation Engine

### 2.1 Corporate Income Tax (IS — Impôt sur les Sociétés)
- **Legal Base**: CGI Art. 19-I-A, as amended by Loi de Finances 2023 (Loi n° 50-22, Art. 6) implementing a 4-year linear convergence schedule (2023–2026).
- **Progressive Barème Method (*Barème progressif*)**: Under Moroccan tax law, IS is calculated using progressive marginal slices, wherein each slice of taxable profit (*Résultat Fiscal*) is taxed at its specific rate.

```
+--------------------------------------------------------------------------------------------------+
| MOROCCAN PROGRESSIVE IS BARÈME (CGI ART. 19-I-A)                                                 |
+------------------------------+---------------+---------------+-----------------------------------+
| Tranche de Résultat (MAD)    | FY 2025 Rate  | FY 2026 Rate  | Legal Source Citation             |
+------------------------------+---------------+---------------+-----------------------------------+
| 0 to 300,000                 | 17.50%        | 20.00%        | CGI Art. 19-I-A & LF 2023 Art. 6  |
| 300,001 to 1,000,000         | 20.00%        | 20.00%        | CGI Art. 19-I-A & LF 2023 Art. 6  |
| 1,000,001 to 100,000,000     | 22.75%        | 20.00%        | CGI Art. 19-I-A & LF 2023 Art. 6  |
| > 100,000,000                | 34.00%        | 35.00%        | CGI Art. 19-I-A & LF 2023 Art. 6  |
+------------------------------+---------------+---------------+-----------------------------------+
```

#### Piecewise Mathematical Computation:
For a taxable profit $R$:
$$\text{IS}_{\text{2025}}(R) = \begin{cases} 
R \times 0.1750 & \text{if } R \le 300,000 \\ 
(300,000 \times 0.1750) + (R - 300,000) \times 0.2000 & \text{if } 300,000 < R \le 1,000,000 \\ 
52,500 + 140,000 + (R - 1,000,000) \times 0.2275 & \text{if } 1,000,000 < R \le 100,000,000 
\end{cases}$$

$$\text{IS}_{\text{2026}}(R) = \begin{cases} 
R \times 0.2000 & \text{if } R \le 100,000,000 \\ 
20,000,000 + (R - 100,000,000) \times 0.3500 & \text{if } R > 100,000,000 
\end{cases}$$

#### Souss Agri-Pack Simulation Application ($R = \mathbf{530,000.00\text{ MAD}}$):
- **FY 2025 Baseline**:
  - Tranche 1 ($300,000 \times 17.50\%$): **52,500.00 MAD**
  - Tranche 2 ($230,000 \times 20.00\%$): **46,000.00 MAD**
  - **Total IS Dû (2025)**: $52,500 + 46,000 = \mathbf{98,500.00\text{ MAD}}$ (Effective rate: $18.585\%$).
- **FY 2026 Rate Convergence**:
  - Unified rate of $20.00\%$ applies across the entire base:
  - $\text{IS}_{\text{2026}} = 530,000 \times 20.00\% = \mathbf{106,000.00\text{ MAD}}$ ($\Delta = \mathbf{+7,500.00\text{ MAD}}$).

---

### 2.2 Cotisation Minimale (CM) & Fiscal Invariant
- **Legal Base**: CGI Art. 144-I.
- **Statutory Rate**: **0.25%** for industrial and commercial operations.
- **Tax Base ($B_{\text{CM}}$)**:
  $$B_{\text{CM}} = \text{CA HT (Compte 711/712)} + \text{Produits Accessoires (718)} + \text{Produits Financiers Imposables (738, excl. dividendes)} + \text{Subventions (716/719)}$$
- **Statutory Floor**: **3,000.00 MAD** minimum (CGI Art. 144-I-C).
- **Core Fiscal Invariant**:
  $$\text{IS Payable} = \max\left(\text{IS Théorique Barème}, \max(B_{\text{CM}} \times 0.0025, 3000.00)\right)$$

#### Souss Agri-Pack Calculation ($B_{\text{CM}} = \mathbf{10,930,700.00\text{ MAD}}$):
$$\text{CM} = 10,930,700.00 \times 0.0025 = \mathbf{27,326.75\text{ MAD}} \approx \mathbf{27,327.00\text{ MAD}}$$
$$\text{Activation Ratio} = \frac{\text{IS Théorique}}{\text{CM}} = \frac{98,500.00}{27,326.75} = \mathbf{3.6045\times} \quad (\ge 2.50\times \text{ mandatory})$$
$$\implies \mathbf{\text{Fiscal Invariant SATISFIED: The progressive barème is fully operative.}}$$

---

### 2.3 Acomptes Provisionnels & Year N+1 Regularization
- **Legal Base**: CGI Art. 170.
- **Installments Schedule**: 4 quarterly prepayments, each equal to $25\%$ of the prior year base IS:
  1. *1st Acompte*: Due on or before **March 31** ($98,500 \times 25\% = \mathbf{24,625.00\text{ MAD}}$).
  2. *2nd Acompte*: Due on or before **June 30** ($98,500 \times 25\% = \mathbf{24,625.00\text{ MAD}}$).
  3. *3rd Acompte*: Due on or before **September 30** ($98,500 \times 25\% = \mathbf{24,625.00\text{ MAD}}$).
  4. *4th Acompte*: Due on or before **December 31** ($98,500 \times 25\% = \mathbf{24,625.00\text{ MAD}}$).
- **Regularization at March 31 N+1**:
  $$\text{Reliquat d'IS} = \text{IS Définitif N} - \sum_{k=1}^4 \text{Acompte}_k$$
  - If $\text{IS Définitif} > \sum \text{Acomptes}$: Pay balance (*Reliquat*) by March 31 N+1 via SIMPL-IS.
  - If $\text{IS Définitif} < \sum \text{Acomptes}$: Credit excess against subsequent acomptes (Compte `34560000`).

---

### 2.4 Fiscal Reconciliation (*Tableau de Passage*) & Reintegrations
Under CGI Articles 11, 12, and 17, accounting profit is reconciled to taxable profit via statutory adjustments:

```
+--------------------------------------------------------------------------------------------------+
| TABLEAU DE PASSAGE DU RÉSULTAT COMPTABLE AU RÉSULTAT FISCAL (FY 2025)                            |
+---------------------------------------------------------------------------------+----------------+
| Description / Fiscal Element                                                    | Amount (MAD)   |
+---------------------------------------------------------------------------------+----------------+
| 1. Résultat Comptable Avant Impôt                                               | +495,700.00    |
|                                                                                 |                |
| 2. Réintégrations Fiscales (Charges non déductibles):                           |  +34,300.00    |
|    - Cadeaux publicitaires > 100 MAD TTC sans sigle apparent (CGI Art. 11-I)    |   +8,500.00    |
|    - Amendes, pénalités fiscales et infractions routières (CGI Art. 11-V)       |   +6,800.00    |
|    - Dépenses fournisseurs réglées en espèces > 5,000 MAD TTC (CGI Art. 11-II)  |   +9,000.00    |
|    - Amortissement excédentaire véhicule de tourisme > 300,000 MAD (Art. 11-III)|  +10,000.00    |
|                                                                                 |                |
| 3. Déductions Fiscales (Produits exonérés / non imposables):                    |          -0.00 |
|                                                                                 |                |
| 4. RÉSULTAT FISCAL IMPOSABLE                                                    | =530,000.00    |
+---------------------------------------------------------------------------------+----------------+
```

---

### 2.5 Dual-Sided Cash Ceiling Rules & Statutory Sanctions

```
+==================================================================================================+
|                              MOROCCAN CASH REGULATIONS & SANCTIONS                               |
+==================================================================================================+
|                                                                                                  |
|   PURCHASES CASH CEILINGS (CGI ART. 11-II & 106-II)   SALES CASH SANCTION (CGI ART. 193)         |
|  ┌─────────────────────────────────────────────────┐ ┌─────────────────────────────────────────┐ |
|  │ * Single Invoice Limit: 5,000.00 MAD TTC        │ │ * Cash Collection Limit: 20,000.00 MAD  │ |
|  │ * Monthly Supplier Limit: 50,000.00 MAD TTC     │ │ * Statutory Sanction: 6.00% on entire   │ |
|  │ * Penalty: Expense disallowed from IS (100%)    │ │   cash receipt                          │ |
|  │ * TVA Impact: Input TVA forfeited (100%)        │ │ * Accounting: Compte 65833000           │ |
|  │   (CGI Art. 106-II)                             │ │ * Tax Status: Strictly non-deductible   │ |
|  └─────────────────────────────────────────────────┘ └─────────────────────────────────────────┘ |
+==================================================================================================+
```

1. **Purchases Cash Ceiling (CGI Art. 11-II & 106-II)**:
   - Any expense exceeding **5,000.00 MAD TTC** per invoice, or **50,000.00 MAD TTC** per month to a single supplier, settled in cash:
     - Is **100% disallowed from IS deductions** (reintegrated in fiscal result).
     - Its **input TVA (*TVA récupérable*) is 100% non-recoverable** and cannot be deducted on SIMPL-TVA.
2. **Sales Cash Collection Sanction (CGI Art. 193)**:
   - Any commercial cash receipt from a client exceeding **20,000.00 MAD** triggers a statutory sanction of **6.00%** on the total cash collected.
   - The penalty is debited to Account `65833000` (*Sanctions pour encaissement espèces*) and is strictly **non-deductible for IS**.

---

## 3. Value Added Tax (TVA) Multi-Year Convergence Engine

- **Legal Base**: CGI Title III (Art. 87 to 130), as amended by Loi de Finances 2024 (Loi n° 55-23, Art. 6) establishing the 2-rate convergence reform (10% and 20% by 2026).
- **Declaration Regime**: Monthly electronic filing via **SIMPL-TVA** due on or before the **last calendar day of month M+1** (CGI Art. 110 & 155).

```
+--------------------------------------------------------------------------------------------------+
| TVA MULTI-YEAR CONVERGENCE SCHEDULE (LF 2024 / CGI 2025–2026)                                    |
+--------------------------------------+---------------+---------------+---------------------------+
| Category / Transaction Type          | FY 2025 Rate  | FY 2026 Rate  | Legal Source Citation     |
+--------------------------------------+---------------+---------------+---------------------------+
| Standard (Corrugated boxes, paper)   | 20.00%        | 20.00%        | CGI Art. 98               |
| ONEE Medium Voltage Electricity (MT) | 18.00%        | 20.00%        | LF 2024 Art. 6 / CGI 98   |
| Industrial Water & Assainissement    |  9.00%        | 10.00%        | LF 2024 Art. 6 / CGI 99-1 |
| Banking Operations & Credit Agios    | 10.00%        | 10.00%        | CGI Art. 99-3             |
| Road Freight & Transport of Goods    | 16.00%        | 20.00%        | LF 2024 Art. 6 / CGI 98   |
| Direct Exports of Finished Packaging |  0.00%        |  0.00%        | CGI Art. 92-I-1 (Droit déd)|
+--------------------------------------+---------------+---------------+---------------------------+
```

#### Monthly SIMPL-TVA Liquidation Equation:
$$\text{TVA Due}_M = \text{TVA Facturée}_M - \text{TVA Récupérable sur Charges}_M - \text{TVA Récupérable sur Immos}_M - \text{Crédit TVA}_{M-1}$$
- If $\text{TVA Due}_M > 0$: Book to Account `44560000` and pay by end of M+1.
- If $\text{TVA Due}_M < 0$: Carry forward as tax credit to Account `34550000` (*Crédit de TVA reportable*).

---

## 4. Personal Income Tax (IR) & Social Deductions Engine

- **Legal Base**: CGI Title II, amended by Loi de Finances 2025 (Loi n° 60-24, Art. 6) restructuring the progressive salary brackets, raising the tax-free allowance to 40,000 MAD, and expanding family deductions.
- **Reporting Schedule**: Monthly electronic declaration via **SIMPL-IR** due on or before the **last day of month M+1** (CGI Art. 78 & 155).

### 4.1 Annual Progressive IR Scale (Effective 2025-01-01)

```
+--------------------------------------------------------------------------------------------------+
| ANNUAL PROGRESSIVE IR SCALE (LF 2025 / CGI ART. 73-I)                                            |
+------------------------------+---------------+-------------------+-------------------------------+
| Annual Taxable Bracket (MAD) | Marginal Rate | Annual Deduction  | Monthly Equivalent (MAD)      |
+------------------------------+---------------+-------------------+-------------------------------+
| 0 to 40,000                  | 0.00%         | 0.00 MAD          | 0.00 to 3,333.33              |
| 40,001 to 60,000             | 10.00%        | 4,000.00 MAD      | 3,333.34 to 5,000.00          |
| 60,001 to 80,000             | 20.00%        | 10,000.00 MAD     | 5,000.01 to 6,666.67          |
| 80,001 to 100,000            | 30.00%        | 18,000.00 MAD     | 6,666.68 to 8,333.33          |
| 100,001 to 180,000           | 34.00%        | 22,000.00 MAD     | 8,333.34 to 15,000.00         |
| > 180,000                    | 37.00%        | 27,400.00 MAD     | > 15,000.00                   |
+------------------------------+---------------+-------------------+-------------------------------+
```

### 4.2 Net Taxable Salary (SNI) Derivation Pipeline
1. **Gross Taxable Salary (*Salaire Brut Imposable — SBI*)**:
   $$\text{SBI} = \text{Base Wage} + \text{Overtime} + \text{Taxable Bonuses} - \text{Exempt Allowances}$$
2. **Employee Social Contributions**:
   $$\text{Social Deductions} = \text{CNSS}_{\text{salariale}} (4.48\% \le 6\text{k}) + \text{AMO}_{\text{salariale}} (2.26\% \text{ uncapped})$$
3. **Professional Expenses Abatement (*Frais Professionnels* — CGI Art. 59-I-B)**:
   $$\text{Frais Pro Annual} = \begin{cases} 
   \text{SBI} \times 0.35 & \text{if } \text{SBI} \le 78,000\text{ MAD/yr} \\ 
   \min(\text{SBI} \times 0.25, 35000.00) & \text{if } \text{SBI} > 78,000\text{ MAD/yr} 
   \end{cases}$$
   $$\text{Monthly Abatement Ceiling} = \frac{35,000.00}{12} = \mathbf{2,916.67\text{ MAD/month}}$$
4. **Salaire Net Imposable (SNI)**:
   $$\text{SNI} = \text{SBI} - \text{CNSS}_{\text{sal}} - \text{AMO}_{\text{sal}} - \min(\text{Frais Pro}, 2916.67)$$
5. **Gross Monthly IR**:
   $$\text{IR Brut} = (\text{SNI} \times \text{Marginal Rate}) - \text{Somme à Déduire Mensuelle}$$
6. **Family Deductions (*Charges de Famille* — CGI Art. 74-II / LF 2025)**:
   $$\text{Family Tax Credit} = \min(\text{Dependents}, 6) \times 41.67\text{ MAD/month} \quad (\text{Max } 250.00\text{ MAD/month})$$
7. **Net Monthly IR Withheld**:
   $$\text{IR Net} = \max\left(0, \text{IR Brut} - \text{Family Tax Credit}\right)$$

---

## 5. Dividend Withholding Tax & The Vintage Partition Rule

- **Legal Base**: CGI Art. 73-II-C-1 and Transitional Article 247-XLIV (LF 2023).
- **Withholding Glide Schedule**:
  - Profits realized in FY 2025: **11.25%**
  - Profits realized in FY 2026: **10.00%**
- **The Vintage Rule (*Règle du Millésime*)**:
  - Dividends paid from **pre-2023 retained earnings (*Report à nouveau anté-2023*)** are subject to a statutory locked rate of **15.00%**.
  - Dividends paid from **2023+ earnings** benefit from the reduced glide rate (11.25% in 2025 / 10.00% in 2026).
  - In `config/opening_balance_sheet.yaml`, Account `1191` (or `1161`) is explicitly partitioned into:
    - `11611000` (Pre-2023 Retained Earnings): **2,150,000.00 MAD** (taxed at 15.00%).
    - `11612000` (Post-2023 Retained Earnings): **1,678,700.00 MAD** (taxed at 11.25%/10.00%).

---

## 6. Social Security (CNSS) & Labour Legislation

### 6.1 Statutory Minimum Wage (SMIG) Revaluation
- **Legal Base**: Code du Travail (Loi n° 65-99 Art. 356) and Social Dialogue Decrees.
- **Working Hours Standard**: 191.00 hours per month ($2,288\text{ hours/year}$).
- **SMIG Dynamics**:
  - **FY 2025 (as of 2025-01-01)**: $17.10\text{ MAD/hour} \implies \mathbf{3,266.10\text{ MAD/month}}$.
  - **FY 2026 (as of 2026-01-01, +5.00% shock)**: $17.92\text{ MAD/hour} \implies \mathbf{3,422.72\text{ MAD/month}}$ ($+156.62\text{ MAD/month/worker}$).

### 6.2 CNSS & Workplace Accident Contribution Matrix

```
+--------------------------------------------------------------------------------------------------+
| CNSS & SOCIAL CHARGES CONTRIBUTION MATRIX (DAHIR 1972 & LOI 65-00)                               |
+--------------------------------------+---------------+---------------+---------------------------+
| Contribution Element                 | Employer %    | Employee %    | Assessment Base Ceiling   |
+--------------------------------------+---------------+---------------+---------------------------+
| Prestations Sociales (Court & Long)  |  8.98%        |  4.48%        | Capped at 6,000.00 MAD/mo |
| Allocations Familiales               |  6.40%        |   —           | Uncapped (Total Gross)    |
| Taxe de Formation Pro (OFPPT)        |  1.60%        |   —           | Uncapped (Total Gross)    |
| Assurance Maladie Obligatoire (AMO)  |  2.26%        |  2.26%        | Uncapped (Total Gross)    |
| Participation Solidarité AMO         |  1.85%        |   —           | Uncapped (Total Gross)    |
+--------------------------------------+---------------+---------------+---------------------------+
| TOTAL CNSS / AMO                     | 21.09% nom.   |  6.74% nom.   | Composite                 |
+--------------------------------------+---------------+---------------+---------------------------+
| Workplace Accident Insurance (AT)    | ~3.80%        |   —           | Uncapped (Private Policy) |
+--------------------------------------+---------------+---------------+---------------------------+
```

- **Monthly Capped Amounts (6,000 MAD ceiling)**:
  - Max Employer Prestations Sociales: $6,000.00 \times 8.98\% = \mathbf{538.80\text{ MAD/employee/month}}$.
  - Max Employee Prestations Sociales: $6,000.00 \times 4.48\% = \mathbf{268.80\text{ MAD/employee/month}}$.

#### Labour Line P&L Reconciliation Invariant:
$$\text{Total Gross Wages (61711)} + \text{CNSS Patronale (61741)} + \text{AT Insurance (61743)} = 2,089,586.00 + 411,010.00 + 79,404.00 = \mathbf{2,580,000.00\text{ MAD}}$$
$$\implies \mathbf{\text{Exact 0.00 MAD delta with P&L Labour Line.}}$$

---

## 7. Customs Administration (ADII) & Port of Agadir Logistics

### 7.1 Customs Tariff Engine (ADII Chapter 48)
- **EU Preferential Origin (Morocco-EU Association Agreement / Dahir n° 1-00-175)**:
  - Proof of Origin: Valid **EUR.1 Movement Certificate** or Invoice Declaration of Origin.
  - **Droit d'Importation (DI)**: **0.00%**.
- **Non-EU / MFN Customs Tariff (Chapter 48 — Papiers & Cartons)**:
  - Kraftliner (HS 4804): **10.00% DI**
  - Fluting & Recycled Medium (HS 4805): **2.50% DI**
  - Corrugated Board & Boxes (HS 4819): **25.00% DI**
- **Taxe Parafiscale à l'Importation (TPI — Loi 43-06)**: **0.25%** on CIF value.
- **Import TVA (CGI Art. 121/122)**: **20.00%** on $(\text{CIF Value} + \text{DI} + \text{TPI})$.

#### Customs Import Liquidation Equation:
$$\text{Total DUM} = \text{DI} + \text{TPI} + \text{TVA Import} = (\text{CIF} \times \text{Rate}_{\text{DI}}) + (\text{CIF} \times 0.0025) + \left[(\text{CIF} + \text{DI} + \text{TPI}) \times 0.20\right]$$

### 7.2 Port of Agadir Surestaries (Demurrage Scale)
- **Legal Base**: ANP / Marsa Maroc Port of Agadir Commercial Container Tariffs.
- **Demurrage Tiering (20ft/40ft Dry Container)**:

```
+--------------------------------------------------------------------------------------------------+
| PORT OF AGADIR SURESTARIES & DEMURRAGE SCALE                                                     |
+------------------------------+---------------------------+---------------------------------------+
| Dwell Time (Days in Port)    | Daily Rate (MAD/day)      | Cumulative Demurrage at Tier End      |
+------------------------------+---------------------------+---------------------------------------+
| Days 1 to 7 (Franchise)      | 0.00 MAD                  | 0.00 MAD                              |
| Days 8 to 14 (Tier 1)        | 150.00 MAD                | 1,050.00 MAD                          |
| Days 15 to 21 (Tier 2)       | 300.00 MAD                | 3,150.00 MAD                          |
| Day 22 and above (Tier 3)    | 500.00 MAD                | 3,150.00 + (Days - 21) * 500.00 MAD   |
+------------------------------+---------------------------+---------------------------------------+
```

---

## 8. Central Banking, Credit Pricing & Law 69-21

### 8.1 Bank Al-Maghrib (BAM) Key Rate & Commercial Paper Discounting
- **BAM Key Interest Rate (*Taux Directeur*)**: **2.75% p.a.** (stable through 2026).
- **Commercial Paper Discounting Agio Formula**:
  $$\text{Discount Interest HT} = \frac{\text{Nominal} \times (\text{BAM Rate} + \text{Spread}) \times (\text{Days} + 1)}{360}$$
  $$\text{Endorsement Commission} = \text{Nominal} \times 0.0010 \quad (0.10\%)$$
  $$\text{Total Agio HT} = \text{Discount Interest HT} + \text{Endorsement Commission} + \text{Bordereau Fee (50 MAD)}$$
  $$\text{TVA sur Agios (10\%)} = \text{Total Agio HT} \times 0.1000 \quad (\text{CGI Art. 99-3})$$
  $$\text{Net Cash Credited} = \text{Nominal} - (\text{Total Agio HT} \times 1.10)$$

### 8.2 Law 69-21 on Payment Delays (Délais de Paiement)
- **Legal Base**: Loi n° 69-21 modifiant la Loi n° 15-95 formant Code de Commerce (Dahir n° 1-23-45).
- **Enterprise Turnover Tier**: Medium Tier (**10,000,000 to 50,000,000 MAD CA HT**). Quarterly electronic declarations via DGI SIMPL-Délais.
- **Statutory Terms**: 60 calendar days from invoice date (contractual maximum 120 days).
- **Late Payment Penalty Fine Scale (Art. 78-3)**:
  - Month 1 of Delay: $\text{Rate} = \text{BAM Key Rate } (2.75\%) + 0.25\% = \mathbf{3.00\%}$.
  - Each Additional Month (or fraction): Additional **+0.85%** per month.
  $$\text{Fine Rate}(M) = 3.00\% + (M - 1) \times 0.85\% \quad \text{for } M \ge 1 \text{ months}$$
  $$\text{Amende DGI} = \text{Invoice TTC} \times \text{Fine Rate}(M)$$
  - *Tax Status*: 100% non-deductible tax fine, booked to Account `65832000`.

### 8.3 FX Clamped Random Walk Engine
- **Legal Base**: Bank Al-Maghrib Notice n° 01/2020 ($\pm 5.00\%$ currency basket fluctuation band).
- **Basket Composition**: 60% EUR, 40% USD.
- **Bounds**:
  - **EUR/MAD**: Central Parity = **10.7400 MAD**; Bounds = **[10.2030, 11.2770 MAD]** ($\sigma = 0.008$).
  - **USD/MAD**: Central Parity = **9.3000 MAD**; Bounds = **[8.8350, 9.7650 MAD]** ($\sigma = 0.012$).

---

## 9. Local Direct Taxation & Communal Levies (Loi 47-06)

### 9.1 Taxe Professionnelle (TP)
- **Legal Base**: Loi n° 47-06 relative à la fiscalité des collectivités locales (Art. 6 to 11).
- **5-Year Initial Exemption Expiry (Art. 6-II-1°)**:
  - Souss Agri-Pack SARL established in 2020 $\implies$ Creation holiday covered 2020, 2021, 2022, 2023, and 2024.
  - **First Taxable Fiscal Year = FY 2025**.
- **Rental Value Base (*Valeur Locative — VL*, Art. 7)**:
  $$\text{VL} = 3.00\% \times (\text{Gross Acquisition Cost of Land, Buildings & Equipment})$$
  $$\text{Gross Assets Base} = 800,000 (\text{Land}) + 2,200,000 (\text{Building}) + 4,400,000 (\text{Machinery}) = \mathbf{7,400,000.00\text{ MAD}}$$
  $$\text{VL} = 7,400,000.00 \times 0.0300 = \mathbf{222,000.00\text{ MAD}}$$
- **Taxe Professionnelle Rate (Class 2 Industrial)**: **10.00%**.
  $$\text{Annual TP Due} = 222,000.00 \times 10.00\% = \mathbf{22,200.00\text{ MAD}}$$

### 9.2 Taxe de Services Communaux (TSC)
- **Legal Base**: Loi n° 47-06 (Art. 32 to 39).
- **Tax Base**: Identical Valeur Locative ($\text{VL} = 222,000.00\text{ MAD}$).
- **Rate**: **10.50%** (Urban zone of Ait Melloul / Commune Urbaine).
  $$\text{Annual TSC Due} = 222,000.00 \times 10.50\% = \mathbf{23,310.00\text{ MAD}}$$
- **Combined Municipal Tax Burden**:
  $$\text{Total Local Taxes} = \text{TP } (22,200) + \text{TSC } (23,310) = \mathbf{45,510.00\text{ MAD}} \quad (\text{VL} \times 20.50\%)$$
  - Due Date: Annually on or before **June 30**. Booked to Account `61611000` / `61612000`.
