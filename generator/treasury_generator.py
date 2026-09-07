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
    def __init__(self, ledger: PCMLedgerEngine, param_engine: ParameterEngine, seed: int = 44,
                 invoice_index: Optional[Dict[str, SalesInvoice]] = None,
                 invoice_source: Optional[Dict[str, SalesInvoice]] = None):
        self.ledger = ledger
        self.param_engine = param_engine
        self.rng = random.Random(seed)
        # Plage dédiée (20000+) pour éviter toute collision d'entry_id avec les
        # autres générateurs (ventes ~0002-0600, achats ~0500, paie ~1000, taxes ~3000).
        self.journal_counter = 20000
        # Index facture par numéro + index par pièce d'effet (ENC-/RET-...)
        # NB: test "is not None" — un dict vide reste un index valide (falsy mais fonctionnel).
        self._invoice_index = invoice_index if invoice_index is not None else {}
        self._invoice_source = invoice_source if invoice_source is not None else {}

    def process_escompte_discounting(self, paper_batch: List[CommercialPaper], discount_date: date) -> List[CommercialPaper]:
        bam_key_rate = self.param_engine.get_decimal("bam_key_rate", discount_date)
        discount_rate = bam_key_rate + Decimal("0.0350")  # e.g. 2.25% + 3.50% = 5.75%
        discounted_papers = []

        for paper in paper_batch:
            # Chronologie stricte : seul un effet déjà créé (draw_date passée ou présente)
            # et toujours en portefeuille peut être remis à l'escompte à cette date.
            if paper.status != "PORTFOLIO":
                continue
            if paper.draw_date > discount_date:
                continue
            if paper.due_date <= discount_date:
                # Un effet échu ou à échéance du jour ne se remet pas à l'escompte.
                continue

            days = (paper.due_date - discount_date).days
            # Durée minimale d'escompte bancaire : en dessous de 15 jours, la remise
            # est refusée ; l'effet dénouera en portefeuille (EVT-BNK-009).
            if days < 15:
                continue
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
            paper.status_orig = "DISCOUNTED"
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

    def _settle_invoice(self, invoice: SalesInvoice, status: str) -> None:
        """Met à jour le statut de la facture source au dénouement de son effet."""
        if invoice is not None and invoice.status not in ("PAID", "DEFAULTED"):
            invoice.status = status

    def _find_invoice(self, invoice_number: str) -> Optional[SalesInvoice]:
        inv = self._invoice_index.get(invoice_number)
        if inv is None:
            inv = self._invoice_source.get(invoice_number)
        return inv

    def process_commercial_paper_maturities(self, current_date: date, papers: List[CommercialPaper]):
        for paper in papers:
            if paper.due_date != current_date:
                continue

            invoice = self._find_invoice(paper.invoice_number)

            # Cas 1 : impayé programmé (CLI-011 en septembre)
            if paper.customer_id == "CLI-011" and current_date.month == 9 and paper.status != "IMPAYE":
                paper.status = "IMPAYE"
                reject_fee_ht = Decimal("1500.00")
                reject_fee_tva = Decimal("150.00")

                if paper.status_orig == "DISCOUNTED":
                    # L'effet était escompté : la banque débite le compte avec frais de rejet.
                    entry_id_imp = f"JRN-{current_date.year}-{self.journal_counter:05d}"
                    self.journal_counter += 1
                    ctx_imp = {
                        "lcn_nominal": paper.nominal_amount_mad,
                        "reject_fee_ht": reject_fee_ht,
                        "reject_fee_tva": reject_fee_tva
                    }
                    self.ledger.post_event("EVT-BNK-005", entry_id_imp, current_date, f"IMP-{paper.effet_id}", ctx_imp, f"Impayé effet LCR {paper.effet_id}")
                else:
                    # Effet non escompté : rentrée en créance ordinaire, sans intervention bancaire.
                    entry_id_ret = f"JRN-{current_date.year}-{self.journal_counter:05d}"
                    self.journal_counter += 1
                    self.ledger.post_event(
                        "EVT-BNK-013", entry_id_ret, current_date, f"RET-{paper.effet_id}",
                        {"lcn_nominal": paper.nominal_amount_mad},
                        f"Effet impayé rentré en créance LCR {paper.effet_id}"
                    )

                self._settle_invoice(invoice, "DEFAULTED")
                continue

            # Cas 2 : effet escompté dénoué normalement (la banque se rembourse)
            if paper.status == "DISCOUNTED":
                paper.status = "COLLECTED_AT_MATURITY"
                entry_id_ech = f"JRN-{current_date.year}-{self.journal_counter:05d}"
                self.journal_counter += 1
                self.ledger.post_event("EVT-BNK-004", entry_id_ech, current_date, f"ECH-{paper.effet_id}", {"lcn_nominal": paper.nominal_amount_mad}, f"Extinction normale LCR {paper.effet_id}")
                self._settle_invoice(invoice, "PAID")
                continue

            # Cas 3 : effet en portefeuille (non escompté) encaissé normalement à l'échéance
            if paper.status == "PORTFOLIO":
                paper.status = "COLLECTED_AT_MATURITY"
                entry_id_col = f"JRN-{current_date.year}-{self.journal_counter:05d}"
                self.journal_counter += 1
                self.ledger.post_event(
                    "EVT-BNK-009", entry_id_col, current_date, f"ENC-{paper.effet_id}",
                    {"lcn_nominal": paper.nominal_amount_mad},
                    f"Encaissement effet LCR {paper.effet_id}"
                )
                self._settle_invoice(invoice, "PAID")

    def process_customer_settlements(self, current_date: date, invoices: List[SalesInvoice]):
        """Règlements clients sans effet (virement, chèque, espèces) au terme de la facture."""
        for inv in invoices:
            if inv.due_date != current_date:
                continue
            if inv.status in ("PAID", "DEFAULTED", "COMMERCIAL_PAPER_DRAWN", "DISCOUNTED"):
                continue
            if inv.is_export:
                continue  # Encaissements export hors périmètre bancaire marocain simulé
            method = inv.payment_method
            if method == PaymentMethod.VIREMENT30:
                event_id = "EVT-BNK-010"
                piece_prefix = "VIR"
            elif method == PaymentMethod.CHEQUE:
                event_id = "EVT-BNK-012"
                piece_prefix = "CHQ"
            elif method == PaymentMethod.CASH:
                event_id = "EVT-BNK-011"
                piece_prefix = "CAI"
            else:
                continue

            entry_id = f"JRN-{current_date.year}-{self.journal_counter:05d}"
            self.journal_counter += 1
            self.ledger.post_event(
                event_id, entry_id, current_date, f"{piece_prefix}-{inv.invoice_number}",
                {"amount_ttc": inv.total_ttc},
                f"Encaissement client {inv.invoice_number} ({method.value})"
            )
            inv.status = "PAID"

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
