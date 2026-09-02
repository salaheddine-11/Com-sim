# SOUSS AGRI-PACK SARL — WORLD ARCHITECTURE & SYSTEM DESIGN
**Document ID**: `DOC-01-ARCH`  
**Version**: 1.0.0 (Phase 1 Formal Specification)  
**Target Entity**: Souss Agri-Pack SARL  
**Location**: Zone Industrielle Ait Melloul, Agadir, Souss-Massa, Kingdom of Morocco  
**Statutory Baselines**: Code de Commerce Marocain (Loi 15-95), Code Général des Impôts (CGI 2025/2026), Lois de Finances 2023–2025, Dahir CNSS 1972, Plan Comptable Marocain (PCM / CGNC), Administration des Douanes et Impôts Indirects (ADII).

---

## 1. Executive Summary & World Topology

**Souss Agri-Pack SARL** is an industrial packaging manufacturing enterprise located in the heart of Morocco's primary agricultural export basin (Souss-Massa). The company operates a dedicated converting facility in the Zone Industrielle of Ait Melloul (Agadir prefecture), transforming virgin and recycled paper reels into specialized corrugated boxes, open-top trays, telescopic export containers, and high-precision punnets.

The enterprise serves as a critical supply chain node for Moroccan agricultural exporters shipping citrus (*Clementines*, *Maroc Late*), round and cluster tomatoes, avocados, and red berries to European Union and United Kingdom markets, as well as supplying domestic modern distribution networks (GMS) and local agro-food processors.

```
+==================================================================================================+
|                                  SOUSS AGRI-PACK SIMULATION GRAPH                                |
+==================================================================================================+
|                                                                                                  |
|   UPSTREAM SUPPLY ECOSYSTEM                     CONVERTING ENTERPRISE      COMMERCIAL CLIENTS    |
|  ┌─────────────────────────┐                   ┌───────────────────────┐  ┌────────────────────┐ |
|  │ Domestic Paper Mills    │────Reels (MAD)───►│                       │─►│ Agri-Exporters 42% │ |
|  │ (GPC, CMCP-IP Kenitra)  │                   │  SOUSS AGRI-PACK      │  │ (Citrus/Tomatoes)  │ |
|  └─────────────────────────┘                   │  SARL (Ait Melloul)   │  └────────────────────┘ |
|  ┌─────────────────────────┐                   │                       │  ┌────────────────────┐ |
|  │ EU Paper Mills (EUR.1)  │────CIF Agadir────►│  * Capital: 800k MAD  │─►│ Modern Retail 26%  │ |
|  │ (Spain, Portugal, Nord) │                   │  * Capacity: 2.4M m2  │  │ (Marjane, Carref.) │ |
|  └─────────────────────────┘                   │  * FY25 CA: 10.93M MAD│  └────────────────────┘ |
|  ┌─────────────────────────┐                   │  * Headcount: 22P+5S  │  ┌────────────────────┐ |
|  │ Auxiliaries & Utilities │──Starch, Glue,───►│  * Load Factor: 79.2% │─►│ Souk Wholesale 12% │ |
|  │ (ONEE MT, Inks, Starch) │   Electricity     │                       │  │ (Inzegane/Local)   │ |
|  └─────────────────────────┘                   └───────────┬───────────┘  └────────────────────┘ |
|                                                            │              ┌────────────────────┐ |
|   REGULATORY & FINANCIAL AGENTS                            │              │ Agro-Indus. 10%    │ |
|  ┌─────────────────────────────────────────────────────────┴───────────┐  │ (Canning/Oils)     │ |
|  │ * Direction Générale des Impôts (DGI): IS Barème, CM 0.25%, TVA 20% │  └────────────────────┘ |
|  │ * Caisse Nationale de Sécurité Sociale (CNSS): 21.09% Pat / 6.74% Sal│  ┌────────────────────┐ |
|  │ * Bank Al-Maghrib (BAM): Taux 2.75%, Clamped FX (+/-5%), Law 69-21   │─►│ Direct EU Exp. 6% │ |
|  │ * Port d'Agadir (ANP/Marsa Maroc): Surestaries Tiers (150/300/500)  │  │ (EUR.1 / 0% TVA)   │ |
|  │ * Banking Partners: Attijariwafa (AWB), CAM, BCP, BMCE (2.5M Lines) │  └────────────────────┘ |
|  └─────────────────────────────────────────────────────────────────────┘  ┌────────────────────┐ |
|                                                                           │ Cooperatives 4%    │ |
|                                                                           │ (COPAG, etc.)      │ |
|                                                                           └────────────────────┘ |
+==================================================================================================+
```

---

## 2. Core Enterprise Master & Corporate Governance

### 2.1 Corporate Identity & Statutory Registration
The simulated enterprise possesses structurally valid, authentic-format Moroccan identification numbers, establishing complete legal standing across all regulatory registries:

```yaml
corporate_profile:
  entity_id: "ENT-SOUSS-001"
  corporate_name: "Souss Agri-Pack SARL"
  legal_form: "Société à Responsabilité Limitée (SARL)"
  creation_date: "2020-01-02"
  headquarters_address: "Lot 142-144, Zone Industrielle Ait Melloul, 80150 Agadir, Maroc"
  share_capital_mad: 800000.00
  nominal_share_value_mad: 100.00
  total_shares_count: 8000
  ice: "002345678000091"           # 15 digits (Identifiant Commun de l'Entreprise)
  identifiant_fiscal: "45127890"    # 8 digits (DGI IF)
  registre_commerce: "28451"        # Tribunal de Commerce d'Agadir
  taxe_professionnelle: "30145280"  # Direction Régionale des Impôts Agadir
  cnss_affiliation: "9127456"       # Caisse Nationale de Sécurité Sociale
  tribunal_competent: "Tribunal de Commerce d'Agadir"
```

### 2.2 Shareholding Structure & Corporate Governance
Souss Agri-Pack SARL is organized under the Moroccan Company Act (Loi n° 5-96 sur la SARL, complétée par la Loi n° 15-95 formant Code de Commerce). The equity capital is distributed among three founding partners:

```
+--------------------------------------------------------------------------------------------------+
| SHAREHOLDING & GOVERNANCE ROSTER                                                                 |
+--------------------------+-----------------------+---------------+-----------------+-------------+
| Shareholder Name         | Corporate Function    | Shares Held   | Capital (MAD)   | Equity %    |
+--------------------------+-----------------------+---------------+-----------------+-------------+
| M. Youssef Bennani       | Gérant Associé Maj.   | 4,800 parts   | 480,000.00 MAD  | 60.00%      |
| Mme Fatima Zahra Amri    | DAF / Associée        | 2,000 parts   | 200,000.00 MAD  | 25.00%      |
| M. Hassan Oulhaj         | Dir. Commercial/Assoc.| 1,200 parts   | 120,000.00 MAD  | 15.00%      |
+--------------------------+-----------------------+---------------+-----------------+-------------+
| TOTAL                    |                       | 8,000 parts   | 800,000.00 MAD  | 100.00%     |
+--------------------------+-----------------------+---------------+-----------------+-------------+
```

### 2.3 Legal Liability Framework of the Managing Director (*Gérant Associé Majoritaire*)
Under Moroccan commercial and tax law, M. Youssef Bennani exercises statutory executive authority as *Gérant Associé Majoritaire*. While a SARL affords limited liability (*responsabilité limitée aux apports*) for ordinary commercial contingencies, positive Moroccan law imposes **strict personal and joint liability** (*responsabilité solidaire et personnelle*) on the statutory manager in three specific legal realms:

1. **Fiscal Infractions & Tax Fraud (CGI Art. 182)**:
   Under Article 182 of the Code Général des Impôts, when tax debts (IS, TVA, IR retenu à la source) cannot be recovered from corporate assets due to fraudulent maneuvers, organized insolvency, or grave intentional breaches of fiscal reporting obligations, the Gérant is held personally and solidarily liable on personal assets for all taxes, fines, surcharges, and collection penalties.
2. **Social Security Non-Remittance (Dahir CNSS 1972)**:
   Pursuant to Dahir portant loi n° 1-72-184 (Art. 28), employee social contributions deducted at source from salaries constitute trust funds. Failure to remit withheld employee CNSS and AMO contributions to the CNSS within statutory deadlines engages the direct criminal and civil personal liability of the Managing Director.
3. **Insolvency & Gross Management Faults (*Comblement de Passif* — Loi 15-95)**:
   Under Articles 704 to 706 of the Code de Commerce (Loi n° 15-95), in the event of judicial restructuring or liquidation (*redressement ou liquidation judiciaire*), if an asset deficiency is proven, the commercial court may order the Managing Director to personally settle all or part of the company’s debts (*action en comblement de passif*) if gross management negligence, fraudulent diversion of company funds, or improper personal use of company credit is established.

---

## 3. Physical Converting Plant Architecture & Technical Assets

### 3.1 Industrial Site Layout & Production Capacity
- **Location**: Industrial Zone of Ait Melloul (Agadir industrial corridor), offering immediate logistics access to the N1 highway (Taroudant/Tiznit/Chtouka export belts) and the Port of Agadir (22 km).
- **Physical Site**: Industrial plot of 2,000 m² featuring a 1,400 m² covered production and warehousing floor and 200 m² administrative offices.
- **Converting Capacity**: **2,400,000 m² per year** based on a single 8-hour shift (250 operational days) plus seasonal high-demand overtime on downstream die-cutters.
- **FY 2025 Volume Target**: **1,900,000 m² per year** ($\approx 79.17\%$ nominal capacity utilization / load factor).
- **FY 2026 Volume Projection**: **1,976,000 m² per year** ($+4.0\%$ volume growth $\implies 82.33\%$ load factor).

### 3.2 Fixed Assets Register & Depreciation Schedule
The physical plant comprises 8 primary asset lots acquired between 2020 and 2022, depreciated under the linear method (*Amortissement linéaire*) pursuant to CGI Article 10:

```
+-------------------------------------------------------------------------------------------------------------------------+
| FIXED ASSETS & MACHINERY REGISTER (01/01/2025)                                                                          |
+----------+---------------------------------+------------+---------------+---------+--------+--------------+-------------+
| Asset ID | Description & Machine Type      | Acq. Date  | Gross (MAD)   | Life    | Rate   | Cumul. Amort | Net VNA     |
+----------+---------------------------------+------------+---------------+---------+--------+--------------+-------------+
| IMM-2111 | Frais de constitution SARL      | 2020-01-02 |     50,000.00 |  5 yrs  | 20.00% |    50,000.00 |        0.00 |
| IMM-2311 | Terrain industriel (2,000 m2)   | 2020-01-15 |    800,000.00 |    —    |    —   |         0.00 |  800,000.00 |
| IMM-2321 | Bâtiment usine & bureaux        | 2020-06-01 |  2,200,000.00 | 20 yrs  |  5.00% |   495,000.00 |1,705,000.00 |
| IMM-2332A| Onduleuse & Combiné Flexo L1    | 2020-03-10 |  3,500,000.00 | 10 yrs  | 10.00% | 1,680,000.00 |1,820,000.00 |
| IMM-2332B| Combiné Flexo L2 & Découpeuse   | 2022-06-15 |    900,000.00 | 10 yrs  | 10.00% |   225,000.00 |  675,000.00 |
| IMM-2340 | Chariots élévateurs & Camion PL | 2020-04-01 |    450,000.00 |  5 yrs  | 20.00% |   427,500.00 |   22,500.00 |
| IMM-2351 | Mobilier & agencements bureaux  | 2020-02-01 |    120,000.00 | 10 yrs  | 10.00% |    58,800.00 |   61,200.00 |
| IMM-2352 | Matériel informatique & serveurs| 2021-09-01 |    180,000.00 | 3.33 yrs| 30.00% |   180,000.00 |        0.00 |
| IMM-2481 | Dépôts & cautionnements ONEE/Bail| 2020-01-10|     45,000.00 |    —    |    —   |         0.00 |   45,000.00 |
+----------+---------------------------------+------------+---------------+---------+--------+--------------+-------------+
| TOTAL    | Gross Fixed Assets              |            |  8,245,000.00 |         |        | 3,116,300.00 |5,128,700.00 |
+----------+---------------------------------+------------+---------------+---------+--------+--------------+-------------+
```

---

## 4. Closed Costing Chain & Bill of Materials (BOM) Model

### 4.1 Physical Corrugated Board Architecture
Souss Agri-Pack manufactures heavy-duty C-flute single-wall corrugated cardboard engineered for humid agricultural cold-chain environments:
1. **Outer Liner (Couverture extérieure)**: High-performance virgin Kraftliner ($150\text{ g/m}^2$), providing humidity barrier properties, burst strength, and clean flexographic printability.
2. **Fluting Medium (Cannelure C)**: Semi-chemical or high-strength recycled fluting ($120\text{ g/m}^2$). The physical fluting corrugation introduces a standard take-up factor (*coefficient d'ondulation*) of $k = 1.4800$:
   $$\text{Fluting Paper Consumed} = 120.00\text{ g/m}^2 \times 1.4800 = \mathbf{177.60\text{ g/m}^2}$$
3. **Inner Liner (Couverture intérieure)**: Recycled Testliner 2 ($150\text{ g/m}^2$), delivering stacking stiffness and box compression resistance (BCT).

$$\text{Total Paper Grammage per m}^2 = 150.00 + 177.60 + 150.00 = \mathbf{477.60\text{ g/m}^2} = \mathbf{0.4776\text{ kg/m}^2}$$

### 4.2 Blended Raw Paper Procurement Cost
Raw paper reels are sourced domestically from Moroccan mills (GPC Kenitra/Agadir, CMCP-IP) and imported from the European Union (Spain, Portugal, Scandinavia) at an average delivered net price:
$$P_{\text{paper}} = \mathbf{6.2000\text{ MAD/kg (net of TVA)}}$$
$$\text{Net Paper Cost per m}^2 (C_{\text{paper}}) = 0.4776\text{ kg/m}^2 \times 6.2000\text{ MAD/kg} = \mathbf{2.9574\text{ MAD/m}^2}$$

### 4.3 Industrial Auxiliaries & Consumables
Box conversion consumes industrial chemical inputs:
- **Modified Starch Glue (Amidon industriel)**: $25\text{ g/m}^2$ dry basis + borax/caustic soda = **0.0800 MAD/m²**.
- **Flexographic Inks (Encres à l'eau)**: Water-based pigments (1 to 3 colors) = **0.0400 MAD/m²**.
- **Stitching Wire & Strapping (Fil d'agrafage & Feuillard PP)**: Fastening materials = **0.0150 MAD/m²**.
- **Palletizing Wrap & Edge Protectors (Film étirable & Cornières)**: Packing consumables = **0.0150 MAD/m²**.
$$\text{Total Auxiliaries Cost } (C_{\text{aux}}) = 0.0800 + 0.0400 + 0.0150 + 0.0150 = \mathbf{0.1500\text{ MAD/m}^2}$$

### 4.4 Technical Scrap & Gross Material Cost Reconciliation
Industrial converting incurs inevitable physical scrap (edge trims 3.5%, die-cut slots 3.0%, machine setups 1.0%, misprints 0.5% $\implies \sigma = \mathbf{8.00\%}$):
$$\text{Net Direct Material Cost } (C_{\text{mat, net}}) = C_{\text{paper}} + C_{\text{aux}} = 2.9574 + 0.1500 = \mathbf{3.1074\text{ MAD/m}^2}$$
$$\text{Gross Direct Material Required } (C_{\text{mat, gross}}) = \frac{C_{\text{mat, net}}}{1 - \sigma} = \frac{3.1074}{1 - 0.08} = \frac{3.1074}{0.92} = \mathbf{3.3776\text{ MAD/m}^2} \approx \mathbf{3.377\text{ MAD/m}^2}$$

#### Scrap Sale Recovery Policy:
- Cuttings generated per net m²: $0.4776 \times (0.08 / 0.92) = 0.04153\text{ kg/m}^2$.
- Reclaimed scrap is baled and sold to local pulpers at **0.8000 MAD/kg**, generating **0.0332 MAD/m²** in revenue credited to Account `71271000` (*Ventes de déchets et rebuts*).

---

## 5. Commercial Client Ecosystem & SKU Product Catalog

### 5.1 Six Market Segments
The commercial sales portfolio is distributed across 6 client segments in Southern Morocco:

```
+--------------------------------------------------------------------------------------------------+
| COMMERCIAL CLIENT SEGMENTS BREAKDOWN                                                             |
+--------------------------+-----------+----------+-------------+------------------+---------------+
| Segment Code / Name      | Share %   | Vol (m2) | Avg DSO     | Payment Method   | TVA Regime    |
+--------------------------+-----------+----------+-------------+------------------+---------------+
| AGRI_EXPORTER            | 42.0%     | 798,000  | 90 days     | LCN Traite       | Standard 20%  |
| MODERN_RETAIL (GMS)      | 26.0%     | 494,000  | 90-120 days | Virement bancaire| Standard 20%  |
| SOUK_WHOLESALE           | 12.0%     | 228,000  | 30 days     | Chèque / Traite  | Standard 20%  |
| AGRO_INDUSTRIAL          | 10.0%     | 190,000  | 60 days     | LCN Traite       | Standard 20%  |
| DIRECT_EU_EXPORT         |  6.0%     | 114,000  | 60 days     | Virement SWIFT   | 0% Art 92     |
| COOPERATIVE              |  4.0%     |  76,000  | 60 days     | LCN / Virement   | Standard 20%  |
+--------------------------+-----------+----------+-------------+------------------+---------------+
| TOTAL                    | 100.0%    |1,900,000 | ~90 days    | Composite        |               |
+--------------------------+-----------+----------+-------------+------------------+---------------+
```

### 5.2 Product Catalog & SKU Matrix
The company manufactures 5 standardized packaging SKUs priced proportionally to board surface and converting complexity:

```
+----------------------------------------------------------------------------------------------------+
| PRODUCT CATALOG & SKU PRICING MATRIX (FY 2025)                                                     |
+------+-----------------------+-----------+---------+-----------+-----------+------------+----------+
| SKU  | Description           | Crop/Use  | Surface | Compl. Ki | Share %   | Price / m2 | Unit MAD |
+------+-----------------------+-----------+---------+-----------+-----------+------------+----------+
| P001 | Plateau Agrumes 10kg  | Citrus    | 0.850 m2| 1.00 (2C) | 40.0%     | 5.5000 MAD | 4.6750   |
| P002 | Caisse Tomate Exp 6kg | Tomatoes  | 0.720 m2| 1.08 (Vent| 28.0%     | 5.8000 MAD | 4.1760   |
| P003 | Plateau Avocat Exp 4kg| Avocados  | 0.650 m2| 1.18 (3C) | 14.0%     | 6.2000 MAD | 4.0300   |
| P004 | Master Fruits Rouges  | Berries   | 0.520 m2| 1.12 (Die)| 10.0%     | 6.0000 MAD | 3.1200   |
| P005 | Caisse Américaine RSC | Agro-Ind. | 1.150 m2| 0.95 (RSC)|  8.0%     | 5.7625 MAD | 6.6269   |
+------+-----------------------+-----------+---------+-----------+-----------+------------+----------+
| TOTAL| Consolidated Catalog  | Souss Bas.| —       | —         | 100.0%    | 5.7530 MAD | —        |
+------+-----------------------+-----------+---------+-----------+-----------+------------+----------+
```

#### Revenue & Pricing Mathematical Identity:
$$\bar{P} = (0.40 \times 5.5000) + (0.28 \times 5.8000) + (0.14 \times 6.2000) + (0.10 \times 6.0000) + (0.08 \times 5.7625) = \mathbf{5.7530\text{ MAD/m}^2}$$
$$\text{Target Turnover (CA HT)} = 1,900,000\text{ m}^2 \times 5.7530\text{ MAD/m}^2 = \mathbf{10,930,700.00\text{ MAD HT}}$$
$$\text{Gross Margin Multiplier} = \frac{5.7530}{3.1074} = \mathbf{1.8514\times \approx 1.85\times \text{ Net Material Cost}}$$

---

## 6. Supply Chain Topology & Inbound Logistics

```
+==================================================================================================+
|                                    INBOUND LOGISTICS FLOWCHART                                   |
+==================================================================================================+
|                                                                                                  |
|  DOMESTIC PROCUREMENT                       EU IMPORTATION (SPAIN / PORTUGAL)                    |
|  ┌───────────────────────┐                  ┌───────────────────────────────────────────────┐    |
|  │ Moroccan Mills (GPC)  │                  │ Maritime Freight Container (CIF Port Agadir)  │    |
|  └──────────┬────────────┘                  └───────────────────────┬───────────────────────┘    |
|             │ Truck Transport (N1)                                  │ Port Discharge             |
|             ▼                                                       ▼                            |
|  ┌───────────────────────┐                  ┌───────────────────────────────────────────────┐    |
|  │ Factory Ingress Gate  │                  │ Port of Agadir Terminal (ANP / Marsa Maroc)   │    |
|  │ (Ait Melloul)         │                  │ * Free Dwell: Days 1-7 (0 MAD)                │    |
|  └──────────┬────────────┘                  │ * Surestaries T1: Days 8-14 (150 MAD/day)     │    |
|             │                               │ * Surestaries T2: Days 15-21 (300 MAD/day)    │    |
|             │                               │ * Surestaries T3: Day 22+ (500 MAD/day)       │    |
|             │                               └───────────────────────┬───────────────────────┘    |
|             │                                                       │ Customs Clearance (DUM)    |
|             │                                                       │ * EUR.1 Origin: 0% DI      |
|             │                                                       │ * TPI: 0.25% CIF           |
|             │                                                       │ * TVA Import: 20%          |
|             │                                                       ▼                            |
|             │                               ┌───────────────────────────────────────────────┐    |
|             │                               │ Port Transit Forwarder Trucking (22 km)       │    |
|             │                               └───────────────────────┬───────────────────────┘    |
|             │                                                       │                            |
|             └───────────────────────┬───────────────────────────────┘                            |
|                                     │                                                            |
|                                     ▼                                                            |
|                         ┌───────────────────────┐                                                |
|                         │ Quality Inbound Check │ (Moisture limit <= 8.5%, Burst ECT/BCT)        |
|                         └───────────┬───────────┘                                                |
|                                     │ Pass                                                       |
|                                     ▼                                                            |
|                         ┌───────────────────────┐                                                |
|                         │ Raw Reel Warehouse    │ (CUMP Valuation Policy / 45-day safety buffer)  |
|                         └───────────────────────┘                                                |
+==================================================================================================+
```

---

## 7. Working Capital & Bank Credit Facilities

### 7.1 Operating Working Capital (BFR) Profile
- **Receivables (Compte 3421)**: DSO $\approx 90$ days across customer mix $\implies 2,732,675\text{ MAD HT}$ ($3,279,210\text{ MAD TTC}$).
- **Inventory (Comptes 3111/3151)**: Raw materials 45 days ($737,500\text{ MAD}$) + Finished goods 15 days ($424,583\text{ MAD}$) $\implies 1,162,083\text{ MAD}$.
- **Payables (Compte 4411)**: Supplier DPO $\approx 70$ days on paper/consumables $\implies 1,250,000\text{ MAD}$.
- **Average BFR**: $3,279,210 + 1,162,083 - 1,250,000 \approx \mathbf{3,191,293\text{ MAD}}$.
- **Peak High-Season BFR (Dec–Feb)**: Multiplier $1.45\times \implies \mathbf{3,520,000\text{ MAD}}$.

### 7.2 Banking Lines & Liquidity Guarantee
To ensure the treasury invariant ($\text{Overdraft} \le \text{Authorized Limit}$) is preserved through peak high-season cash troughs, the company maintains three structured credit facilities:

```
+--------------------------------------------------------------------------------------------------+
| AUTHORIZED BANKING CREDIT FACILITIES                                                             |
+--------------------+-------------------------+----------------+----------------+-----------------+
| Bank Partner       | Facility Type           | Line Limit     | Pricing Basis  | Security / Coll.|
+--------------------+-------------------------+----------------+----------------+-----------------+
| Attijariwafa Bank  | Ligne d'Escompte Comm.  | 1,500,000 MAD  | BAM + 3.50%    | LCR Clients Agr |
| Attijariwafa Bank  | Facilité de Caisse / Déc|   600,000 MAD  | BAM + 5.50%    | Caution Gérant  |
| Crédit Agricole M. | Crédit Campagne Agricole|   400,000 MAD  | BAM + 2.75%    | Warrant Stock PF|
+--------------------+-------------------------+----------------+----------------+-----------------+
| TOTAL AUTHORIZED   | Credit Absorption Cap   | 2,500,000 MAD  | Composite      | —               |
+--------------------+-------------------------+----------------+----------------+-----------------+
```

#### Treasury Invariant Proof:
$$\text{Fonds de Roulement (FR)} = \text{Financement Permanent } (7,028,700) - \text{Actif Immobilisé } (5,128,700) = \mathbf{1,900,000.00\text{ MAD}}$$
$$\text{Peak Cash Deficit } (\text{TN}_{\text{peak}}) = \text{FR} - \text{BFR}_{\text{peak}} = 1,900,000 - 3,520,000 = \mathbf{-1,620,000.00\text{ MAD}}$$
$$\text{Total Authorized Credit Facilities} = 1,500,000 + 600,000 + 400,000 = \mathbf{2,500,000.00\text{ MAD}}$$
$$\text{Net Safety Buffer at Peak Campaign} = 2,500,000.00 - 1,620,000.00 = \mathbf{+880,000.00\text{ MAD} > 0}$$
$$\implies \mathbf{\text{Treasury Invariant GUARANTEED: Cash balance never breaches credit covenants.}}$$
