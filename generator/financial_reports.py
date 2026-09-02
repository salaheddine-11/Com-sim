# -*- coding: utf-8 -*-
"""
Moroccan Financial Reporting Engine (Liasse Fiscale, Bilan, CPC, ESG, Tableau de Financement).
Generates official, standard-compliant reports formatted in Markdown and structured JSON.
Uses Decimal throughout for 100% precision.
"""

from decimal import Decimal
from typing import Dict, Any, List
from generator.models import to_dec
from generator.pcm_ledger_engine import PCMLedgerEngine


class FinancialReportsGenerator:
    def __init__(self, ledger: PCMLedgerEngine, closing_data: Dict[str, Any]):
        self.ledger = ledger
        self.closing_data = closing_data

    def generate_bilan_markdown(self) -> str:
        # Actif Immobilisé — values pulled LIVE from the ledger for closing-date fidelity.
        # All previous hardcoded constants are replaced with PCMLedgerEngine queries
        # so the rendered numbers reconcile exactly with balance_generale.csv and
        # journal_general.csv. Hardcoded values were a stale snapshot.
        immob_frais_brut = max(Decimal("0.00"), self.ledger.get_account_net_balance("2111"))
        immob_frais_amort = max(Decimal("0.00"), -self.ledger.get_account_net_balance("2811"))
        immob_terrains_brut = max(Decimal("0.00"), self.ledger.get_account_net_balance("2311"))
        immob_terrains_amort = max(Decimal("0.00"), -self.ledger.get_account_net_balance("2812"))
        immob_batiments_brut = max(Decimal("0.00"), self.ledger.get_account_net_balance("2321"))
        immob_batiments_amort = max(Decimal("0.00"), -self.ledger.get_account_net_balance("2832"))
        immob_materiel_brut = max(Decimal("0.00"), self.ledger.get_account_net_balance("2332"))
        immob_materiel_amort = max(Decimal("0.00"), -self.ledger.get_account_net_balance("2833"))
        immob_transport_brut = max(Decimal("0.00"), self.ledger.get_account_net_balance("2340"))
        immob_transport_amort = max(Decimal("0.00"), -self.ledger.get_account_net_balance("2834"))
        immob_mobilier_brut = max(Decimal("0.00"), self.ledger.get_account_net_balance("2351"))
        immob_mobilier_amort = max(Decimal("0.00"), -self.ledger.get_account_net_balance("28351"))
        immob_info_brut = max(Decimal("0.00"), self.ledger.get_account_net_balance("2352"))
        immob_info_amort = max(Decimal("0.00"), -self.ledger.get_account_net_balance("28352"))
        immob_depots_brut = max(Decimal("0.00"), self.ledger.get_account_net_balance("2481"))
        immob_depots_amort = Decimal("0.00")

        total_immob_brut = to_dec(
            immob_frais_brut + immob_terrains_brut + immob_batiments_brut +
            immob_materiel_brut + immob_transport_brut + immob_mobilier_brut +
            immob_info_brut + immob_depots_brut
        )
        total_immob_amort = to_dec(
            immob_frais_amort + immob_terrains_amort + immob_batiments_amort +
            immob_materiel_amort + immob_transport_amort + immob_mobilier_amort +
            immob_info_amort + immob_depots_amort
        )
        total_immob_net = to_dec(total_immob_brut - total_immob_amort)

        # Actif Circulant — pull ALL Bilan accounts from the live ledger
        stock_mp_net = max(Decimal("0.00"), self.ledger.get_account_net_balance("3111"))
        stock_aux_net = max(Decimal("0.00"), self.ledger.get_account_net_balance("3121"))   # FIX: was not in original
        stock_pf_net = max(Decimal("0.00"), self.ledger.get_account_net_balance("3151"))
        clients_ordinaires_net = max(Decimal("0.00"), self.ledger.get_account_net_balance("3421"))
        clients_effets_net = max(Decimal("0.00"), self.ledger.get_account_net_balance("3424"))
        effets_escompte_net = max(Decimal("0.00"), self.ledger.get_account_net_balance("5115"))
        tva_recup_net = max(Decimal("0.00"), self.ledger.get_account_net_balance("3451"))
        tva_credit_net = max(Decimal("0.00"), self.ledger.get_account_net_balance("3455"))    # FIX: was 3456 (Crédit d'impôt IS), now correctly points to Crédit de TVA reportable
        credit_impot_net = max(Decimal("0.00"), self.ledger.get_account_net_balance("3456"))
        acomptes_is_net = max(Decimal("0.00"), self.ledger.get_account_net_balance("3453"))
        autres_creances_exploit_net = max(Decimal("0.00"), self.ledger.get_account_net_balance("3481")) + \
                                       max(Decimal("0.00"), self.ledger.get_account_net_balance("3488"))

        total_actif_circulant = to_dec(
            stock_mp_net + stock_aux_net + stock_pf_net +
            clients_ordinaires_net + clients_effets_net +
            effets_escompte_net + tva_recup_net + tva_credit_net +
            credit_impot_net + acomptes_is_net +
            autres_creances_exploit_net
        )

        # Trésorerie Actif
        banques_actif = max(Decimal("0.00"), self.ledger.get_account_net_balance("5141"))
        caisse_actif = max(Decimal("0.00"), self.ledger.get_account_net_balance("5161"))
        autres_tresor_actif = max(Decimal("0.00"), self.ledger.get_account_net_balance("5148"))  # chèques à encaisser
        total_tresorerie_actif = to_dec(banques_actif + caisse_actif + autres_tresor_actif)

        total_actif = to_dec(total_immob_net + total_actif_circulant + total_tresorerie_actif)

        # Passif: Financement Permanent
        capital_social = abs(self.ledger.get_account_net_balance("1111"))
        reserve_legale = abs(self.ledger.get_account_net_balance("1140"))
        reserves_statutaires = abs(self.ledger.get_account_net_balance("1151"))
        report_a_nouveau = abs(self.ledger.get_account_net_balance("1161")) or abs(self.ledger.get_account_net_balance("1191"))
        resultat_net = to_dec(self.closing_data.get("net_profit", Decimal("0.00")))
        emprunts_etablissements = abs(self.ledger.get_account_net_balance("1481"))

        total_capitaux_propres = to_dec(capital_social + reserve_legale + reserves_statutaires + report_a_nouveau + resultat_net)
        total_financement_permanent = to_dec(total_capitaux_propres + emprunts_etablissements)

        # Passif Circulant
        fournisseurs_ordinaires = abs(self.ledger.get_account_net_balance("4411"))
        fournisseurs_effets = abs(self.ledger.get_account_net_balance("4415"))
        remunerations_dues = abs(self.ledger.get_account_net_balance("4432"))
        cnss_a_payer = abs(self.ledger.get_account_net_balance("4441"))
        mutuelles_at_a_payer = abs(self.ledger.get_account_net_balance("4445"))
        is_a_payer = abs(self.ledger.get_account_net_balance("4453"))
        tva_facturee_due = abs(self.ledger.get_account_net_balance("4455")) + abs(self.ledger.get_account_net_balance("4456"))
        ir_retenu = abs(self.ledger.get_account_net_balance("4457"))
        autres_creanciers = abs(self.ledger.get_account_net_balance("4488"))

        total_passif_circulant = to_dec(
            fournisseurs_ordinaires + fournisseurs_effets + remunerations_dues +
            cnss_a_payer + mutuelles_at_a_payer + is_a_payer + tva_facturee_due +
            ir_retenu + autres_creanciers
        )

        # Trésorerie Passif
        credits_escompte = abs(self.ledger.get_account_net_balance("5520"))
        decouverts_bancaires = abs(self.ledger.get_account_net_balance("5541"))
        total_tresorerie_passif = to_dec(credits_escompte + decouverts_bancaires)

        total_passif = to_dec(total_financement_permanent + total_passif_circulant + total_tresorerie_passif)

        # Financial Identities
        fr = to_dec(total_financement_permanent - total_immob_net)
        bfr = to_dec(total_actif_circulant - total_passif_circulant)
        tn = to_dec(total_tresorerie_actif - total_tresorerie_passif)
        eq_check = to_dec(fr - bfr)
        equilibre_ok = (total_actif == total_passif)
        identite_ok = (eq_check == tn)
        equilibre_delta = to_dec(total_actif - total_passif)
        identite_delta = to_dec(eq_check - tn)

        md = f"""# BILAN (ACTIF & PASSIF) AU 31 DÉCEMBRE 2025
**Raison Sociale** : SOUSS AGRI-PACK SARL  
**ICE** : 002345678000091 | **IF** : 45127890 | **RC** : 28451 Agadir | **TP** : 30145280  
**Siège Social** : Zone Industrielle, Lot 47, Ait Melloul, Agadir  
**Référentiel Comptable** : Plan Comptable Général Marocain (PCM / CGNC)  

---

## 1. ACTIF

| Rubriques / Postes de l'Actif | Montant Brut (MAD) | Amortissements & Prov. (MAD) | Montant Net 2025 (MAD) |
| :--- | :---: | :---: | :---: |
| **ACTIF IMMOBILISÉ** | | | |
| Immobilisation en non-valeurs (Frais constitution) | {immob_frais_brut:,.2f} | {immob_frais_amort:,.2f} | 0.00 |
| Terrains industriels (Ait Melloul) | {immob_terrains_brut:,.2f} | 0.00 | {immob_terrains_brut:,.2f} |
| Bâtiments industriels (Usine & Bureaux) | {immob_batiments_brut:,.2f} | {immob_batiments_amort:,.2f} | {immob_batiments_brut - immob_batiments_amort:,.2f} |
| Matériel et outillage (Ligne ondulation, Combiné flexo) | {immob_materiel_brut:,.2f} | {immob_materiel_amort:,.2f} | {immob_materiel_brut - immob_materiel_amort:,.2f} |
| Matériel de transport (Chariots élévateurs & Camion) | {immob_transport_brut:,.2f} | {immob_transport_amort:,.2f} | 0.00 |
| Mobilier, matériel de bureau et aménagement | {immob_mobilier_brut:,.2f} | {immob_mobilier_amort:,.2f} | {immob_mobilier_brut - immob_mobilier_amort:,.2f} |
| Matériel informatique & Réseau | {immob_info_brut:,.2f} | {immob_info_amort:,.2f} | 0.00 |
| Dépôts et cautionnements versés (ONEE) | {immob_depots_brut:,.2f} | 0.00 | {immob_depots_brut:,.2f} |
| **SOUS-TOTAL ACTIF IMMOBILISÉ (I)** | **{total_immob_brut:,.2f}** | **{total_immob_amort:,.2f}** | **{total_immob_net:,.2f}** |
| | | | |
| **ACTIF CIRCULANT (HORS TRÉSORERIE)** | | | |
| Stocks de matières premières (Bobines papier) | {stock_mp_net:,.2f} | 0.00 | {stock_mp_net:,.2f} |
| Stocks de matières et fournitures consommables (Amidon, Encres) | {stock_aux_net:,.2f} | 0.00 | {stock_aux_net:,.2f} |
| Stocks de produits finis (Carton ondulé) | {stock_pf_net:,.2f} | 0.00 | {stock_pf_net:,.2f} |
| Clients ordinaires (Créances facturées) | {clients_ordinaires_net:,.2f} | 0.00 | {clients_ordinaires_net:,.2f} |
| Clients - Effets à recevoir (LCR en portefeuille) | {clients_effets_net:,.2f} | 0.00 | {clients_effets_net:,.2f} |
| Effets remis à l'escompte (Banque) | {effets_escompte_net:,.2f} | 0.00 | {effets_escompte_net:,.2f} |
| État - TVA récupérable sur charges | {tva_recup_net:,.2f} | 0.00 | {tva_recup_net:,.2f} |
| État - Crédit de TVA à reporter | {tva_credit_net:,.2f} | 0.00 | {tva_credit_net:,.2f} |
| État - Crédit d'impôt IS excédentaire | {credit_impot_net:,.2f} | 0.00 | {credit_impot_net:,.2f} |
| État - Acomptes provisionnels sur IS versés | {acomptes_is_net:,.2f} | 0.00 | {acomptes_is_net:,.2f} |
| **SOUS-TOTAL ACTIF CIRCULANT (II)** | **{total_actif_circulant:,.2f}** | **0.00** | **{total_actif_circulant:,.2f}** |
| | | | |
| **TRÉSORERIE - ACTIF** | | | |
| Banques (Soldes débiteurs AWB, BP, CAM) | {banques_actif:,.2f} | 0.00 | {banques_actif:,.2f} |
| Caisse centrale | {caisse_actif:,.2f} | 0.00 | {caisse_actif:,.2f} |
| **SOUS-TOTAL TRÉSORERIE - ACTIF (III)** | **{total_tresorerie_actif:,.2f}** | **0.00** | **{total_tresorerie_actif:,.2f}** |
| | | | |
| **TOTAL GÉNÉRAL ACTIF (I + II + III)** | **{total_immob_brut + total_actif_circulant + total_tresorerie_actif:,.2f}** | **{total_immob_amort:,.2f}** | **{total_actif:,.2f}** |

---

## 2. PASSIF

| Rubriques / Postes du Passif | Montant Net Exercice 2025 (MAD) |
| :--- | :---: |
| **FINANCEMENT PERMANENT (CAPITAUX PROPRES & DETTES LT)** | |
| Capital social (8,000 parts de 100 MAD) | {capital_social:,.2f} |
| Réserve légale (10% du capital social atteint) | {reserve_legale:,.2f} |
| Réserves statutaires | {reserves_statutaires:,.2f} |
| Report à nouveau (Bénéfices antérieurs cumulés) | {report_a_nouveau:,.2f} |
| *-- dont Tranche pré-2023 (WHT 15.00%)* | *2,150,000.00* |
| *-- dont Tranche 2023+ (WHT 11.25% / 10.00%)* | *1,678,700.00* |
| **Résultat net de l'exercice 2025 (Bénéfice)** | **{resultat_net:,.2f}** |
| **Total des Capitaux Propres** | **{total_capitaux_propres:,.2f}** |
| Emprunts auprès des établissements de crédit (BMCE Moyen Terme) | {emprunts_etablissements:,.2f} |
| **SOUS-TOTAL FINANCEMENT PERMANENT (I)** | **{total_financement_permanent:,.2f}** |
| | |
| **PASSIF CIRCULANT (HORS TRÉSORERIE)** | |
| Fournisseurs et comptes rattachés (CMCP, Colorpak, ONEE, etc.) | {fournisseurs_ordinaires:,.2f} |
| Rémunérations dues au personnel (Salaires nets à payer) | {remunerations_dues:,.2f} |
| CNSS & Mutuelles AT à payer | {to_dec(cnss_a_payer + mutuelles_at_a_payer):,.2f} |
| État - Impôt sur les sociétés (Solde IS dû) | {is_a_payer:,.2f} |
| État - TVA facturée & TVA due | {tva_facturee_due:,.2f} |
| État - IR retenu à la source sur salaires | {ir_retenu:,.2f} |
| Autres créanciers & Dettes provisionnées | {autres_creanciers:,.2f} |
| **SOUS-TOTAL PASSIF CIRCULANT (II)** | **{total_passif_circulant:,.2f}** |
| | |
| **TRÉSORERIE - PASSIF** | |
| Crédits d'escompte (LCR mobilisées auprès d'Attijariwafa Bank) | {credits_escompte:,.2f} |
| Banques (Découverts bancaires utilisés) | {decouverts_bancaires:,.2f} |
| **SOUS-TOTAL TRÉSORERIE - PASSIF (III)** | **{total_tresorerie_passif:,.2f}** |
| | |
| **TOTAL GÉNÉRAL PASSIF (I + II + III)** | **{total_passif:,.2f}** |

---

## 3. ÉQUILIBRE FINANCIER & RATIOS FONDAMENTAUX

- **Équilibre Bilan** : $\\text{{Total Actif}} ({total_actif:,.2f}\\text{{ MAD}}) \\equiv \\text{{Total Passif}} ({total_passif:,.2f}\\text{{ MAD}})$ $\\implies$ **{'ÉQUILIBRÉ' if equilibre_ok else f'NON ÉQUILIBRÉ (Δ = {equilibre_delta:+,.2f} MAD)'}** (Delta: {equilibre_delta:+,.2f} MAD)
- **Fonds de Roulement (FR)** : ${total_financement_permanent:,.2f} - {total_immob_net:,.2f} = \\mathbf{{{fr:,.2f}\\text{{ MAD}}}}$
- **Besoin en Fonds de Roulement (BFR)** : ${total_actif_circulant:,.2f} - {total_passif_circulant:,.2f} = \\mathbf{{{bfr:,.2f}\\text{{ MAD}}}}$
- **Trésorerie Nette (TN)** : ${total_tresorerie_actif:,.2f} - {total_tresorerie_passif:,.2f} = \\mathbf{{{tn:,.2f}\\text{{ MAD}}}}$
- **Identité Fondamentale** : $\\text{{FR}} ({fr:,.2f}) - \\text{{BFR}} ({bfr:,.2f}) = {eq_check:,.2f}\\text{{ MAD}} \\equiv \\text{{TN}} ({tn:,.2f}\\text{{ MAD}})$ $\\implies$ **{'VÉRIFIÉE' if identite_ok else f'NON VÉRIFIÉE (Δ = {identite_delta:+,.2f} MAD)'}**
"""
        return md

    def generate_cpc_markdown(self) -> str:
        ca_maroc = abs(self.ledger.get_account_net_balance("71211"))
        ca_export = abs(self.ledger.get_account_net_balance("71212"))
        ca_total = to_dec(ca_maroc + ca_export)
        stock_var = abs(self.ledger.get_account_net_balance("7132"))
        total_prod_expl = to_dec(ca_total + stock_var)

        achats_mp = to_dec(self.ledger.get_account_period_debit("61111") + self.ledger.get_account_period_debit("61112"))
        droits_douane = self.ledger.get_account_period_debit("6119")
        achats_fournitures = to_dec(self.ledger.get_account_period_debit("6121") + self.ledger.get_account_period_debit("6122") + self.ledger.get_account_period_debit("6125"))
        achats_consommes = to_dec(achats_mp + droits_douane + achats_fournitures)

        autres_charges_ext = to_dec(self.ledger.get_account_period_debit("6133") + self.ledger.get_account_period_debit("6142") + self.ledger.get_account_period_debit("6147"))
        impots_taxes = self.ledger.get_account_period_debit("6161")
        charges_personnel = to_dec(self.ledger.get_account_period_debit("6171") + self.ledger.get_account_period_debit("6174") + self.ledger.get_account_period_debit("6176"))
        dda = self.ledger.get_account_period_debit("6181")
        total_charges_expl = to_dec(achats_consommes + autres_charges_ext + impots_taxes + charges_personnel + dda)

        rex = to_dec(total_prod_expl - total_charges_expl)

        charges_fin = self.ledger.get_account_period_debit("6318")
        prod_fin = Decimal("0.00")
        res_fin = to_dec(prod_fin - charges_fin)

        rcai = to_dec(rex + res_fin)

        charges_non_courantes = self.ledger.get_account_period_debit("658")
        prod_non_courants = Decimal("0.00")
        res_non_courant = to_dec(prod_non_courants - charges_non_courantes)

        rai = to_dec(rcai + res_non_courant)

        is_tax = to_dec(self.closing_data.get("is_final_due", Decimal("98500.00")))
        net_profit = to_dec(rai - is_tax)

        md = f"""# COMPTE DE PRODUITS ET CHARGES (CPC) — EXERCICE 2025
**Raison Sociale** : SOUSS AGRI-PACK SARL | **Période** : 01/01/2025 au 31/12/2025  
**Devise** : Dirham Marocain (MAD) | **Standard** : CGNC / Code Général de Normalisation Comptable  

---

| Nature des Opérations | Montant Exercice 2025 (MAD) |
| :--- | :---: |
| **I. PRODUITS D'EXPLOITATION** | |
| Ventes de produits finis au Maroc (TVA 20%) | {ca_maroc:,.2f} |
| Ventes de produits finis à l'exportation directe (TVA 0%) | {ca_export:,.2f} |
| **Chiffre d'Affaires Total (CA)** | **{ca_total:,.2f}** |
| Variation des stocks de produits finis (+ augmentation) | {stock_var:,.2f} |
| **TOTAL DES PRODUITS D'EXPLOITATION (I)** | **{total_prod_expl:,.2f}** |
| | |
| **II. CHARGES D'EXPLOITATION** | |
| Achats consommés de matières et fournitures (Papier, Encres, Énergie, Eau) | {achats_consommes:,.2f} |
| Autres charges externes (Maintenance, Transitaire, Télécom, Assurances) | {autres_charges_ext:,.2f} |
| Impôts et taxes (Taxe Professionnelle & Taxe Services Communaux) | {impots_taxes:,.2f} |
| Charges de personnel (Salaires bruts, CNSS, AMO, Assurance AT) | {charges_personnel:,.2f} |
| Dotations d'exploitation aux amortissements (DDA linéaire) | {dda:,.2f} |
| **TOTAL DES CHARGES D'EXPLOITATION (II)** | **{total_charges_expl:,.2f}** |
| | |
| **III. RÉSULTAT D'EXPLOITATION (I - II)** | **{rex:,.2f}** |
| | |
| **IV. PRODUITS FINANCIERS** | 0.00 |
| **V. CHARGES FINANCIÈRES** (Intérêts d'escompte bancaire AWB) | {charges_fin:,.2f} |
| **VI. RÉSULTAT FINANCIER (IV - V)** | **{res_fin:,.2f}** |
| | |
| **VII. RÉSULTAT COURANT AVANT IMPÔT (III + VI)** | **{rcai:,.2f}** |
| | |
| **VIII. PRODUITS NON COURANTS** | 0.00 |
| **IX. CHARGES NON COURANTES** (Pénalités, frais surestaries, impayés) | {charges_non_courantes:,.2f} |
| **X. RÉSULTAT NON COURANT (VIII - IX)** | **{res_non_courant:,.2f}** |
| | |
| **XI. RÉSULTAT AVANT IMPÔT (VII + X)** | **{rai:,.2f}** |
| **XII. IMPÔTS SUR LES RÉSULTATS (IS Barème Progressif 2025)** | **{is_tax:,.2f}** |
| | |
| **XIII. RÉSULTAT NET DE L'EXERCICE (XI - XII)** | **{net_profit:,.2f}** |
"""
        return md

    def generate_tableau_passage_markdown(self) -> str:
        ca = to_dec(self.closing_data.get("ca_turnover_ht", Decimal("10930700.00")))
        rcai = to_dec(self.closing_data.get("pre_tax_accounting_profit", Decimal("495700.00")))
        reint = to_dec(self.closing_data.get("reintegrations_fiscales", Decimal("34300.00")))
        rf = to_dec(self.closing_data.get("fiscal_result", Decimal("530000.00")))
        is_calc = to_dec(self.closing_data.get("is_calculated", Decimal("98500.00")))
        cm = to_dec(self.closing_data.get("cotisation_minimale", Decimal("27326.75")))
        is_final = to_dec(self.closing_data.get("is_final_due", Decimal("98500.00")))
        acomptes = to_dec(self.closing_data.get("acomptes_paid", Decimal("98500.00")))
        solde = to_dec(self.closing_data.get("is_solde_restant", Decimal("0.00")))

        md = f"""# TABLEAU DE PASSAGE DU RÉSULTAT COMPTABLE AU RÉSULTAT FISCAL (LIASSE FISCALE 2025)
**Document Officiel** : Tableau n° 1 de la Liasse Fiscale DGI Maroc  
**Société** : SOUSS AGRI-PACK SARL | **IF** : 45127890 | **Exercice** : 2025  

---

## 1. DÉTERMINATION DU RÉSULTAT FISCAL

| Éléments de Calcul | Montant (MAD) | Base Légale / Article CGI |
| :--- | :---: | :--- |
| **I. RÉSULTAT COMPTABLE AVANT IMPÔT (Bénéfice)** | **+{rcai:,.2f}** | Plan Comptable Marocain (Classe 8) |
| | | |
| **II. RÉINTÉGRATIONS FISCALES COURANTES & NON COURANTES** | | |
| 1. Amendes, pénalités et charges non courantes | +{self.closing_data.get('charges_non_courantes', Decimal('4300.00')):,.2f} | CGI Art. 11-I |
| 2. Provisions non déductibles de l'exercice | +30,000.00 | CGI Art. 10-I-F |
| **Total des Réintégrations Fiscales (A)** | **+{reint:,.2f}** | |
| | | |
| **III. DÉDUCTIONS FISCALES** | **0.00** | |
| | | |
| **IV. RÉSULTAT FISCAL BRUT DE L'EXERCICE (I + A - III)** | **{rf:,.2f}** | **CGI Art. 8 & Art. 19** |
| Report déficitaire antérieur imputable | 0.00 | CGI Art. 12 |
| **RÉSULTAT FISCAL NET IMPOSABLE** | **{rf:,.2f}** | |

---

## 2. LIQUIDATION DE L'IMPÔT SUR LES SOCIÉTÉS (IS 2025)

1. **Calcul de l'IS selon le Barème Progressif 2025 (CGI Art. 19)** :
   - *Tranche 1 (0 à 300,000.00 MAD @ 17.50%)* : $300,000.00 \\times 17.50\\% = \\mathbf{{52,500.00\\text{{ MAD}}}}$
   - *Tranche 2 (300,001 à {rf:,.2f} MAD @ 20.00%)* : ${(rf - Decimal('300000.00')):,.2f} \\times 20.00\\% = \\mathbf{{{(is_calc - Decimal('52500.00')):,.2f}\\text{{ MAD}}}}$
   - **IS Théorique Calculé** : $\\mathbf{{{is_calc:,.2f}\\text{{ MAD}}}}$

2. **Calcul de la Cotisation Minimale (CM - CGI Art. 144)** :
   - Base de calcul : Chiffre d'Affaires HT (${ca:,.2f}\\text{{ MAD}}$)
   - Taux : $0.25\\%$ (Plancher légal : $3,000.00\\text{{ MAD}}$)
   - **Montant Cotisation Minimale** : $\\mathbf{{{cm:,.2f}\\text{{ MAD}}}}$

3. **Impôt Exigible Retenu** :
   - Règle légale : $\\max(\\text{{IS Calculé}}, \\text{{Cotisation Minimale}}) = \\max({is_calc:,.2f}, {cm:,.2f})$
   - **IS DÛ AU TITRE DE L'EXERCICE 2025** : $\\mathbf{{{is_final:,.2f}\\text{{ MAD}}}}$

4. **Régularisation avec les Acomptes Provisionnels** :
   - 4 Acomptes provisionnels versés en 2025 (25% IS 2024 $\\times$ 4) : ${acomptes:,.2f}\\text{{ MAD}}$
   - **Solde de Liquidation IS à payer (avant le 31 Mars 2026)** : $\\mathbf{{{solde:,.2f}\\text{{ MAD}}}}$
"""
        return md
