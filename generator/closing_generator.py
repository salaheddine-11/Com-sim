# -*- coding: utf-8 -*-
"""
Year-End Closing, Depreciation, Fiscal Result Reconciliation, and IS Liquidation Engine.
Posts all closing entries dynamically through journal_templates.yaml using Decimal.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, Any

from generator.models import to_dec
from generator.pcm_ledger_engine import PCMLedgerEngine
from generator.parameters_engine import ParameterEngine


class ClosingGenerator:
    def __init__(self, ledger: PCMLedgerEngine, param_engine: ParameterEngine):
        self.ledger = ledger
        self.param_engine = param_engine
        self.journal_counter = 4000

    def execute_year_end_closing(self, closing_date: date = date(2025, 12, 31)) -> Dict[str, Any]:
        year = closing_date.year

        # 1. Fixed Asset Linear Depreciation (EVT-CLS-001)
        dda_buildings = Decimal("110000.00")
        dda_machinery = Decimal("220000.00")
        dda_vehicles = Decimal("22500.00")
        dda_furniture = Decimal("12000.00")
        dda_it = Decimal("15500.00")

        entry_id_dda = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        ctx_dda = {
            "dda_buildings": dda_buildings,
            "dda_machinery": dda_machinery,
            "dda_vehicles": dda_vehicles,
            "dda_furniture": dda_furniture,
            "dda_it": dda_it
        }
        self.ledger.post_event("EVT-CLS-001", entry_id_dda, closing_date, f"DDA-ANNUEL-{year}", ctx_dda, f"Dotations aux amortissements de l'exercice {year}")

        # 2. Compute P&L Totals and Pre-tax Profit from Ledgers
        ca_sales_maroc = abs(self.ledger.get_account_net_balance("71211"))
        ca_sales_export = abs(self.ledger.get_account_net_balance("71212"))
        ca_turnover = to_dec(ca_sales_maroc + ca_sales_export)
        stock_var_prod = abs(self.ledger.get_account_net_balance("7132"))
        total_produits = to_dec(ca_turnover + stock_var_prod)

        # Operating charges
        charges_mp_dom = self.ledger.get_account_period_debit("61111")
        charges_mp_imp = self.ledger.get_account_period_debit("61112")
        charges_customs = self.ledger.get_account_period_debit("6119")
        charges_consumables = self.ledger.get_account_period_debit("6121")
        charges_fuel = self.ledger.get_account_period_debit("6122")
        charges_utilities = self.ledger.get_account_period_debit("6125")
        charges_maintenance = self.ledger.get_account_period_debit("6133")
        charges_transport = self.ledger.get_account_period_debit("6142")
        charges_bank_fees = self.ledger.get_account_period_debit("6147")
        charges_local_taxes = self.ledger.get_account_period_debit("6161")
        charges_personnel = self.ledger.get_account_period_debit("6171")
        charges_social = self.ledger.get_account_period_debit("6174")
        charges_at = self.ledger.get_account_period_debit("6176")
        charges_dda = self.ledger.get_account_period_debit("6181")

        # Financial charges
        charges_interest = self.ledger.get_account_period_debit("6318")

        # Non-current charges (Penalties / Demurrage / Losses)
        charges_non_courantes = self.ledger.get_account_period_debit("658")

        total_charges_exploitation = to_dec(
            charges_mp_dom + charges_mp_imp + charges_customs + charges_consumables +
            charges_fuel + charges_utilities + charges_maintenance + charges_transport +
            charges_bank_fees + charges_local_taxes + charges_personnel + charges_social +
            charges_at + charges_dda
        )
        total_charges = to_dec(total_charges_exploitation + charges_interest + charges_non_courantes)

        pre_tax_accounting_profit = to_dec(total_produits - total_charges)

        # 3. Fiscal Result Reconciliation (Tableau de passage)
        # Reintegrations: Non-deductible tax/social penalties and non-deductible provisions
        reintegrations = to_dec(charges_non_courantes + Decimal("30000.00"))  # provisions conges
        fiscal_result = to_dec(pre_tax_accounting_profit + reintegrations)

        # 4. Corporate Income Tax (IS) Calculation - Progressive Barème 2025
        # Tranche 1: <= 300,000 @ 17.50%
        # Tranche 2: 300,001 to 1,000,000 @ 20.00%
        slice_300k = Decimal("300000.00")
        if fiscal_result <= slice_300k:
            is_calculated = to_dec(fiscal_result * Decimal("0.1750"))
        else:
            is_tranche1 = to_dec(slice_300k * Decimal("0.1750"))
            is_tranche2 = to_dec((fiscal_result - slice_300k) * Decimal("0.2000"))
            is_calculated = to_dec(is_tranche1 + is_tranche2)

        # Cotisation Minimale (0.25% of CA HT, floor 3000 MAD)
        cm_rate = self.param_engine.get_decimal("cotisation_minimale_rate", closing_date)
        cm_floor = self.param_engine.get_decimal("cotisation_minimale_floor_mad", closing_date)
        cotisation_minimale = max(cm_floor, to_dec(ca_turnover * (cm_rate / Decimal("100.00"))))

        is_final_due = max(is_calculated, cotisation_minimale)

        # 5. Liquidate IS via EVT-TAX-004
        acomptes_paid = self.ledger.get_account_net_balance("3453")
        is_solde_restant = to_dec(is_final_due - acomptes_paid)

        entry_id_is = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        ctx_is = {
            "total_is_due": is_final_due,
            "sum_4_acomptes": acomptes_paid
        }
        self.ledger.post_event("EVT-TAX-004", entry_id_is, closing_date, f"IS-CLO-{year}", ctx_is, f"Liquidation annuelle IS {year}")

        # 6. Net Accounting Profit & Transfer (EVT-CLS-006)
        net_profit = to_dec(pre_tax_accounting_profit - is_final_due)

        entry_id_res = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        self.ledger.post_event("EVT-CLS-006", entry_id_res, closing_date, f"RES-NET-{year}", {"net_accounting_profit": net_profit}, f"Bénéfice net après impôts {year}")

        return {
            "ca_turnover_ht": ca_turnover,
            "total_produits": total_produits,
            "total_charges": total_charges,
            "charges_non_courantes": charges_non_courantes,
            "pre_tax_accounting_profit": pre_tax_accounting_profit,
            "reintegrations_fiscales": reintegrations,
            "fiscal_result": fiscal_result,
            "is_calculated": is_calculated,
            "cotisation_minimale": cotisation_minimale,
            "is_final_due": is_final_due,
            "acomptes_paid": acomptes_paid,
            "is_solde_restant": is_solde_restant,
            "net_profit": net_profit
        }
