# -*- coding: utf-8 -*-
"""
Treasury, Banking & Cash Management Engine for Souss Agri-Pack SARL.
Simulates bank accounts (AWB, BP, CAM), discounting (escompte), agios, settlements, and collections.
Posts all journal entries dynamically through journal_templates.yaml using Decimal.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
import random

from generator.models import (
    CommercialPaper, SalesInvoice, PurchaseInvoice,
    PaymentMethod, to_dec, to_dec_4dp
)
from generator.pcm_ledger_engine import PCMLedgerEngine
from generator.parameters_engine import ParameterEngine


class TreasuryGenerator:
    def __init__(self, ledger: PCMLedgerEngine, param_engine: ParameterEngine, seed: int = 44):
        self.ledger = ledger
        self.param_engine = param_engine
        self.rng = random.Random(seed)
        self.journal_counter = 2000

    def process_escompte_discounting(self, paper_batch: List[CommercialPaper], discount_date: date) -> List[CommercialPaper]:
        bam_key_rate = self.param_engine.get_decimal("bam_key_rate", discount_date)
        discount_rate = bam_key_rate + Decimal("0.0350")  # e.g. 2.25% + 3.50% = 5.75%
        discounted_papers = []

        for paper in paper_batch:
            if paper.status != "PORTFOLIO":
                continue

            days = max(15, (paper.due_date - discount_date).days)
            nominal = paper.nominal_amount_mad

            # Interêts d'escompte
            interet = to_dec((nominal * discount_rate * Decimal(str(days))) / Decimal("360.00"))
            # Commission d'endos (0.60%) + frais dossier (50 MAD)
            endos = to_dec(nominal * Decimal("0.0060"))
            service = Decimal("50.00")
            fees_ht = to_dec(endos + service)
            # TVA 10% sur agios (CGI Art. 99-3)
            tva_10 = to_dec((interet + fees_ht) * Decimal("0.10"))
            total_agio = to_dec(interet + fees_ht + tva_10)
            net_cash = to_dec(nominal - total_agio)

            paper.status = "DISCOUNTED"
            paper.bank_discounted = "Attijariwafa Bank"
            paper.discount_date = discount_date
            paper.agio_interet_mad = interet
            paper.agio_endos_mad = endos
            paper.agio_service_mad = service
            paper.agio_tva_10_mad = tva_10
            paper.total_agio_mad = total_agio
            paper.net_cash_received_mad = net_cash
            discounted_papers.append(paper)

            # Step 1: EVT-BNK-002 (Transfer from 3424 to 5115 - Effets remis à l'escompte)
            entry_id_remise = f"JRN-{discount_date.year}-{self.journal_counter:05d}"
            self.journal_counter += 1
            self.ledger.post_event("EVT-BNK-002", entry_id_remise, discount_date, f"REM-{paper.effet_id}", {"lcn_nominal": nominal}, f"Remise escompte LCR {paper.effet_id}")

            # Step 2: EVT-BNK-003 (Credit in AWB + Agios + TVA 10% -> 5520)
            entry_id_credit = f"JRN-{discount_date.year}-{self.journal_counter:05d}"
            self.journal_counter += 1
            ctx_escompte = {
                "lcn_nominal": nominal,
                "total_agio_ttc": total_agio,
                "discount_interest_ht": interet,
                "banking_fees_ht": fees_ht,
                "agio_tva_10": tva_10
            }
            self.ledger.post_event("EVT-BNK-003", entry_id_credit, discount_date, f"BDC-{paper.effet_id}", ctx_escompte, f"Crédit escompte AWB LCR {paper.effet_id}")

        return discounted_papers

    def process_commercial_paper_maturities(self, current_date: date, papers: List[CommercialPaper]):
        for paper in papers:
            if paper.due_date == current_date:
                # Check for default (CLI-011 in Sep)
                if paper.customer_id == "CLI-011" and current_date.month == 9 and paper.status != "IMPAYE":
                    paper.status = "IMPAYE"
                    reject_fee_ht = Decimal("1500.00")
                    reject_fee_tva = Decimal("150.00")

                    entry_id_imp = f"JRN-{current_date.year}-{self.journal_counter:05d}"
                    self.journal_counter += 1
                    ctx_imp = {
                        "lcn_nominal": paper.nominal_amount_mad,
                        "reject_fee_ht": reject_fee_ht,
                        "reject_fee_tva": reject_fee_tva
                    }
                    self.ledger.post_event("EVT-BNK-005", entry_id_imp, current_date, f"IMP-{paper.effet_id}", ctx_imp, f"Impayé effet LCR {paper.effet_id}")
                    continue

                if paper.status == "DISCOUNTED":
                    paper.status = "COLLECTED_AT_MATURITY"
                    entry_id_ech = f"JRN-{current_date.year}-{self.journal_counter:05d}"
                    self.journal_counter += 1
                    self.ledger.post_event("EVT-BNK-004", entry_id_ech, current_date, f"ECH-{paper.effet_id}", {"lcn_nominal": paper.nominal_amount_mad}, f"Extinction normale LCR {paper.effet_id}")


    def process_supplier_payments(self, current_date: date, purchase_invoices: List[PurchaseInvoice]):
        for pinv in purchase_invoices:
            if pinv.due_date == current_date and pinv.status == "PENDING":
                pinv.status = "PAID"
                entry_id = f"JRN-{current_date.year}-{self.journal_counter:05d}"
                self.journal_counter += 1
                self.ledger.post_event("EVT-BNK-006", entry_id, current_date, f"PAY-{pinv.invoice_number}", {"payment_amount": pinv.amount_ttc_mad}, f"Règlement Fournisseur {pinv.supplier_name}")

    def process_monthly_payroll_disbursement(self, current_date: date, year: int, month: int):
        net_salaries_due = self.ledger.get_account_net_balance("4432")
        if net_salaries_due < Decimal("0.00"):
            amount = abs(net_salaries_due)
            entry_id = f"JRN-{year}-{self.journal_counter:05d}"
            self.journal_counter += 1
            self.ledger.post_event("EVT-PAY-004", entry_id, current_date, f"VIR-SAL-{year}-{month:02d}", {"net_salaries_payable": amount}, f"Paiement net salaires {month:02d}/{year}")
