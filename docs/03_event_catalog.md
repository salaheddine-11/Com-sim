# SOUSS AGRI-PACK SARL — BUSINESS EVENT CATALOG
**Document ID**: `DOC-03-EVT`  
**Version**: 1.0.0 (Phase 1 Formal Specification)  
**Applicable Accounting Standard**: Plan Comptable Marocain (PCM / CGNC)  
**Tax & Legal Framework**: Code Général des Impôts (CGI 2025/2026), Code de Commerce (Loi 15-95, Loi 69-21), Dahir CNSS 1972, Code des Douanes ADII.

---

## 1. Catalog Architecture & Cycle Topology

The Souss Agri-Pack SARL simulation engine organizes all operational, commercial, financial, and regulatory activities into **8 numbered enterprise cycles**:

```
+--------------------------------------------------------------------------------------------------+
| BUSINESS EVENT CYCLE TOPOLOGY                                                                    |
+----+--------------------+----------------------------------------+-------------------------------+
| #  | Prefix Code        | Operational Cycle Name                 | Primary Specialized Journals  |
+----+--------------------+----------------------------------------+-------------------------------+
| 1  | EVT-SAL-xxx        | Order-to-Cash & Commercial Receivables | VEN (Ventes), OD              |
| 2  | EVT-PUR-xxx        | Procure-to-Pay, Raw Materials & Utility| ACH (Achats), OD              |
| 3  | EVT-PAY-xxx        | Payroll, Social Security & Gerance     | PAI (Paie), BQ-AWB            |
| 4  | EVT-BNK-xxx        | Treasury, LCN Discounting & Credit     | BQ-AWB, BQ-CAM, OD            |
| 5  | EVT-TAX-xxx        | Corporate Taxes, Declarations & Fines  | OD, BQ-AWB                    |
| 6  | EVT-INV-xxx        | Inventory Movements & Production Logs  | OD (Opérations Diverses)      |
| 7  | EVT-RSK-xxx        | Operational Risks & Stochastic Shocks  | OD, ACH                       |
| 8  | EVT-CLS-xxx        | Year-End Closing, Cut-Offs & Roll-Over | OD, RAN (À-Nouveaux)          |
+----+--------------------+----------------------------------------+-------------------------------+
```

Every single event satisfies the **1:1 Mapping Contract**: it corresponds to exactly one balanced journal template in `config/journal_templates.yaml` and enforces strict preconditions and postconditions.

---

## 2. Detailed Event Specifications

### Cycle 1: Order-to-Cash & Commercial Receivables (`EVT-SAL-xxx`)

#### `EVT-SAL-001`: Sales Order Confirmation
- **Description**: Confirmation of a commercial customer order for corrugated packaging (P001–P005).
- **Trigger**: Receipt and validation of customer Purchase Order (*Bon de Commande Client*).
- **Trigger Type**: Transactional / Event-Driven.
- **Primary Document**: *Bon de Commande Client (BC)*.
- **Parameters**: `client_id`, `sku_code`, `ordered_quantity_m2`, `unit_price_ht`, `delivery_deadline`.
- **Preconditions**:
  1. Client exists in `dim_clients` and is active.
  2. `Client.OutstandingReceivables + (Quantity * Price * 1.20) <= Client.CreditLimit`.
- **Postconditions**: Production capacity reserved; Order status set to `CONFIRMED`.
- **Accounting Side-Effects**: None (Off-balance sheet commitment).

#### `EVT-SAL-002`: Finished Goods Dispatch
- **Description**: Physical shipping of finished packaging from Ait Melloul warehouse to customer packing station.
- **Trigger**: Warehouse outbound inspection and truck loading.
- **Trigger Type**: Transactional / Event-Driven.
- **Primary Document**: *Bon de Livraison (BL)* signed by carrier and customer.
- **Parameters**: `bl_number`, `order_id`, `dispatched_quantity_m2`, `carrier_id`.
- **Preconditions**: Finished goods inventory available in Account `31510000`.
- **Postconditions**: Inventory depleted; BL logged for billing.
- **Accounting Side-Effects**: Handled in Inventory Cycle (`EVT-INV-002` variation).

#### `EVT-SAL-003`: Domestic Sales Invoicing
- **Description**: Generation of statutory commercial invoice with 20% Moroccan TVA for domestic clients.
- **Trigger**: Validation of signed delivery slip (*BL*).
- **Trigger Type**: Transactional.
- **Primary Document**: *Facture de Vente* (carrying ICE, IF, RC, TP, and legal mentions).
- **Parameters**: `invoice_number`, `client_id`, `amount_ht`, `tva_rate` (0.20), `amount_tva`, `amount_ttc`.
- **Preconditions**: Signed BL exists; invoice date within open fiscal period.
- **Postconditions**: Customer ledger updated; TVA liability recorded.
- **Accounting Template**: `TPL-SAL-003` (Journal `VEN`):
  - **Debit**: `34210000` (Clients ordinaires) = `amount_ttc`
  - **Credit**: `71211000` (Ventes de produits finis au Maroc) = `amount_ht`
  - **Credit**: `44550000` (État - TVA facturée) = `amount_tva`
- **Statutory Reference**: CGI Art. 89 & Art. 98.

#### `EVT-SAL-004`: Direct EU Export Invoicing
- **Description**: Invoicing of corrugated packaging exported directly to European clients with 0% TVA deduction right.
- **Trigger**: Customs clearance confirmation and export declaration (*DUM de Sortie*).
- **Trigger Type**: Transactional.
- **Primary Document**: *Facture Export* + *DUM Exportation* + *Certificat EUR.1*.
- **Parameters**: `invoice_number`, `client_id`, `amount_ht_mad`, `currency` (`EUR`), `exchange_rate`.
- **Preconditions**: Verified customs export declaration (*DUM Sortie*) with stamp.
- **Postconditions**: Export sales recorded; 0% TVA reported under SIMPL-TVA exempt deduction line.
- **Accounting Template**: `TPL-SAL-004` (Journal `VEN`):
  - **Debit**: `34210000` (Clients ordinaires) = `amount_ht_mad`
  - **Credit**: `71212000` (Ventes de produits finis à l'exportation) = `amount_ht_mad`
- **Statutory Reference**: CGI Art. 92-I-1 (Exonération avec droit à déduction).

#### `EVT-SAL-005`: Customer Credit Note (*Facture d'Avoir*)
- **Description**: Issuance of a credit note for customer return, technical defect, or volume rebate (*RRR*).
- **Trigger**: Quality claim validation or commercial rebate approval.
- **Trigger Type**: Transactional.
- **Primary Document**: *Facture d'Avoir*.
- **Parameters**: `credit_note_number`, `original_invoice_ref`, `rebate_ht`, `tva_rate` (0.20), `rebate_tva`, `rebate_ttc`.
- **Preconditions**: Original invoice was posted and verified.
- **Postconditions**: Client receivable reduced; output TVA adjusted.
- **Accounting Template**: `TPL-SAL-005` (Journal `VEN`):
  - **Debit**: `71211000` (Ventes de produits finis au Maroc) = `rebate_ht`
  - **Debit**: `44550000` (État - TVA facturée) = `rebate_tva`
  - **Credit**: `34210000` (Clients ordinaires) = `rebate_ttc`
- **Statutory Reference**: CGI Art. 98 & Plan Comptable Marocain.

#### `EVT-SAL-006`: Production Scrap & Waste Board Sale
- **Description**: Sale of baled corrugated cardboard cuttings (8% technical scrap) to recycling pulpers.
- **Trigger**: Outbound weighbridge ticket and recycling pickup.
- **Trigger Type**: Transactional.
- **Primary Document**: *Facture Vente Rebuts* + *Bon de Pesée*.
- **Parameters**: `scrap_weight_kg`, `price_per_kg` (0.80 MAD), `amount_ht`, `amount_tva` (20%), `amount_ttc`.
- **Preconditions**: Minimum 5 tonnes accumulated in scrap baler.
- **Postconditions**: Scrap inventory cleared; ancillary revenue booked.
- **Accounting Template**: `TPL-SAL-006` (Journal `VEN`):
  - **Debit**: `34210000` (Clients ordinaires) = `amount_ttc`
  - **Credit**: `71271000` (Ventes de déchets et rebuts de carton) = `amount_ht`
  - **Credit**: `44550000` (État - TVA facturée) = `amount_tva`
- **Statutory Reference**: CGI Art. 89.

#### `EVT-SAL-007`: Doubtful Customer Provision Reclassification
- **Description**: Reclassification of an overdue receivable (> 180 days) as doubtful and creation of a bad-debt provision.
- **Trigger**: Legal recovery initiation or formal collection notice (*Mise en demeure*).
- **Trigger Type**: Conditional / Period-End.
- **Primary Document**: *Avis de Contentieux / Mise en Demeure d'Avocat*.
- **Parameters**: `client_id`, `unpaid_amount_ttc`, `provision_rate` (0.50 to 1.00), `provision_amount_ht`.
- **Preconditions**: Invoice overdue beyond agreed terms; formal collection unsuccessful.
- **Postconditions**: Customer transferred to doubtful ledger; tax-deductible provision accrued.
- **Accounting Template**: `TPL-SAL-007` (Journal `OD`):
  - **Debit**: `34250000` (Clients douteux ou litigieux) = `unpaid_amount_ttc`
  - **Credit**: `34210000` (Clients ordinaires) = `unpaid_amount_ttc`
  - **Debit**: `61961000` (Dotations d'exploitation aux provisions créances) = `provision_amount_ht`
  - **Credit**: `39420000` (Provisions pour dépréciation clients) = `provision_amount_ht`
- **Statutory Reference**: CGI Art. 10-I-F-3° (Provisions pour créances douteuses).

---

### Cycle 2: Procure-to-Pay, Raw Materials & Utilities (`EVT-PUR-xxx`)

#### `EVT-PUR-001`: Raw Paper Purchase Order Placement
- **Description**: Placement of raw paper purchase order with domestic or European paper mills.
- **Trigger**: MRP reorder point breach (Stock < 45-day consumption buffer).
- **Trigger Type**: Operational / Automated.
- **Primary Document**: *Bon de Commande Achat (PO)*.
- **Parameters**: `po_number`, `supplier_id`, `paper_grade` (Kraft/Fluting/Testliner), `tonnage`, `price_per_kg`.
- **Preconditions**: Supplier exists in `dim_suppliers`; procurement budget allocated.
- **Postconditions**: Supplier acknowledgment received; estimated arrival scheduled.
- **Accounting Side-Effects**: None (Off-balance sheet commitment).

#### `EVT-PUR-002`: Raw Material Inbound Acceptance
- **Description**: Physical receipt and quality validation of paper reels at Ait Melloul plant.
- **Trigger**: Truck arrival, weighbridge verification, moisture (< 8.5%) and burst strength testing.
- **Trigger Type**: Transactional.
- **Primary Document**: *Bon de Réception (BR)* + *Fiche de Contrôle Qualité*.
- **Parameters**: `br_number`, `po_ref`, `received_tonnage`, `reel_barcodes`, `moisture_pct`.
- **Preconditions**: Moisture $\le 8.5\%$; burst test ECT conforms to specification.
- **Postconditions**: Raw material stock increased under CUMP valuation.
- **Accounting Side-Effects**: Handled in Inventory Cycle (`EVT-INV-001` valuation).

#### `EVT-PUR-003`: Domestic Paper Mill Invoicing
- **Description**: Accounting of supplier invoice for raw paper delivered by domestic mills (GPC/CMCP).
- **Trigger**: 3-Way Match validation (PO + BR + Supplier Invoice).
- **Trigger Type**: Transactional.
- **Primary Document**: *Facture Fournisseur* (TVA 20%).
- **Parameters**: `invoice_number`, `supplier_id`, `amount_ht`, `tva_rate` (0.20), `amount_tva`, `amount_ttc`.
- **Preconditions**: 3-Way matching verified without quantity/price variance.
- **Postconditions**: Accounts payable credited; input TVA recorded.
- **Accounting Template**: `TPL-PUR-003` (Journal `ACH`):
  - **Debit**: `61111000` (Achats de papier Kraftliner et Testliner) = `amount_ht`
  - **Debit**: `34512000` (État - TVA récupérable sur charges) = `amount_tva`
  - **Credit**: `44110000` (Fournisseurs ordinaires) = `amount_ttc`
- **Statutory Reference**: CGI Art. 98 & Art. 101.

#### `EVT-PUR-004`: EU Paper Importation Clearance (Port of Agadir)
- **Description**: Customs clearance and DUM liquidation of containerized paper reels imported from the European Union.
- **Trigger**: Vessel discharge at Port of Agadir and customs liquidation.
- **Trigger Type**: Transactional.
- **Primary Document**: *DUM d'Importation* + *Certificat EUR.1* + *Facture Papetier UE CIF*.
- **Parameters**: `dum_number`, `cif_mad`, `droit_importation` (0.00 MAD / EUR.1), `tpi_mad` (0.25%), `import_tva_mad` (20%).
- **Preconditions**: Valid EUR.1 certificate presented to ADII (0% Droit d'Importation).
- **Postconditions**: Goods cleared through customs; import taxes settled.
- **Accounting Template**: `TPL-PUR-004` (Journal `ACH`):
  - **Debit**: `61112000` (Achats de papier Kraftliner importé) = `cif_mad + tpi_mad`
  - **Debit**: `34512000` (État - TVA récupérable sur charges) = `import_tva_mad`
  - **Credit**: `44110000` (Fournisseurs - Papetier UE & Douane) = `cif_mad + tpi_mad + import_tva_mad`
- **Statutory Reference**: Accord d'Association Maroc-UE (Dahir n° 1-00-175) & CGI Art. 121.

#### `EVT-PUR-005`: Customs Transit & Forwarder Invoicing
- **Description**: Port handling, maritime transit, and customs forwarding fees for imported containers.
- **Trigger**: Receipt of freight forwarder invoice (*Facture Transitaire*).
- **Trigger Type**: Transactional.
- **Primary Document**: *Facture Transitaire*.
- **Parameters**: `invoice_number`, `transitaire_id`, `amount_ht`, `tva_rate` (0.20), `amount_tva`, `amount_ttc`.
- **Preconditions**: Port exit voucher (*Bon de Sortie Portuaire*) validated.
- **Postconditions**: Forwarder payable recorded; recoverable TVA accrued.
- **Accounting Template**: `TPL-PUR-005` (Journal `ACH`):
  - **Debit**: `61421000` (Transports sur achats - Fret & Transit) = `amount_ht`
  - **Debit**: `34512000` (État - TVA récupérable sur charges) = `amount_tva`
  - **Credit**: `44110000` (Fournisseurs ordinaires) = `amount_ttc`
- **Statutory Reference**: CGI Art. 98.

#### `EVT-PUR-006`: ONEE Medium Voltage Electricity Invoicing
- **Description**: Monthly industrial power utility invoice from ONEE MT under the multi-year TVA convergence rate.
- **Trigger**: Monthly electricity meter reading.
- **Trigger Type**: Monthly Scheduled.
- **Primary Document**: *Facture ONEE Moyenne Tension*.
- **Parameters**: `invoice_number`, `consumption_kwh`, `amount_ht`, `tva_rate` (0.18 in 2025 / 0.20 in 2026), `amount_tva`, `amount_ttc`.
- **Preconditions**: Meter reading confirmed by plant maintenance engineer.
- **Postconditions**: Utility cost booked; input TVA recognized at effective-dated rate.
- **Accounting Template**: `TPL-PUR-006` (Journal `ACH`):
  - **Debit**: `61251000` (Achats non stockés - Électricité MT ONEE) = `amount_ht`
  - **Debit**: `34512000` (État - TVA récupérable sur charges) = `amount_tva`
  - **Credit**: `44110000` (Fournisseurs ordinaires - ONEE) = `amount_ttc`
- **Statutory Reference**: LF 2024 Art. 6 (TVA convergence: 18% in 2025 $\to$ 20% in 2026).

#### `EVT-PUR-007`: Auxiliary Chemicals & Starch Glue Invoicing
- **Description**: Procurement of industrial modified starch, flexo inks, stitching wire, and pallet wrap.
- **Trigger**: Delivery acceptance slip and supplier invoice matching.
- **Trigger Type**: Transactional.
- **Primary Document**: *Facture Fournisseur Fournitures Consommables*.
- **Parameters**: `invoice_number`, `supplier_id`, `amount_ht`, `tva_rate` (0.20), `amount_tva`, `amount_ttc`.
- **Preconditions**: Physical receipt in chemical storage area.
- **Postconditions**: Consumables expense booked; supplier payable recorded.
- **Accounting Template**: `TPL-PUR-007` (Journal `ACH`):
  - **Debit**: `61211000` (Achats d'amidon et colles industrielles) = `amount_ht`
  - **Debit**: `34512000` (État - TVA récupérable sur charges) = `amount_tva`
  - **Credit**: `44110000` (Fournisseurs ordinaires) = `amount_ttc`
- **Statutory Reference**: CGI Art. 98.

---

### Cycle 3: Payroll, Social Security & Statutory Remuneration (`EVT-PAY-xxx`)

#### `EVT-PAY-001`: Monthly Gross Payroll Accrual
- **Description**: Monthly recording of gross wages for 22 permanent employees and 5 seasonal packaging workers.
- **Trigger**: Month-end payroll calculation and attendance sheet approval.
- **Trigger Type**: Monthly Scheduled (25th of month).
- **Primary Document**: *Livre de Paie Mensuel* / *Journal de Paie*.
- **Parameters**: `gross_wages_permanent`, `gross_wages_seasonal`, `total_gross_wages`.
- **Preconditions**: Timeclock hours validated; SMIG compliance verified (17.10 MAD/h in 2025 $\to$ 17.92 MAD/h in 2026).
- **Postconditions**: Gross payroll accrued; employee payable created.
- **Accounting Template**: `TPL-PAY-001` (Journal `PAI`):
  - **Debit**: `61711000` (Rémunérations du personnel permanent) = `gross_wages_permanent`
  - **Debit**: `61712000` (Rémunérations des ouvriers saisonniers) = `gross_wages_seasonal`
  - **Credit**: `44320000` (Rémunérations dues au personnel) = `total_gross_wages`
- **Statutory Reference**: Code du Travail (Loi n° 65-99).

#### `EVT-PAY-002`: Employee Salary Deductions (CNSS & IR)
- **Description**: Withholding of employee social contributions (CNSS/AMO 6.74%) and salary personal income tax (IR LF 2025 scale).
- **Trigger**: Net salary computation per employee bulletin.
- **Trigger Type**: Monthly Scheduled.
- **Primary Document**: *Bulletins de Paie Récapitulatifs*.
- **Parameters**: `cnss_employee_total` (4.48% capped at 6k + 2.26% AMO), `ir_withheld_total`.
- **Preconditions**: Gross salary accrued in Account `44320000`.
- **Postconditions**: Net payable salary established; tax/social debts recognized.
- **Accounting Template**: `TPL-PAY-002` (Journal `PAI`):
  - **Debit**: `44320000` (Rémunérations dues au personnel) = `cnss_employee_total + ir_withheld_total`
  - **Credit**: `44410000` (CNSS) = `cnss_employee_total`
  - **Credit**: `44571000` (État - Retenues à la source sur salaires IR) = `ir_withheld_total`
- **Statutory Reference**: Dahir CNSS 1972 & CGI Art. 73-I (LF 2025).

#### `EVT-PAY-003`: Employer Social Charges Accrual
- **Description**: Accrual of mandatory employer social contributions (CNSS/AMO 21.09%) and Workplace Accident Insurance (AT 3.80%).
- **Trigger**: Monthly social security bordereau preparation.
- **Trigger Type**: Monthly Scheduled.
- **Primary Document**: *Bordereau Récapitulatif CNSS & Quittance AT*.
- **Parameters**: `cnss_employer_prestations` (8.98% capped + 6.40% AF), `cnss_employer_amo_fp` (1.60% + 2.26% + 1.85%), `at_insurance_cost` (3.80%).
- **Preconditions**: Payroll master grid reconciled with P&L labour envelope.
- **Postconditions**: Social liabilities accrued.
- **Accounting Template**: `TPL-PAY-003` (Journal `PAI`):
  - **Debit**: `61741000` (Charges sociales patronales - CNSS Prestations & Alloc.) = `cnss_employer_prestations`
  - **Debit**: `61742000` (Charges sociales patronales - AMO & Formation pro) = `cnss_employer_amo_fp`
  - **Debit**: `61761000` (Cotisations d'assurance Accidents du Travail - AT 3.80%) = `at_insurance_cost`
  - **Credit**: `44410000` (CNSS) = `cnss_employer_prestations + cnss_employer_amo_fp`
  - **Credit**: `44450000` (Mutuelles et assurances accidents du travail) = `at_insurance_cost`
- **Statutory Reference**: Dahir n° 1-72-184 & Loi n° 18-12.

#### `EVT-PAY-004`: Net Salary Bank Disbursement
- **Description**: Bank electronic transfer of net salaries to employee bank accounts.
- **Trigger**: Monthly salary settlement date (28th of month).
- **Trigger Type**: Monthly Scheduled.
- **Primary Document**: *Ordre de Virement de Masse AWB*.
- **Parameters**: `net_salaries_payable`, `bank_code` (`AWB`).
- **Preconditions**: Available cash or authorized overdraft in Account `51411000`.
- **Postconditions**: Employee payable cleared; bank account debited.
- **Accounting Template**: `TPL-PAY-004` (Journal `BQ-AWB`):
  - **Debit**: `44320000` (Rémunérations dues au personnel) = `net_salaries_payable`
  - **Credit**: `51411000` (Banque Attijariwafa bank) = `net_salaries_payable`
- **Statutory Reference**: Code du Travail (Loi n° 65-99 Art. 363).

#### `EVT-PAY-005`: CNSS DAMANCOM Monthly Tele-Payment
- **Description**: Electronic settlement of total monthly CNSS contributions (Employee + Employer).
- **Trigger**: Statutory deadline (10th of month M+1).
- **Trigger Type**: Monthly Scheduled.
- **Primary Document**: *Quittance Télé-règlement DAMANCOM*.
- **Parameters**: `total_cnss_due`.
- **Preconditions**: Monthly DAMANCOM tele-declaration validated.
- **Postconditions**: CNSS liability fully extinguished.
- **Accounting Template**: `TPL-PAY-005` (Journal `BQ-AWB`):
  - **Debit**: `44410000` (CNSS) = `total_cnss_due`
  - **Credit**: `51411000` (Banque Attijariwafa bank) = `total_cnss_due`
- **Statutory Reference**: Dahir n° 1-72-184 Art. 26.

#### `EVT-PAY-006`: SIMPL-IR Monthly Tele-Payment
- **Description**: Electronic settlement of withheld salary personal income tax (IR) to the DGI.
- **Trigger**: Statutory deadline (last day of month M+1).
- **Trigger Type**: Monthly Scheduled.
- **Primary Document**: *Quittance de Télé-Paiement SIMPL-IR*.
- **Parameters**: `ir_withheld_total`.
- **Preconditions**: Monthly SIMPL-IR electronic return validated.
- **Postconditions**: IR withholding liability cleared.
- **Accounting Template**: `TPL-PAY-006` (Journal `BQ-AWB`):
  - **Debit**: `44571000` (État - Retenues à la source sur salaires IR) = `ir_withheld_total`
  - **Credit**: `51411000` (Banque Attijariwafa bank) = `ir_withheld_total`
- **Statutory Reference**: CGI Art. 78 & Art. 155.

---

### Cycle 4: Treasury, Commercial Paper & Credit Facilities (`EVT-BNK-xxx`)

#### `EVT-BNK-001`: Customer LCN Commercial Paper Receipt
- **Description**: Acceptance and receipt of a Lettre de Change Normalisée (*LCN*) commercial paper from a customer.
- **Trigger**: Physical receipt of signed LCN paper / electronic acceptance.
- **Trigger Type**: Transactional.
- **Primary Document**: *LCN Traite acceptée*.
- **Parameters**: `instrument_id`, `client_id`, `lcn_nominal`, `due_date` (60 to 90 days).
- **Preconditions**: Valid commercial invoice exists in customer ledger.
- **Postconditions**: Ordinary receivable converted to negotiable commercial bill in portfolio.
- **Accounting Template**: `TPL-BNK-001` (Journal `OD`):
  - **Debit**: `34240000` (Clients - effets à recevoir / LCN en portefeuille) = `lcn_nominal`
  - **Credit**: `34210000` (Clients ordinaires) = `lcn_nominal`
- **Statutory Reference**: Code de Commerce (Loi n° 15-95 Art. 159 to 231).

#### `EVT-BNK-002`: LCN Remittance for Discount (*Remise à l'Escompte*)
- **Description**: Endorsement and transmission of portfolio commercial bills to Attijariwafa Bank for discounting.
- **Trigger**: Treasury cash requirement during peak high-season working capital buildup.
- **Trigger Type**: Conditional / Treasury-Driven.
- **Primary Document**: *Bordereau de Remise à l'Escompte AWB*.
- **Parameters**: `bordereau_number`, `bills_count`, `total_nominal_remitted`.
- **Preconditions**: Available headroom under AWB discount facility ($\le 1,500,000\text{ MAD}$).
- **Postconditions**: Commercial bills transferred from portfolio to discounted collection.
- **Accounting Template**: `TPL-BNK-002` (Journal `OD`):
  - **Debit**: `51150000` (Effets remis à l'escompte) = `total_nominal_remitted`
  - **Credit**: `34240000` (Clients - effets à recevoir) = `total_nominal_remitted`
- **Statutory Reference**: Code de Commerce & Banking Standards.

#### `EVT-BNK-003`: Discount Credit Advice & Agios Calculation
- **Description**: Crediting of net discounted proceeds to bank account and recognition of financial interest and commissions.
- **Trigger**: Bank processing and issuance of credit advice (*Avis de Crédit*).
- **Trigger Type**: Transactional.
- **Primary Document**: *Avis de Crédit Escompte AWB*.
- **Parameters**: `lcn_nominal`, `days_to_maturity`, `discount_interest_ht`, `banking_fees_ht`, `agio_tva_10`, `total_agio_ttc`.
- **Preconditions**: `EVT-BNK-002` posted; credit facility active.
- **Postconditions**: Cash received; short-term bank credit booked; financial charges recognized.
- **Accounting Template**: `TPL-BNK-003` (Journal `BQ-AWB`):
  - **Debit**: `51411000` (Banque Attijariwafa bank) = `lcn_nominal - total_agio_ttc`
  - **Debit**: `63181000` (Intérêts et agios sur crédits d'escompte) = `discount_interest_ht + banking_fees_ht`
  - **Debit**: `34512000` (État - TVA récupérable sur charges - 10% agios) = `agio_tva_10`
  - **Credit**: `55200000` (Crédits d'escompte - Ligne mobilisée) = `lcn_nominal`
- **Statutory Reference**: CGI Art. 99-3 (TVA 10% sur opérations de banque) & BAM directives.

#### `EVT-BNK-004`: LCN Maturity Normal Extinction
- **Description**: Automatic extinction of the discount liability upon customer honoring the LCN on its due date.
- **Trigger**: LCN maturity date reached without drawee protest.
- **Trigger Type**: Scheduled / Maturity Date.
- **Primary Document**: *Avis de Dénouement / Relevé Bancaire*.
- **Parameters**: `lcn_nominal`, `instrument_id`.
- **Preconditions**: Maturity date elapsed without bank return advice.
- **Postconditions**: Discount credit facility line freed; off-balance exposure cleared.
- **Accounting Template**: `TPL-BNK-004` (Journal `OD`):
  - **Debit**: `55200000` (Crédits d'escompte) = `lcn_nominal`
  - **Credit**: `51150000` (Effets remis à l'escompte) = `lcn_nominal`
- **Statutory Reference**: Code de Commerce (Loi n° 15-95).

#### `EVT-BNK-005`: LCN Unpaid Protest & Rejection Notice
- **Description**: Processing of a customer bill rejected at maturity by the drawee bank (*Impayé LCN*).
- **Trigger**: Bank issuance of non-payment notice (*Avis d'Impayé*) and debiting of company bank account.
- **Trigger Type**: Stochastic / Exception.
- **Primary Document**: *Avis d'Impayé Bancaire + Relevé de Compte*.
- **Parameters**: `lcn_nominal`, `reject_fee_ht` (150 MAD), `reject_fee_tva` (15 MAD).
- **Preconditions**: Drawee bank dishonored bill.
- **Postconditions**: Customer receivable reinstated; rejection fee recognized; collection process initiated.
- **Accounting Template**: `TPL-BNK-005` (Journal `BQ-AWB`):
  - **Debit**: `34210000` (Clients ordinaires) = `lcn_nominal`
  - **Debit**: `61471000` (Services bancaires - Frais de rejet d'effet) = `reject_fee_ht`
  - **Debit**: `34512000` (État - TVA récupérable sur charges - 10%) = `reject_fee_tva`
  - **Credit**: `51411000` (Banque Attijariwafa bank) = `lcn_nominal + reject_fee_ht + reject_fee_tva`
- **Statutory Reference**: Code de Commerce Art. 211 & BAM interbank clearing rules.

#### `EVT-BNK-006`: Supplier Wire Transfer Disbursement
- **Description**: Bank wire transfer settlement for raw paper or auxiliary supplier invoices.
- **Trigger**: Payment schedule maturity (60 to 90 days DPO).
- **Trigger Type**: Transactional / Scheduled.
- **Primary Document**: *Ordre de Virement Bancaire*.
- **Parameters**: `payment_amount`, `supplier_id`, `invoice_ref`.
- **Preconditions**: Supplier invoice approved for payment; bank funds available.
- **Postconditions**: Supplier payable debited; bank cash decreased.
- **Accounting Template**: `TPL-BNK-006` (Journal `BQ-AWB`):
  - **Debit**: `44110000` (Fournisseurs ordinaires) = `payment_amount`
  - **Credit**: `51411000` (Banque Attijariwafa bank) = `payment_amount`
- **Statutory Reference**: Code de Commerce (Loi 69-21 compliance).

#### `EVT-BNK-007`: CAM Agricultural Campaign Credit Drawdown
- **Description**: Seasonal cash advance drawdown from Crédit Agricole du Maroc (CAM) to fund agricultural harvest packaging.
- **Trigger**: High-season BFR spike (October through February).
- **Trigger Type**: Seasonal / Treasury-Driven.
- **Primary Document**: *Avis de Déblocage Crédit de Campagne CAM*.
- **Parameters**: `loan_principal` (up to 400,000 MAD), `campaign_season` (`2025-2026`).
- **Preconditions**: Campaign season active (Sep–Mar); CAM facility headroom available.
- **Postconditions**: CAM bank cash increased; seasonal short-term debt recorded.
- **Accounting Template**: `TPL-BNK-007` (Journal `BQ-CAM`):
  - **Debit**: `51413000` (Banque Crédit Agricole du Maroc) = `loan_principal`
  - **Credit**: `55410000` (Crédits de campagne agricole) = `loan_principal`
- **Statutory Reference**: CAM Agricultural Financing Framework.

#### `EVT-BNK-008`: CAM Agricultural Campaign Credit Repayment
- **Description**: Full repayment of the CAM seasonal campaign credit principal along with accrued financial interest.
- **Trigger**: Campaign loan maturity (March 31).
- **Trigger Type**: Seasonal Scheduled.
- **Primary Document**: *Avis de Remboursement & Décompte d'Intérêts CAM*.
- **Parameters**: `loan_principal`, `interest_amount_ht` (5.50% p.a.), `interest_tva_10`.
- **Preconditions**: Campaign proceeds realized from citrus/tomato client collections.
- **Postconditions**: Campaign loan liability settled; financial charges booked.
- **Accounting Template**: `TPL-BNK-008` (Journal `BQ-CAM`):
  - **Debit**: `55410000` (Crédits de campagne agricole) = `loan_principal`
  - **Debit**: `63183000` (Intérêts sur crédits de campagne agricole) = `interest_amount_ht`
  - **Debit**: `34512000` (État - TVA récupérable sur charges - 10%) = `interest_tva_10`
  - **Credit**: `51413000` (Banque Crédit Agricole du Maroc) = `loan_principal + interest_amount_ht + interest_tva_10`
- **Statutory Reference**: BAM directives & CGI Art. 99-3.

#### `EVT-BNK-009`: Portfolio LCN Collection at Maturity (Not Discounted)
- **Description**: Normal collection of a customer bill retained in portfolio (not discounted), settled at maturity by credit of the bank account.
- **Trigger**: Bill maturity date reached while the bill remains in PORTFOLIO.
- **Trigger Type**: Scheduled.
- **Primary Document**: *Avis de Crédit Encaissement LCN*.
- **Parameters**: `lcn_reference`, `maturity_date`, `lcn_nominal`.
- **Preconditions**: Customer bill in portfolio, not discounted; no unpaid protest received from the drawee bank.
- **Postconditions**: Bank cash increased; bills receivable decreased.
- **Accounting Template**: `TPL-BNK-009` (Journal `OD`):
  - **Debit**: `51411000` (Banque Attijariwafa bank) = `lcn_nominal`
  - **Credit**: `34240000` (Clients - effets à recevoir) = `lcn_nominal`
- **Statutory Reference**: CGI Art. 218 / practice des effets de commerce.

#### `EVT-BNK-010`: Customer Wire Transfer Collection at Terms
- **Description**: Collection by bank wire of a customer invoice settled at the agreed terms (30 days).
- **Trigger**: Invoice due date reached for a `VIR_30D` payment-terms invoice.
- **Trigger Type**: Scheduled.
- **Primary Document**: *Relevé Bancaire - Virement Client*.
- **Parameters**: `invoice_number`, `settlement_date`, `amount_ttc`.
- **Preconditions**: Customer invoice at wire-transfer terms; wire reconciled with the invoice.
- **Postconditions**: Bank cash increased; ordinary trade receivable extinguished.
- **Accounting Template**: `TPL-BNK-010` (Journal `BQ-AWB`):
  - **Debit**: `51411000` (Banque Attijariwafa bank) = `amount_ttc`
  - **Credit**: `34210000` (Clients ordinaires) = `amount_ttc`
- **Statutory Reference**: CGI Art. 218.

#### `EVT-BNK-011`: Customer Cash Collection at Reception
- **Description**: Cash collection at reception of a customer invoice settled on delivery (souk / traditional wholesale market).
- **Trigger**: Delivery of a CASH payment-terms invoice.
- **Trigger Type**: Transactional.
- **Primary Document**: *Reçu de Caisse Client*.
- **Parameters**: `invoice_number`, `settlement_date`, `amount_ttc`.
- **Preconditions**: Invoice delivered and settled cash on reception; cash receipt reconciled with the invoice.
- **Postconditions**: Central cash increased; ordinary trade receivable extinguished.
- **Accounting Template**: `TPL-BNK-011` (Journal `CAI`):
  - **Debit**: `51611000` (Caisse Centrale Usine Ait Melloul) = `amount_ttc`
  - **Credit**: `34210000` (Clients ordinaires) = `amount_ttc`
- **Statutory Reference**: CGI Art. 218.

#### `EVT-BNK-012`: Customer Cheque Collection at Terms
- **Description**: Collection by cheque of a customer invoice settled at the agreed terms (15 days).
- **Trigger**: Invoice due date reached for a CHEQUE payment-terms invoice.
- **Trigger Type**: Scheduled.
- **Primary Document**: *Bordereau de Remise de Chèques*.
- **Parameters**: `invoice_number`, `settlement_date`, `amount_ttc`.
- **Preconditions**: Customer invoice at cheque terms; cheque cleared and reconciled with the invoice.
- **Postconditions**: Bank cash increased; ordinary trade receivable extinguished.
- **Accounting Template**: `TPL-BNK-012` (Journal `BQ-AWB`):
  - **Debit**: `51411000` (Banque Attijariwafa bank) = `amount_ttc`
  - **Credit**: `34210000` (Clients ordinaires) = `amount_ttc`
- **Statutory Reference**: CGI Art. 218.

#### `EVT-BNK-013`: Portfolio LCN Unpaid Return to Ordinary Receivable
- **Description**: Customer bill unpaid at maturity while retained in portfolio (not discounted): the receivable returns to the ordinary account, with no bank intervention and no protest fees.
- **Trigger**: Portfolio bill maturity with drawee dishonor.
- **Trigger Type**: Conditional.
- **Primary Document**: *Effet Impayé Rendu par la Banque Tirée*.
- **Parameters**: `lcn_reference`, `maturity_date`, `lcn_nominal`.
- **Preconditions**: Bill in portfolio, not discounted, at maturity; dishonor confirmed by the drawee bank or the drawer.
- **Postconditions**: Ordinary trade receivable increased; bills receivable decreased. No bank fee (bank was not mobilized).
- **Accounting Template**: `TPL-BNK-013` (Journal `OD`):
  - **Debit**: `34210000` (Clients ordinaires) = `lcn_nominal`
  - **Credit**: `34240000` (Clients - effets à recevoir) = `lcn_nominal`
- **Statutory Reference**: CGI Art. 218 / pratique des effets de commerce.

---

### Cycle 5: Corporate Taxes, Declarations & Compliance (`EVT-TAX-xxx`)

#### `EVT-TAX-001`: Monthly SIMPL-TVA Liquidation
- **Description**: Month-end net VAT liability calculation comparing collected output VAT and deductible input VAT.
- **Trigger**: Month-end closing of purchase and sales journals.
- **Trigger Type**: Monthly Scheduled.
- **Primary Document**: *Déclaration Mensuelle SIMPL-TVA*.
- **Parameters**: `tva_collectee_total`, `tva_deductible_charges`, `tva_deductible_immob`, `tva_due_net`.
- **Preconditions**: All sales and purchase invoices for month M posted.
- **Postconditions**: Net VAT payable booked to Account `44560000` (or credit to `34550000`).
- **Accounting Template**: `TPL-TAX-001` (Journal `OD`):
  - **Debit**: `44550000` (État - TVA facturée) = `tva_collectee_total`
  - **Credit**: `34512000` (État - TVA récupérable sur charges) = `tva_deductible_charges`
  - **Credit**: `34511000` (État - TVA récupérable sur immobilisations) = `tva_deductible_immob`
  - **Credit**: `44560000` (État - TVA due à payer) = `tva_due_net`
- **Statutory Reference**: CGI Art. 108 & Art. 110.

#### `EVT-TAX-002`: Monthly SIMPL-TVA Tele-Payment
- **Description**: Electronic bank payment of the liquidated net VAT balance to the DGI Treasury.
- **Trigger**: Statutory due date (last day of month M+1).
- **Trigger Type**: Monthly Scheduled.
- **Primary Document**: *Quittance de Télé-Paiement SIMPL-TVA*.
- **Parameters**: `tva_due_net`.
- **Preconditions**: SIMPL-TVA return validated; `tva_due_net > 0`.
- **Postconditions**: Net VAT liability cleared.
- **Accounting Template**: `TPL-TAX-002` (Journal `BQ-AWB`):
  - **Debit**: `44560000` (État - TVA due) = `tva_due_net`
  - **Credit**: `51411000` (Banque Attijariwafa bank) = `tva_due_net`
- **Statutory Reference**: CGI Art. 155.

#### `EVT-TAX-003`: Quarterly Corporate Tax Acompte Payment
- **Description**: Electronic settlement of the quarterly 25% IS installment (*Acompte provisionnel*).
- **Trigger**: Statutory due date (March 31, June 30, September 30, December 31).
- **Trigger Type**: Quarterly Scheduled.
- **Primary Document**: *Bordereau de Versement SIMPL-IS*.
- **Parameters**: `installment_number` (1 to 4), `acompte_amount` ($25\% \times \text{Prior IS} = \mathbf{24,625.00\text{ MAD}}$).
- **Preconditions**: Prior-year base IS established.
- **Postconditions**: Tax asset recognized in Account `34531000`.
- **Accounting Template**: `TPL-TAX-003` (Journal `BQ-AWB`):
  - **Debit**: `34531000` (État - Acomptes provisionnels sur IS) = `acompte_amount`
  - **Credit**: `51411000` (Banque Attijariwafa bank) = `acompte_amount`
- **Statutory Reference**: CGI Art. 170.

#### `EVT-TAX-004`: Annual IS Liquidation & Reliquat Settlement
- **Description**: Year-end calculation of definitive corporate income tax liability and determination of the remaining balance (*Reliquat d'IS*).
- **Trigger**: Fiscal year financial statement finalization (March 31 N+1).
- **Trigger Type**: Annual Scheduled.
- **Primary Document**: *Liasse Fiscale / Déclaration SIMPL-IS*.
- **Parameters**: `total_is_due` (98,500 MAD in 2025), `sum_4_acomptes` (98,500 MAD), `reliquat_amount` (0.00 MAD).
- **Preconditions**: Fiscal result finalized via *Tableau de passage*; $\text{IS} > \text{CM}$ verified.
- **Postconditions**: Definitive IS recorded in P&L Class 6; advance acomptes cleared; reliquat recognized.
- **Accounting Template**: `TPL-TAX-004` (Journal `OD`):
  - **Debit**: `67010000` (Impôts sur les résultats - IS définitif) = `total_is_due`
  - **Credit**: `34531000` (État - Acomptes provisionnels sur IS) = `sum_4_acomptes`
  - **Credit**: `44530000` (État - Impôts sur les résultats / Reliquat) = `total_is_due - sum_4_acomptes`
- **Statutory Reference**: CGI Art. 19 & Art. 170.

#### `EVT-TAX-005`: Annual Taxe Professionnelle & TSC Settlement
- **Description**: Payment of annual municipal direct taxes assessed on the 3% Rental Value of industrial assets.
- **Trigger**: DGI tax assessment receipt (*Avis d'imposition*) due by May 31 / June 30.
- **Trigger Type**: Annual Scheduled.
- **Primary Document**: *Avis d'Imposition Taxe Professionnelle / TSC*.
- **Parameters**: `valeur_locative` (222,000 MAD), `tp_amount` (22,200 MAD @ 10%), `tsc_amount` (23,310 MAD @ 10.5%).
- **Preconditions**: 5-Year creation exemption expired (effective 2025).
- **Postconditions**: Local taxes recognized in operating expenses and cleared from bank.
- **Accounting Template**: `TPL-TAX-005` (Journal `BQ-AWB`):
  - **Debit**: `61611000` (Impôts et taxes directs - Taxe professionnelle) = `tp_amount`
  - **Debit**: `61612000` (Impôts et taxes directs - Taxe de services communaux) = `tsc_amount`
  - **Credit**: `51411000` (Banque Attijariwafa bank) = `tp_amount + tsc_amount`
- **Statutory Reference**: Loi n° 47-06 relative à la fiscalité locale (Art. 6, 7, 8, 32–39).

#### `EVT-TAX-006`: Dividend Distribution & Vintage RAS Withholding
- **Description**: Annual General Meeting dividend declaration and execution of the statutory vintage withholding tax rule.
- **Trigger**: Approval of profit distribution at AGM (*Procès-Verbal de l'AGO*).
- **Trigger Type**: Annual Scheduled (Post-June AGM).
- **Primary Document**: *Procès-Verbal de l'Assemblée Générale Ordinaire*.
- **Parameters**: `gross_dividends`, `vintage_split` (Pre-2023 @ 15.0% vs Post-2023 @ 11.25%/10.0%), `ras_dividends_amount`, `net_dividends_payable`.
- **Preconditions**: Distributable retained earnings available; legal reserve ceiling (10% capital = 80,000 MAD) satisfied.
- **Postconditions**: Shareholder dividends payable recognized; withholding tax owed to DGI.
- **Accounting Template**: `TPL-TAX-006` (Journal `OD`):
  - **Debit**: `11910000` (Résultat net de l'exercice - Bénéfice distribué) = `gross_dividends`
  - **Credit**: `44572000` (État - Retenues à la source sur dividendes) = `ras_dividends_amount`
  - **Credit**: `44650000` (Associés - dividendes à payer) = `gross_dividends - ras_dividends_amount`
- **Statutory Reference**: CGI Art. 73-II-C-1 & Art. 247-XLIV.

#### `EVT-TAX-007`: Law 69-21 Late Payment Penalty Accrual
- **Description**: Accrual of statutory late payment penalties on supplier invoices settled beyond the 60-day legal term.
- **Trigger**: Quarterly Law 69-21 compliance audit.
- **Trigger Type**: Quarterly Scheduled.
- **Primary Document**: *Déclaration Trimestrielle SIMPL-Délais*.
- **Parameters**: `overdue_invoice_ttc`, `months_delayed`, `fine_rate` (BAM 2.75% + 0.25% + 0.85%/mo), `penalty_l69_amount`.
- **Preconditions**: Invoices identified exceeding statutory credit terms.
- **Postconditions**: Tax fine recognized; non-deductible liability accrued.
- **Accounting Template**: `TPL-TAX-007` (Journal `OD`):
  - **Debit**: `65832000` (Pénalités et astreintes de retard Loi 69-21) = `penalty_l69_amount`
  - **Credit**: `45010000` (Provisions pour litiges et pénalités Loi 69-21) = `penalty_l69_amount`
- **Statutory Reference**: Loi n° 69-21 modifiant le Code de Commerce.

---

### Cycle 6: Inventory Movements & Production Logging (`EVT-INV-xxx`)

#### `EVT-INV-001`: Raw Paper Issue to Corrugator
- **Description**: Transfer of raw paper reels (Kraftliner, Fluting, Testliner) from warehouse to corrugator line for board manufacturing.
- **Trigger**: Production work order execution.
- **Trigger Type**: Operational.
- **Primary Document**: *Bon de Sortie Matières Premières*.
- **Parameters**: `consumed_tonnage`, `consumed_cump_value`.
- **Preconditions**: Raw reel inventory available in Account `31110000`.
- **Postconditions**: Raw material stock reduced; stock variation expense recognized.
- **Accounting Template**: `TPL-INV-001` (Journal `OD`):
  - **Debit**: `61140000` (Variation des stocks de matières premières) = `consumed_cump_value`
  - **Credit**: `31110000` (Matières premières - Bobines de papier) = `consumed_cump_value`
- **Statutory Reference**: Plan Comptable Marocain (Méthode de l'inventaire permanent).

#### `EVT-INV-002`: Finished Box Receipt to Warehouse
- **Description**: Receipt of finished printed and die-cut agricultural boxes into the finished goods warehouse at full production cost.
- **Trigger**: Production batch completion and QA release.
- **Trigger Type**: Operational.
- **Primary Document**: *Bon d'Entrée Produits Finis*.
- **Parameters**: `produced_m2`, `sku_code`, `production_cost_value`.
- **Preconditions**: Conversion inspection passed.
- **Postconditions**: Finished goods inventory increased; production variation credited.
- **Accounting Template**: `TPL-INV-002` (Journal `OD`):
  - **Debit**: `31510000` (Produits finis - Emballages carton) = `production_cost_value`
  - **Credit**: `71320000` (Variation des stocks de produits finis) = `production_cost_value`
- **Statutory Reference**: Plan Comptable Marocain.

#### `EVT-INV-003`: Production Technical Scrap Logging (8%)
- **Description**: Logging of baled technical scrap (rognures et chutes de découpe) generated during converting.
- **Trigger**: End-of-shift scrap collection and baling.
- **Trigger Type**: Operational.
- **Primary Document**: *Fiche de Rebuts & Balle de Carton*.
- **Parameters**: `scrap_weight_kg`, `scrap_recoverable_value` (valued at 0.80 MAD/kg).
- **Preconditions**: 8% technical waste rate generated.
- **Postconditions**: Scrap inventory recognized in Account `31580000`.
- **Accounting Template**: `TPL-INV-003` (Journal `OD`):
  - **Debit**: `31580000` (Déchets et rebuts de carton récupérables) = `scrap_recoverable_value`
  - **Credit**: `61140000` (Variation des stocks de matières premières) = `scrap_recoverable_value`
- **Statutory Reference**: Plan Comptable Marocain.

---

### Cycle 7: Operational Risks & Stochastic Events (`EVT-RSK-xxx`)

#### `EVT-RSK-001`: Raw Paper Humidity Loss & Scrapping
- **Description**: Scrapping and write-off of paper reels damaged by warehouse water ingress or excessive relative humidity (> 12%).
- **Trigger**: Quality inspection failure on damaged reels (PRNG Seed `42002`).
- **Trigger Type**: Stochastic / Event-Driven.
- **Primary Document**: *Procès-Verbal de Destruction & Constat d'Avarie*.
- **Parameters**: `damaged_stock_value` (31,000 to 93,000 MAD).
- **Preconditions**: Damaged reels identified in storage.
- **Postconditions**: Raw material inventory written off; non-operating loss recognized.
- **Accounting Template**: `TPL-RSK-001` (Journal `OD`):
  - **Debit**: `65881000` (Charges non courantes - Pertes sur stocks avariés) = `damaged_stock_value`
  - **Credit**: `31110000` (Matières premières) = `damaged_stock_value`
- **Statutory Reference**: CGI Art. 10 (Déduction des pertes réelles et justifiées).

#### `EVT-RSK-002`: Port of Agadir Container Demurrage Incurred
- **Description**: Surcharge incurred for imported container dwell time exceeding the 7-day tariff franchise at the Port of Agadir terminal.
- **Trigger**: Customs clearance delay beyond Day 7 (PRNG Seed `42004`).
- **Trigger Type**: Stochastic / Event-Driven.
- **Primary Document**: *Facture Marsa Maroc / ANP Surestaries Port Agadir*.
- **Parameters**: `dwell_days`, `demurrage_amount_ht` (Tier 1: 150 MAD/d, Tier 2: 300 MAD/d, Tier 3: 500 MAD/d), `demurrage_tva` (20%).
- **Preconditions**: Container dwell time $> 7$ calendar days.
- **Postconditions**: Demurrage cost recognized; port authority payable created.
- **Accounting Template**: `TPL-RSK-002` (Journal `ACH`):
  - **Debit**: `65881000` (Frais de surestaries et magasinage Port Agadir) = `demurrage_amount_ht`
  - **Debit**: `34512000` (État - TVA récupérable sur charges - 20%) = `demurrage_tva`
  - **Credit**: `44110000` (Fournisseurs - Marsa Maroc / ANP) = `demurrage_amount_ht + demurrage_tva`
- **Statutory Reference**: Tarifs Officiels ANP / Marsa Maroc Port d'Agadir.

#### `EVT-RSK-003`: CGI Art. 193 Cash Collection Penalty Assessment
- **Description**: Assessment of a 6% tax penalty on cash received from a client exceeding the statutory 20,000 MAD threshold.
- **Trigger**: Cash settlement receipt exceeding 20,000 MAD.
- **Trigger Type**: Exception / Breach.
- **Primary Document**: *Notification de Redressement DGI / Reçu Caisse*.
- **Parameters**: `cash_collected_amount`, `penalty_rate` (0.06), `cash_penalty_amount`.
- **Preconditions**: Client settled $> 20,000.00\text{ MAD}$ in cash.
- **Postconditions**: Statutory sanction booked in non-deductible tax expenses.
- **Accounting Template**: `TPL-RSK-003` (Journal `OD`):
  - **Debit**: `65833000` (Sanctions pour encaissement espèces - CGI Art 193) = `cash_penalty_amount`
  - **Credit**: `44521000` (État - Impôts, taxes et pénalités à payer) = `cash_penalty_amount`
- **Statutory Reference**: CGI Art. 193 (Sanction pour paiement en espèces).

---

### Cycle 8: Year-End Closing, Cut-Offs & Roll-Over (`EVT-CLS-xxx`)

#### `EVT-CLS-001`: Annual Fixed Asset Depreciation (DDA)
- **Description**: Recording of annual linear depreciation across all industrial buildings, corrugator machinery, vehicles, and IT assets.
- **Trigger**: Fiscal year-end inventory closing (December 31).
- **Trigger Type**: Annual Scheduled.
- **Primary Document**: *Tableau des Amortissements de l'Exercice*.
- **Parameters**: `dda_buildings` (110k), `dda_machinery` (220k), `dda_vehicles` (30k), `dda_it` (20k), `total_annual_dda` (**380,000.00 MAD**).
- **Preconditions**: Fixed asset register reconciled with opening gross values.
- **Postconditions**: Operating depreciation recognized; accumulated amortization updated.
- **Accounting Template**: `TPL-CLS-001` (Journal `OD`):
  - **Debit**: `61810000` (Dotations d'exploitation aux amortissements) = `total_annual_dda`
  - **Credit**: `28321000` (Amortissements des bâtiments industriels) = `dda_buildings`
  - **Credit**: `28332000` (Amortissements du matériel et outillage) = `dda_machinery`
  - **Credit**: `28340000` (Amortissements du matériel de transport) = `dda_vehicles`
  - **Credit**: `28352000` (Amortissements du matériel informatique) = `dda_it`
- **Statutory Reference**: CGI Art. 10 & Plan Comptable Marocain.

#### `EVT-CLS-002`: Prepaid Expenses Cut-Off (*Charges Constatées d'Avance — CCA*)
- **Description**: Year-end cut-off adjustment deferring expenses paid in year N that relate to year N+1 (annual insurance policies, rent).
- **Trigger**: Year-end cut-off audit (December 31).
- **Trigger Type**: Annual Scheduled.
- **Primary Document**: *État d'Inventaire des Charges Constatées d'Avance*.
- **Parameters**: `prepaid_expense_amount`.
- **Preconditions**: Invoices span into FY 2026.
- **Postconditions**: Current-year expenses reduced; current asset recognized in Account `34910000`.
- **Accounting Template**: `TPL-CLS-002` (Journal `OD`):
  - **Debit**: `34910000` (Charges constatées d'avance) = `prepaid_expense_amount`
  - **Credit**: `61341000` (Primes d'assurances) = `prepaid_expense_amount`
- **Statutory Reference**: Plan Comptable Marocain (Principe de spécialisation des exercices).

#### `EVT-CLS-003`: Unbilled Domestic Deliveries Cut-Off (*Factures à Établir — FAE*)
- **Description**: Year-end cut-off recognition of finished packaging delivered before December 31 for which formal invoices have not yet been issued.
- **Trigger**: Unmatched dispatch notes on December 31.
- **Trigger Type**: Annual Scheduled.
- **Primary Document**: *État des Bons de Livraison Non Facturés au 31/12*.
- **Parameters**: `unbilled_amount_ht`, `unbilled_amount_tva` (20%), `unbilled_amount_ttc`.
- **Preconditions**: Signed BL dated on or before 31/12/N.
- **Postconditions**: Accrued revenue and output VAT recognized in current year.
- **Accounting Template**: `TPL-CLS-003` (Journal `OD`):
  - **Debit**: `34271000` (Clients - factures à établir) = `unbilled_amount_ttc`
  - **Credit**: `71211000` (Ventes de produits finis au Maroc) = `unbilled_amount_ht`
  - **Credit**: `44550000` (État - TVA facturée) = `unbilled_amount_tva`
- **Statutory Reference**: Plan Comptable Marocain.

#### `EVT-CLS-004`: Expense Accounts Clearance to CPC (*Solde des Charges*)
- **Description**: Closing and clearing of all Class 6 expense accounts to the intermediate CPC synthesis accounts (8100, 8300, 8500).
- **Trigger**: Year-end ledger closing.
- **Trigger Type**: Annual Scheduled.
- **Primary Document**: *Balance Générale des Comptes Avant Clôture*.
- **Parameters**: `sum_charges_exploitation` (10,190,000 MAD), `sum_charges_financieres` (245,000 MAD), `sum_charges_non_courantes` (0.00 MAD).
- **Preconditions**: All inventory, DDA, and cut-off adjustments posted.
- **Postconditions**: Class 6 accounts zeroed; CPC result accounts debited.
- **Accounting Template**: `TPL-CLS-004` (Journal `OD`):
  - **Debit**: `81000000` (Résultat d'exploitation - Débit) = `sum_charges_exploitation`
  - **Debit**: `83000000` (Résultat financier - Débit) = `sum_charges_financieres`
  - **Debit**: `85000000` (Résultat non courant - Débit) = `sum_charges_non_courantes`
  - **Credit**: `61111000` ... `61810000` (All Class 6 accounts credited to zero)
- **Statutory Reference**: Plan Comptable Marocain (Classe 8 CGNC).

#### `EVT-CLS-005`: Revenue Accounts Clearance to CPC (*Solde des Produits*)
- **Description**: Closing and clearing of all Class 7 revenue accounts to intermediate CPC synthesis accounts.
- **Trigger**: Year-end ledger closing.
- **Trigger Type**: Annual Scheduled.
- **Primary Document**: *Balance Générale des Comptes Avant Clôture*.
- **Parameters**: `sum_produits_exploitation` (10,930,700 MAD), `sum_produits_financiers` (0.00 MAD).
- **Preconditions**: All revenue entries finalized.
- **Postconditions**: Class 7 accounts zeroed; CPC result accounts credited.
- **Accounting Template**: `TPL-CLS-005` (Journal `OD`):
  - **Debit**: `71211000` ... `71271000` (All Class 7 accounts debited to zero)
  - **Credit**: `81000000` (Résultat d'exploitation - Crédit) = `sum_produits_exploitation`
  - **Credit**: `83000000` (Résultat financier - Crédit) = `sum_produits_financiers`
- **Statutory Reference**: Plan Comptable Marocain.

#### `EVT-CLS-006`: Net Profit Determination & Balance Sheet Transfer
- **Description**: Transfer of the post-tax accounting net profit from the CPC synthesis account `88000000` into permanent equity Account `11910000`.
- **Trigger**: Fiscal result finalization and IS deduction.
- **Trigger Type**: Annual Scheduled.
- **Primary Document**: *Compte de Produits et Charges (CPC) Définitif*.
- **Parameters**: `net_accounting_profit` (**397,200.00 MAD**).
- **Preconditions**: Pre-tax profit ($495,700$) minus IS ($98,500$) equals exactly $397,200.00\text{ MAD}$.
- **Postconditions**: Net profit posted to equity; Balance Sheet in perfect mathematical equilibrium.
- **Accounting Template**: `TPL-CLS-006` (Journal `OD`):
  - **Debit**: `88000000` (Résultat net après impôts) = `net_accounting_profit`
  - **Credit**: `11910000` (Résultat net de l'exercice - Solde créditeur) = `net_accounting_profit`
- **Statutory Reference**: Plan Comptable Marocain.

#### `EVT-CLS-007`: Opening Balance Roll-Over (*Journal des À-Nouveaux*)
- **Description**: Rolling over closing balance sheet balances of December 31 into the opening journal (*Journal des À-Nouveaux — RAN*) on January 1 of the new fiscal year.
- **Trigger**: Opening of new fiscal year (January 1).
- **Trigger Type**: Annual Scheduled.
- **Primary Document**: *Bilan de Clôture N / Balance d'Ouverture N+1*.
- **Parameters**: Full opening ledger vector satisfying $\text{Actif} == \text{Passif}$ ($10,233,700.00\text{ MAD}$).
- **Preconditions**: Prior fiscal year fully closed with zero unresolved discrepancies.
- **Postconditions**: All balance sheet accounts initialized with correct opening balances and vintage partitions.
- **Accounting Template**: `TPL-CLS-007` (Journal `RAN`):
  - **Debit**: All Class 2, 3, and 5 asset accounts
  - **Credit**: All Class 1, 4, and 5 liability accounts
- **Statutory Reference**: Plan Comptable Marocain (Principe de continuité de l'exploitation).
