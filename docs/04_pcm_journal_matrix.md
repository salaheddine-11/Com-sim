# SOUSS AGRI-PACK SARL — PCM JOURNAL MATRIX & DOUBLE-ENTRY TEMPLATES
**Document ID**: `DOC-04-PCM`  
**Version**: 1.0.0 (Phase 1 Formal Specification)  
**Accounting Standard**: Plan Comptable Général Marocain (CGNC / PCM)  
**Zero-Fault Equilibrium Invariant**: $\sum \text{Debits} \equiv \sum \text{Credits}$ for every individual journal entry template across all periods.

---

## 1. Accounting System Architecture & Journal Master Directory

The financial accounting system for Souss Agri-Pack SARL operates under the **Plan Comptable Général Marocain (CGNC)**, structured around 10 specialized auxiliary journals (*Journaux auxiliaires divisionnaires*). All transactions must balance to the exact centime with zero mathematical slack.

```
+--------------------------------------------------------------------------------------------------+
| SPECIALIZED JOURNALS MASTER DIRECTORY                                                            |
+----+--------------+---------------------------------------+--------------------------------------+
| #  | Journal Code | Journal Name (French)                 | Functional Accounting Scope          |
+----+--------------+---------------------------------------+--------------------------------------+
| 1  | RAN          | Journal des À-Nouveaux                | Opening balance sheet & year roll-over|
| 2  | ACH          | Journal des Achats & Importations     | Supplier invoices, DUM, electricity  |
| 3  | VEN          | Journal des Ventes & Facturation      | Client invoices, credit notes, scrap |
| 4  | BQ-AWB       | Journal Banque Attijariwafa bank      | Primary operating account, discount  |
| 5  | BQ-BP        | Journal Banque Centrale Populaire     | Secondary commercial collections     |
| 6  | BQ-CAM       | Journal Banque Crédit Agricole Maroc  | Agricultural campaign seasonal credit|
| 7  | BQ-BMCE      | Journal Banque BMCE Bank of Africa    | Export foreign currency operations   |
| 8  | CAI          | Journal de Caisse Centrale            | Petty cash disbursements (<=5k MAD)  |
| 9  | PAI          | Journal de Paie & Charges Sociales    | Monthly salaries, CNSS, AMO, IR      |
| 10 | OD           | Journal des Opérations Diverses       | TVA, DDA, inventory, cut-offs, risk  |
+----+--------------+---------------------------------------+--------------------------------------+
```

---

## 2. Exhaustive Double-Entry Journal Templates Matrix

Below is the complete, zero-fault debit/credit matrix mapping every business event to its corresponding PCM accounts, formulas, and balance proof.

```
====================================================================================================
SOUSS AGRI-PACK SARL — PCM ZERO-FAULT JOURNAL TEMPLATES MATRIX
====================================================================================================
```

### 2.1 Journal des Ventes & Facturation (`VEN`)

```
----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-SAL-003 | EVENT: EVT-SAL-003 | JOURNAL: VEN
Description: Facturation vente emballages carton au Maroc (TVA Standard 20.00%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
34210000 | Clients ordinaires                       | amount_ttc             | 0.00
71211000 | Ventes de produits finis au Maroc        | 0.00                   | amount_ht
44550000 | État - TVA facturée                      | 0.00                   | amount_tva
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: amount_ttc == (amount_ht + amount_tva) -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-SAL-004 | EVENT: EVT-SAL-004 | JOURNAL: VEN
Description: Facturation exportation directe cartons à des clients UE (TVA 0% CGI Art. 92)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
34210000 | Clients ordinaires                       | amount_ht_mad          | 0.00
71212000 | Ventes de produits finis à l'exportation | 0.00                   | amount_ht_mad
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: amount_ht_mad == amount_ht_mad -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-SAL-005 | EVENT: EVT-SAL-005 | JOURNAL: VEN
Description: Facture d'avoir accordée pour retour client / rabais de qualité (TVA 20.00%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
71211000 | Ventes de produits finis au Maroc        | rebate_ht              | 0.00
44550000 | État - TVA facturée                      | rebate_tva             | 0.00
34210000 | Clients ordinaires                       | 0.00                   | rebate_ttc
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (rebate_ht + rebate_tva) == rebate_ttc -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-SAL-006 | EVENT: EVT-SAL-006 | JOURNAL: VEN
Description: Vente de déchets et rognures de carton ondulé balées (TVA 20.00%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
34210000 | Clients ordinaires                       | amount_ttc             | 0.00
71271000 | Ventes de déchets et rebuts de carton    | 0.00                   | amount_ht
44550000 | État - TVA facturée                      | 0.00                   | amount_tva
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: amount_ttc == (amount_ht + amount_tva) -> EXACT EQUILIBRIUM
```

---

### 2.2 Journal des Achats & Importations (`ACH`)

```
----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-PUR-003 | EVENT: EVT-PUR-003 | JOURNAL: ACH
Description: Achat de bobines de papier chez des papetiers locaux marocains (TVA 20.00%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
61111000 | Achats de papier Kraftliner et Testliner | amount_ht              | 0.00
34512000 | État - TVA récupérable sur charges       | amount_tva             | 0.00
44110000 | Fournisseurs ordinaires                  | 0.00                   | amount_ttc
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (amount_ht + amount_tva) == amount_ttc -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-PUR-004 | EVENT: EVT-PUR-004 | JOURNAL: ACH
Description: Importation papier UE Port Agadir (EUR.1 0% DI, TPI 0.25%, TVA Import 20.00%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
61112000 | Achats de papier Kraftliner importé      | cif_mad + tpi_mad      | 0.00
34512000 | État - TVA récupérable sur charges       | import_tva_mad         | 0.00
44110000 | Fournisseurs (Papetier étranger & Douane)| 0.00                   | cif_mad+tpi_mad+tva
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (cif_mad + tpi_mad + import_tva_mad) == Total Fournisseurs -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-PUR-005 | EVENT: EVT-PUR-005 | JOURNAL: ACH
Description: Honoraires de transit et dédouanement maritime Port Agadir (TVA 20.00%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
61421000 | Transports sur achats (Fret & Transit)   | amount_ht              | 0.00
34512000 | État - TVA récupérable sur charges       | amount_tva             | 0.00
44110000 | Fournisseurs ordinaires (Transitaire)    | 0.00                   | amount_ttc
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (amount_ht + amount_tva) == amount_ttc -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-PUR-006 | EVENT: EVT-PUR-006 | JOURNAL: ACH
Description: Facture ONEE électricité industrielle MT (TVA 18.00% en 2025 / 20.00% en 2026)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
61251000 | Achats non stockés - Électricité MT ONEE | amount_ht              | 0.00
34512000 | État - TVA récupérable sur charges       | amount_tva             | 0.00
44110000 | Fournisseurs ordinaires (ONEE)           | 0.00                   | amount_ttc
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (amount_ht + amount_tva) == amount_ttc -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-PUR-007 | EVENT: EVT-PUR-007 | JOURNAL: ACH
Description: Achats d'amidon, colles industrielles et encres flexographiques (TVA 20.00%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
61211000 | Achats d'amidon et colles industrielles  | amount_ht              | 0.00
34512000 | État - TVA récupérable sur charges       | amount_tva             | 0.00
44110000 | Fournisseurs ordinaires                  | 0.00                   | amount_ttc
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (amount_ht + amount_tva) == amount_ttc -> EXACT EQUILIBRIUM
```

---

### 2.3 Journal de Paie & Charges Sociales (`PAI`)

```
----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-PAY-001 | EVENT: EVT-PAY-001 | JOURNAL: PAI
Description: Constatation des salaires bruts mensuels (22 permanents + 5 ouvriers saisonniers)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
61711000 | Rémunérations du personnel permanent     | gross_wages_permanent | 0.00
61712000 | Rémunérations des ouvriers saisonniers   | gross_wages_seasonal  | 0.00
44320000 | Rémunérations dues au personnel          | 0.00                   | total_gross_wages
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (gross_wages_permanent + gross_wages_seasonal) == total_gross_wages -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-PAY-002 | EVENT: EVT-PAY-002 | JOURNAL: PAI
Description: Retenues sur salaires : CNSS salariale (6.74%) et Impôt sur le Revenu (IR LF 2025)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
44320000 | Rémunérations dues au personnel          | cnss_sal + ir_withheld | 0.00
44410000 | CNSS (Part salariale 6.74%)              | 0.00                   | cnss_sal
44571000 | État - Retenues à la source IR salaires  | 0.00                   | ir_withheld
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (cnss_sal + ir_withheld) == Débit(4432) -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-PAY-003 | EVENT: EVT-PAY-003 | JOURNAL: PAI
Description: Charges patronales CNSS (21.09%) et Assurance Accidents du Travail (AT 3.80%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
61741000 | Charges patronales - Prestations & AF    | cnss_pat_prestations   | 0.00
61742000 | Charges patronales - AMO & Formation pro | cnss_pat_amo_fp        | 0.00
61761000 | Cotisations d'assurance AT (3.80%)       | at_insurance_cost      | 0.00
44410000 | CNSS (Part patronale totale)             | 0.00                   | cnss_pat_total
44450000 | Mutuelles et assurances AT               | 0.00                   | at_insurance_cost
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (cnss_pat_prestations + cnss_pat_amo_fp + at_insurance_cost) == (cnss_pat_total + at_insurance_cost)
```

---

### 2.4 Journal Banque Attijariwafa bank (`BQ-AWB`)

```
----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-PAY-004 | EVENT: EVT-PAY-004 | JOURNAL: BQ-AWB
Description: Virement bancaire de masse des salaires nets mensuels
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
44320000 | Rémunérations dues au personnel          | net_salaries_payable   | 0.00
51411000 | Banque Attijariwafa bank                 | 0.00                   | net_salaries_payable
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: net_salaries_payable == net_salaries_payable -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-PAY-005 | EVENT: EVT-PAY-005 | JOURNAL: BQ-AWB
Description: Télé-règlement mensuel DAMANCOM des cotisations CNSS
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
44410000 | CNSS                                     | total_cnss_due         | 0.00
51411000 | Banque Attijariwafa bank                 | 0.00                   | total_cnss_due
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: total_cnss_due == total_cnss_due -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-PAY-006 | EVENT: EVT-PAY-006 | JOURNAL: BQ-AWB
Description: Télé-paiement mensuel SIMPL-IR des retenues à la source sur salaires
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
44571000 | État - Retenues à la source IR salaires  | ir_withheld_total      | 0.00
51411000 | Banque Attijariwafa bank                 | 0.00                   | ir_withheld_total
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: ir_withheld_total == ir_withheld_total -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-BNK-003 | EVENT: EVT-BNK-003 | JOURNAL: BQ-AWB
Description: Crédit du produit net de l'escompte commercial et constatation des agios (TVA 10%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
51411000 | Banque Attijariwafa bank                 | lcn_nominal - agio_ttc | 0.00
63181000 | Intérêts et agios sur crédits d'escompte | discount_interest_ht   | 0.00
34512000 | État - TVA récupérable sur charges (10%) | agio_tva_10            | 0.00
55200000 | Crédits d'escompte (Ligne mobilisée AWB) | 0.00                   | lcn_nominal
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (lcn_nominal - agio_ttc) + discount_interest_ht + agio_tva_10 == lcn_nominal -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-BNK-005 | EVENT: EVT-BNK-005 | JOURNAL: BQ-AWB
Description: Débit suite à rejet d'effet escompté impayé et frais de rejet bancaire (TVA 10%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
34210000 | Clients ordinaires (Créance rétablie)    | lcn_nominal            | 0.00
61471000 | Services bancaires (Frais de rejet)      | reject_fee_ht          | 0.00
34512000 | État - TVA récupérable sur charges (10%) | reject_fee_tva         | 0.00
51411000 | Banque Attijariwafa bank                 | 0.00                   | lcn_nominal+fee_ttc
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (lcn_nominal + reject_fee_ht + reject_fee_tva) == Crédit(51411) -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-BNK-006 | EVENT: EVT-BNK-006 | JOURNAL: BQ-AWB
Description: Règlement par virement bancaire d'une facture fournisseur de matières premières
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
44110000 | Fournisseurs ordinaires                  | payment_amount         | 0.00
51411000 | Banque Attijariwafa bank                 | 0.00                   | payment_amount
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: payment_amount == payment_amount -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-TAX-002 | EVENT: EVT-TAX-002 | JOURNAL: BQ-AWB
Description: Paiement mensuel par télé-règlement SIMPL-TVA
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
44560000 | État - TVA due                           | tva_due_net            | 0.00
51411000 | Banque Attijariwafa bank                 | 0.00                   | tva_due_net
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: tva_due_net == tva_due_net -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-TAX-003 | EVENT: EVT-TAX-003 | JOURNAL: BQ-AWB
Description: Paiement trimestriel d'un acompte provisionnel d'Impôt sur les Sociétés (25% IS)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
34531000 | État - Acomptes provisionnels sur IS     | acompte_amount         | 0.00
51411000 | Banque Attijariwafa bank                 | 0.00                   | acompte_amount
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: acompte_amount == acompte_amount -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-TAX-005 | EVENT: EVT-TAX-005 | JOURNAL: BQ-AWB
Description: Paiement annuel de la Taxe Professionnelle (10%) et de la TSC (10.50%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
61611000 | Impôts et taxes directs - Taxe Prof.     | tp_amount              | 0.00
61612000 | Impôts et taxes directs - TSC            | tsc_amount             | 0.00
51411000 | Banque Attijariwafa bank                 | 0.00                   | tp_amount + tsc_amount
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (tp_amount + tsc_amount) == Crédit(51411) -> EXACT EQUILIBRIUM
```

---

### 2.5 Journal Banque Crédit Agricole du Maroc (`BQ-CAM`)

```
----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-BNK-007 | EVENT: EVT-BNK-007 | JOURNAL: BQ-CAM
Description: Déblocage d'un crédit de campagne agricole auprès du Crédit Agricole du Maroc
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
51413000 | Banque Crédit Agricole du Maroc          | loan_principal         | 0.00
55410000 | Crédits de campagne agricole             | 0.00                   | loan_principal
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: loan_principal == loan_principal -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-BNK-008 | EVENT: EVT-BNK-008 | JOURNAL: BQ-CAM
Description: Remboursement du principal et paiement des intérêts du crédit de campagne (TVA 10%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
55410000 | Crédits de campagne agricole             | loan_principal         | 0.00
63183000 | Intérêts sur crédits de campagne         | interest_amount_ht     | 0.00
34512000 | État - TVA récupérable sur charges (10%) | interest_tva_10        | 0.00
51413000 | Banque Crédit Agricole du Maroc          | 0.00                   | principal+interest_ttc
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: (loan_principal + interest_amount_ht + interest_tva_10) == Crédit(51413) -> EXACT EQUILIBRIUM
```

---

### 2.6 Journal des Opérations Diverses (`OD`)

```
----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-BNK-001 | EVENT: EVT-BNK-001 | JOURNAL: OD
Description: Réception et prise en portefeuille d'une traite LCN client
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
34240000 | Clients - effets à recevoir              | lcn_nominal            | 0.00
34210000 | Clients ordinaires                       | 0.00                   | lcn_nominal
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: lcn_nominal == lcn_nominal -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-BNK-002 | EVENT: EVT-BNK-002 | JOURNAL: OD
Description: Remise à l'escompte bancaire d'effets de commerce de portefeuille
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
51150000 | Effets remis à l'escompte                | lcn_nominal            | 0.00
34240000 | Clients - effets à recevoir              | 0.00                   | lcn_nominal
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: lcn_nominal == lcn_nominal -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-BNK-004 | EVENT: EVT-BNK-004 | JOURNAL: OD
Description: Extinction normale de la traite LCN à son échéance par le tiré
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
55200000 | Crédits d'escompte                       | lcn_nominal            | 0.00
51150000 | Effets remis à l'escompte                | 0.00                   | lcn_nominal
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: lcn_nominal == lcn_nominal -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-TAX-001 | EVENT: EVT-TAX-001 | JOURNAL: OD
Description: Liquidation mensuelle SIMPL-TVA (Déclaration du solde de TVA à décaisser)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
44550000 | État - TVA facturée                      | tva_collectee_total    | 0.00
34512000 | État - TVA récupérable sur charges       | 0.00                   | tva_deductible_charges
34511000 | État - TVA récupérable sur immobilisat.  | 0.00                   | tva_deductible_immob
44560000 | État - TVA due (Solde à payer)           | 0.00                   | tva_due_net
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: tva_collectee_total == (tva_deductible_charges + tva_deductible_immob + tva_due_net) -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-TAX-004 | EVENT: EVT-TAX-004 | JOURNAL: OD
Description: Liquidation annuelle IS (Charge définitive vs 4 acomptes provisionnels versés)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
67010000 | Impôts sur les résultats (IS définitif)  | total_is_due           | 0.00
34531000 | État - Acomptes provisionnels sur IS     | 0.00                   | sum_4_acomptes
44530000 | État - Impôts sur les résultats (Reliquat| 0.00                   | total_is_due - sum_4_acomptes
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: total_is_due == (sum_4_acomptes + Reliquat) -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-TAX-006 | EVENT: EVT-TAX-006 | JOURNAL: OD
Description: Distribution de dividendes avec Retenue à la Source selon millésime (15% vs 11.25%/10%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
11910000 | Résultat net de l'exercice (Dividendes)  | gross_dividends        | 0.00
44572000 | État - Retenues à la source dividendes   | 0.00                   | ras_dividends_amount
44650000 | Associés - dividendes à payer (Net)      | 0.00                   | gross - ras_amount
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: gross_dividends == (ras_dividends_amount + Net Dividendes) -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-TAX-007 | EVENT: EVT-TAX-007 | JOURNAL: OD
Description: Dotation provision pour pénalités Loi 69-21 (Délais de paiement fournisseurs)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
65832000 | Pénalités et amendes Loi 69-21           | penalty_l69_amount     | 0.00
45010000 | Provisions pour litiges & pénalités L69  | 0.00                   | penalty_l69_amount
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: penalty_l69_amount == penalty_l69_amount -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-INV-001 | EVENT: EVT-INV-001 | JOURNAL: OD
Description: Sortie de stock de bobines de papier consommées pour la fabrication
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
61140000 | Variation des stocks de matières prem.   | consumed_cump_value    | 0.00
31110000 | Matières premières - Bobines de papier   | 0.00                   | consumed_cump_value
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: consumed_cump_value == consumed_cump_value -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-INV-002 | EVENT: EVT-INV-002 | JOURNAL: OD
Description: Entrée en stock de produits finis fabriqués au coût de production complet
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
31510000 | Produits finis - Emballages carton       | production_cost_value  | 0.00
71320000 | Variation des stocks de produits finis   | 0.00                   | production_cost_value
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: production_cost_value == production_cost_value -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-INV-003 | EVENT: EVT-INV-003 | JOURNAL: OD
Description: Constatation en stock des déchets et rognures de production valorisés (8% scrap)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
31580000 | Déchets et rebuts de carton récupérables | scrap_recoverable_val  | 0.00
61140000 | Variation des stocks de matières prem.   | 0.00                   | scrap_recoverable_val
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: scrap_recoverable_val == scrap_recoverable_val -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-RSK-001 | EVENT: EVT-RSK-001 | JOURNAL: OD
Description: Destruction et mise au rebut de bobines de papier avariées par humidité
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
65881000 | Charges non courantes - Pertes sur stock | damaged_stock_value    | 0.00
31110000 | Matières premières                       | 0.00                   | damaged_stock_value
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: damaged_stock_value == damaged_stock_value -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-RSK-003 | EVENT: EVT-RSK-003 | JOURNAL: OD
Description: Sanction fiscale CGI Art. 193 pour encaissement espèces excédant 20,000 MAD (6%)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
65833000 | Sanctions encaissement espèces (Art 193) | cash_penalty_amount    | 0.00
44521000 | État - Impôts, taxes et pénalités à payer| 0.00                   | cash_penalty_amount
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: cash_penalty_amount == cash_penalty_amount -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-CLS-001 | EVENT: EVT-CLS-001 | JOURNAL: OD
Description: Dotations annuelles aux amortissements des immobilisations corporelles (DDA 380k MAD)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
61810000 | Dotations d'exploitation amortissements  | 380000.00              | 0.00
28321000 | Amortissements des bâtiments industriels | 0.00                   | 110000.00
28332000 | Amortissements du matériel et outillage  | 0.00                   | 220000.00
28340000 | Amortissements du matériel de transport  | 0.00                   | 30000.00
28352000 | Amortissements du matériel informatique  | 0.00                   | 20000.00
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: 380000.00 == (110000 + 220000 + 30000 + 20000) -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-CLS-002 | EVENT: EVT-CLS-002 | JOURNAL: OD
Description: Régularisation des charges constatées d'avance de fin d'exercice (Assurances N+1)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
34910000 | Charges constatées d'avance              | prepaid_expense_amount | 0.00
61341000 | Primes d'assurances                      | 0.00                   | prepaid_expense_amount
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: prepaid_expense_amount == prepaid_expense_amount -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-CLS-003 | EVENT: EVT-CLS-003 | JOURNAL: OD
Description: Régularisation des livraisons non facturées au 31/12 (Factures à établir)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
34271000 | Clients - factures à établir             | unbilled_amount_ttc    | 0.00
71211000 | Ventes de produits finis au Maroc        | 0.00                   | unbilled_amount_ht
44550000 | État - TVA facturée                      | 0.00                   | unbilled_amount_tva
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: unbilled_amount_ttc == (unbilled_amount_ht + unbilled_amount_tva) -> EXACT EQUILIBRIUM

----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-CLS-006 | EVENT: EVT-CLS-006 | JOURNAL: OD
Description: Constatation du Bénéfice Net après Impôts au Bilan (Compte 11910000)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Formule Débit (MAD)    | Formule Crédit (MAD)
---------+------------------------------------------+------------------------+----------------------
88000000 | Résultat net après impôts (Synthèse CPC) | net_profit (397200.00) | 0.00
11910000 | Résultat net de l'exercice (Bénéfice)    | 0.00                   | net_profit (397200.00)
---------+------------------------------------------+------------------------+----------------------
PROOF OF BALANCE: 397200.00 == 397200.00 -> EXACT EQUILIBRIUM
```

---

### 2.7 Journal des À-Nouveaux (`RAN`)

```
----------------------------------------------------------------------------------------------------
TEMPLATE: TPL-CLS-007 | EVENT: EVT-CLS-007 | JOURNAL: RAN
Description: Réouverture des comptes de bilan au 01/01/2025 (Équilibre parfait Actif == Passif)
----------------------------------------------------------------------------------------------------
PCM Code | Compte Intitulé Officiel CGNC            | Débit d'Ouverture (MAD)| Crédit d'Ouverture (MAD)
---------+------------------------------------------+------------------------+----------------------
23110000 | Terrains nus                             |             800,000.00 |                 0.00
23210000 | Bâtiments industriels                    |           2,200,000.00 |                 0.00
23320000 | Matériel et outillage de production      |           4,400,000.00 |                 0.00
23400000 | Matériel de transport                    |             450,000.00 |                 0.00
23510000 | Mobilier de bureau                       |             120,000.00 |                 0.00
23520000 | Matériel informatique                    |             180,000.00 |                 0.00
24810000 | Dépôts et cautionnements versés          |              45,000.00 |                 0.00
28321000 | Amortissements des bâtiments             |                   0.00 |           495,000.00
28332000 | Amortissements du matériel et outillage  |                   0.00 |         1,905,000.00
28340000 | Amortissements du matériel de transport  |                   0.00 |           427,500.00
28351000 | Amortissements du mobilier de bureau     |                   0.00 |            58,800.00
28352000 | Amortissements du matériel informatique  |                   0.00 |           180,000.00
31110000 | Stocks de matières premières             |             820,000.00 |                 0.00
31510000 | Stocks de produits finis                 |             340,000.00 |                 0.00
34210000 | Clients et comptes rattachés             |           3,450,000.00 |                 0.00
34550000 | État - TVA récupérable / Crédit          |             185,000.00 |                 0.00
51411000 | Banques (Soldes débiteurs disponibles)   |             285,000.00 |                 0.00
51611000 | Caisse centrale                          |              25,000.00 |                 0.00
11110000 | Capital social                           |                   0.00 |           800,000.00
11400000 | Réserve légale                           |                   0.00 |            80,000.00
11510000 | Réserves statutaires                     |                   0.00 |           120,000.00
11611000 | Report à nouveau (Vintage Pré-2023 - 15%)|                   0.00 |         2,150,000.00
11612000 | Report à nouveau (Vintage 2023+ - 11.25%)|                   0.00 |         1,678,700.00
14810000 | Emprunts auprès des étb de crédit (BMCE) |                   0.00 |         2,200,000.00
44110000 | Fournisseurs et comptes rattachés        |                   0.00 |         2,150,000.00
44410000 | CNSS à payer                             |                   0.00 |           112,000.00
44520000 | État - Impôts et taxes (IS dû)           |                   0.00 |            98,500.00
44550000 | État - TVA facturée à décaisser          |                   0.00 |           265,000.00
44570000 | État - IR retenu à la source             |                   0.00 |            44,500.00
44880000 | Autres créanciers & charges à payer      |                   0.00 |            35,000.00
55200000 | Crédits d'escompte (LCR mobilisées)      |                   0.00 |           500,000.00
---------+------------------------------------------+------------------------+----------------------
TOTAL    | BILAN D'OUVERTURE AU 01/01/2025          |          13,300,000.00 |        13,300,000.00
---------+------------------------------------------+------------------------+----------------------
PROOF OF EQUILIBRIUM:
  Total Actif Brut = 13,300,000.00 MAD
  Total Amortissements Passifs = 3,066,300.00 MAD
  Total Actif Net == Total Passif Net == 10,233,700.00 MAD
  Imbalance = 0.00 MAD -> MATHEMATICALLY PERFECT ZERO-FAULT EQUILIBRIUM
```
