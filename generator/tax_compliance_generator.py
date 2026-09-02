# -*- coding: utf-8 -*-
"""
Tax & Regulatory Compliance Generator for Souss Agri-Pack SARL.
Handles SIMPL-TVA liquidations, Damancom CNSS payments, SIMPL-IR, IS acomptes, and local taxes.
Posts all journal entries dynamically through journal_templates.yaml using Decimal.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Tuple

from generator.models import to_dec
from generator.pcm_ledger_engine import PCMLedgerEngine
from generator.parameters_engine import ParameterEngine


class TaxComplianceGenerator:
    def __init__(self, ledger: PCMLedgerEngine, param_engine: ParameterEngine):
        self.ledger = ledger
        self.param_engine = param_engine
        self.journal_counter = 3000
        self.prior_is_acompte_quarterly_mad = Decimal("24625.00")  # 25% of 2024 IS (98,500 MAD)

    def process_monthly_cnss_payment(self, current_date: date, year: int, month: int):
        cnss_due = self.ledger.get_account_net_balance("4441")
        if cnss_due < Decimal("0.00"):
            amount = abs(cnss_due)
            entry_id = f"JRN-{year}-{self.journal_counter:05d}"
            self.journal_counter += 1
            self.ledger.post_event("EVT-PAY-005", entry_id, current_date, f"DAMANCOM-{year}-{month:02d}", {"total_cnss_due": amount}, f"Télé-règlement Damancom CNSS {month:02d}/{year}")

    def process_monthly_ir_payment(self, current_date: date, year: int, month: int):
        ir_due = self.ledger.get_account_net_balance("4457")
        if ir_due < Decimal("0.00"):
            amount = abs(ir_due)
            entry_id = f"JRN-{year}-{self.journal_counter:05d}"
            self.journal_counter += 1
            self.ledger.post_event("EVT-PAY-006", entry_id, current_date, f"SIMPL-IR-{year}-{month:02d}", {"ir_withheld_total": amount}, f"Paiement SIMPL-IR {month:02d}/{year}")

    def process_monthly_tva_liquidation(self, current_date: date, year: int, month: int):
        tva_facturee_bal = self.ledger.get_account_net_balance("4455")
        tva_recup_bal = self.ledger.get_account_net_balance("3451")

        tva_facturee = abs(tva_facturee_bal) if tva_facturee_bal < Decimal("0.00") else Decimal("0.00")
        tva_recup = tva_recup_bal if tva_recup_bal > Decimal("0.00") else Decimal("0.00")

        if tva_facturee == Decimal("0.00") and tva_recup == Decimal("0.00"):
            return

        net_tva = to_dec(tva_facturee - tva_recup)

        if net_tva >= Decimal("0.00"):
            # Step 1: EVT-TAX-001 (Liquidation TVA Facturée vs Récupérable -> TVA due)
            entry_id_liq = f"JRN-{year}-{self.journal_counter:05d}"
            self.journal_counter += 1
            ctx_liq = {
                "tva_collectee_total": tva_facturee,
                "tva_deductible_charges": tva_recup,
                "tva_deductible_immob": Decimal("0.00")
            }
            self.ledger.post_event("EVT-TAX-001", entry_id_liq, current_date, f"LIQ-TVA-{year}-{month:02d}", ctx_liq, f"Liquidation SIMPL-TVA {month:02d}/{year}")

            # Step 2: If not December (year-end accrual), pay TVA due in cash
            if month != 12 and net_tva > Decimal("0.00"):
                entry_id_pay = f"JRN-{year}-{self.journal_counter:05d}"
                self.journal_counter += 1
                self.ledger.post_event("EVT-TAX-002", entry_id_pay, current_date, f"PAY-TVA-{year}-{month:02d}", {"tva_due_net": net_tva}, f"Télépaiement SIMPL-TVA {month:02d}/{year}")

    def process_quarterly_is_acompte(self, current_date: date, quarter_num: int, year: int):
        amount = self.prior_is_acompte_quarterly_mad
        entry_id = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        self.ledger.post_event("EVT-TAX-003", entry_id, current_date, f"IS-ACOMPTE-{year}-Q{quarter_num}", {"acompte_amount": amount}, f"Paiement {quarter_num}e acompte IS {year}")

    def process_prior_year_is_solde(self, current_date: date, year: int):
        is_solde_due = abs(self.ledger.get_account_net_balance("4452"))
        if is_solde_due > Decimal("0.00"):
            entry_id = f"JRN-{year}-{self.journal_counter:05d}"
            self.journal_counter += 1
            # Settle 4452 vs 51411 (AWB)
            self.ledger.post_event("EVT-BNK-006", entry_id, current_date, f"IS-SOLDE-2024", {"payment_amount": is_solde_due}, f"Règlement Solde IS 2024")

    def process_annual_local_taxes(self, current_date: date, year: int):
        tp_rate = self.param_engine.get_decimal("taxe_professionnelle_rate", current_date)
        tsc_rate = self.param_engine.get_decimal("taxe_services_communaux_rate", current_date)
        valeur_locative = Decimal("222000.00")

        tp_amount = to_dec(valeur_locative * (tp_rate / Decimal("100.00")))
        tsc_amount = to_dec(valeur_locative * (tsc_rate / Decimal("100.00")))

        entry_id = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        ctx = {
            "tp_amount": tp_amount,
            "tsc_amount": tsc_amount
        }
        self.ledger.post_event("EVT-TAX-005", entry_id, current_date, f"TP-TSC-{year}", ctx, f"Paiement TP ({tp_amount}) + TSC ({tsc_amount}) {year}")
