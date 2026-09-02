# -*- coding: utf-8 -*-
"""
PCM Double-Entry Accounting Ledger Engine for Souss Agri-Pack SARL.
Resolves and posts all journal entries dynamically through config/journal_templates.yaml.
Uses Decimal throughout for 100% cent-level balance invariance.
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
import yaml
import os

from generator.models import JournalCode, JournalEntry, JournalLine, to_dec


@dataclass
class AccountMeta:
    account_number: str
    account_title: str
    class_code: int
    level: str
    normal_balance: str  # "DR" or "CR"
    statement_type: str  # "BILAN_ACTIF", "BILAN_PASSIF", "CPC_CHARGE", "CPC_PRODUIT"


@dataclass
class AccountLedgerRecord:
    account_number: str
    account_title: str
    opening_debit: Decimal = Decimal("0.00")
    opening_credit: Decimal = Decimal("0.00")
    period_debit: Decimal = Decimal("0.00")
    period_credit: Decimal = Decimal("0.00")
    entries: List[Tuple[date, str, str, Decimal, Decimal]] = field(default_factory=list)

    @property
    def total_debit(self) -> Decimal:
        return to_dec(self.opening_debit + self.period_debit)

    @property
    def total_credit(self) -> Decimal:
        return to_dec(self.opening_credit + self.period_credit)

    @property
    def final_debit_balance(self) -> Decimal:
        net = self.total_debit - self.total_credit
        return to_dec(net) if net > Decimal("0.00") else Decimal("0.00")

    @property
    def final_credit_balance(self) -> Decimal:
        net = self.total_credit - self.total_debit
        return to_dec(net) if net > Decimal("0.00") else Decimal("0.00")

    @property
    def net_balance(self) -> Decimal:
        """Positive for net debit, negative for net credit."""
        return to_dec(self.total_debit - self.total_credit)


class PCMLedgerEngine:
    def __init__(self, chart_of_accounts_path: str, journal_templates_path: str):
        self.accounts_meta: Dict[str, AccountMeta] = {}
        self.ledger: Dict[str, AccountLedgerRecord] = {}
        self.templates_by_event: Dict[str, Dict[str, Any]] = {}
        self.journal: List[JournalEntry] = []
        self.auxiliary_ledgers: Dict[str, Dict[str, Decimal]] = {
            "clients": {},
            "fournisseurs": {}
        }
        self._load_chart_of_accounts(chart_of_accounts_path)
        self._load_journal_templates(journal_templates_path)

    def _load_chart_of_accounts(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for acc in data.get("chart_of_accounts", []):
            num = str(acc["account_number"])
            meta = AccountMeta(
                account_number=num,
                account_title=acc.get("account_title", ""),
                class_code=int(acc.get("class_code", num[0])),
                level=acc.get("level", "SOUS_COMPTE"),
                normal_balance=acc.get("normal_balance", "DR"),
                statement_type=acc.get("statement_type", "BILAN_ACTIF")
            )
            self.accounts_meta[num] = meta
            self.ledger[num] = AccountLedgerRecord(
                account_number=num,
                account_title=meta.account_title
            )

    def _load_journal_templates(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for tpl in data.get("journal_templates", []):
            eid = tpl["event_id"]
            self.templates_by_event[eid] = tpl

    def get_account_meta(self, account_number: str) -> AccountMeta:
        num = str(account_number)
        if num not in self.accounts_meta:
            raise KeyError(f"CRITICAL ACCOUNTING ERROR: Account number '{num}' does NOT exist in Chart of Accounts!")
        return self.accounts_meta[num]

    def load_opening_balance_sheet(self, opening_bs_path: str):
        """Loads opening balance sheet with exact Decimal balances."""
        with open(opening_bs_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        opening_lines = []

        # Account normalization map from 4-digit opening to 8-digit operational accounts
        norm_map = {
            "2111": "21110000",
            "2311": "23110000",
            "2321": "23210000",
            "2332": "23320000",
            "2340": "23400000",
            "2351": "23510000",
            "2352": "23520000",
            "2481": "24810000",
            "3111": "31110000",
            "3121": "31210000",
            "3421": "34210000",
            "3455": "34550000",
            "5141": "51411000",
            "5161": "51611000",
            "1111": "11110000",
            "1140": "11400000",
            "1151": "11510000",
            "1191": "11611000",
            "1481": "14810000",
            "4411": "44110000",
            "4441": "44410000",
            "4452": "44530000",
            "4455": "44550000",
            "4457": "44571000",
            "4488": "44880000",
            "5520": "55200000",
        }

        amort_map = {
            "2111": "28110000",
            "2321": "28321000",
            "2332": "28332000",
            "2340": "28340000",
            "2351": "28351000",
            "2352": "28352000",
        }

        # Actif immobilisé
        for acc in data.get("actif", {}).get("actif_immobilise", {}).get("comptes", []):
            raw_num = str(acc["account_number"])
            num = norm_map.get(raw_num, raw_num)
            brut = to_dec(acc.get("montant_brut_mad", 0.0))
            amort = to_dec(acc.get("amortissements_mad", 0.0))
            title = self.get_account_meta(num).account_title
            if brut > Decimal("0.00"):
                self.ledger[num].opening_debit += brut
                opening_lines.append(JournalLine(num, title, brut, Decimal("0.00"), "Bilan d'ouverture 2025"))
            if amort > Decimal("0.00"):
                amort_num = amort_map.get(raw_num, "28" + num[2:])
                amort_title = self.get_account_meta(amort_num).account_title
                self.ledger[amort_num].opening_credit += amort
                opening_lines.append(JournalLine(amort_num, amort_title, Decimal("0.00"), amort, "Bilan d'ouverture 2025"))

        # Actif circulant
        for acc in data.get("actif", {}).get("actif_circulant_hors_tresorerie", {}).get("comptes", []):
            raw_num = str(acc["account_number"])
            num = norm_map.get(raw_num, raw_num)
            net = to_dec(acc.get("montant_net_mad", 0.0))
            title = self.get_account_meta(num).account_title
            if net > Decimal("0.00"):
                self.ledger[num].opening_debit += net
                opening_lines.append(JournalLine(num, title, net, Decimal("0.00"), "Bilan d'ouverture 2025"))

        # Trésorerie actif
        for acc in data.get("actif", {}).get("tresorerie_actif", {}).get("comptes", []):
            raw_num = str(acc["account_number"])
            num = norm_map.get(raw_num, raw_num)
            net = to_dec(acc.get("montant_net_mad", 0.0))
            title = self.get_account_meta(num).account_title
            if net > Decimal("0.00"):
                self.ledger[num].opening_debit += net
                opening_lines.append(JournalLine(num, title, net, Decimal("0.00"), "Bilan d'ouverture 2025"))

        # Financement permanent (Passif)
        for acc in data.get("passif", {}).get("financement_permanent", {}).get("comptes", []):
            raw_num = str(acc["account_number"])
            num = norm_map.get(raw_num, raw_num)
            net = to_dec(acc.get("montant_net_mad", 0.0))
            title = self.get_account_meta(num).account_title
            if net > Decimal("0.00"):
                self.ledger[num].opening_credit += net
                opening_lines.append(JournalLine(num, title, Decimal("0.00"), net, "Bilan d'ouverture 2025"))

        # Passif circulant
        for acc in data.get("passif", {}).get("passif_circulant_hors_tresorerie", {}).get("comptes", []):
            raw_num = str(acc["account_number"])
            num = norm_map.get(raw_num, raw_num)
            net = to_dec(acc.get("montant_net_mad", 0.0))
            title = self.get_account_meta(num).account_title
            if net > Decimal("0.00"):
                self.ledger[num].opening_credit += net
                opening_lines.append(JournalLine(num, title, Decimal("0.00"), net, "Bilan d'ouverture 2025"))

        # Trésorerie passif
        for acc in data.get("passif", {}).get("tresorerie_passif", {}).get("comptes", []):
            raw_num = str(acc["account_number"])
            num = norm_map.get(raw_num, raw_num)
            net = to_dec(acc.get("montant_net_mad", 0.0))
            title = self.get_account_meta(num).account_title
            if net > Decimal("0.00"):
                self.ledger[num].opening_credit += net
                opening_lines.append(JournalLine(num, title, Decimal("0.00"), net, "Bilan d'ouverture 2025"))

        opening_entry = JournalEntry(
            entry_id="JRN-2025-00001",
            entry_date=date(2025, 1, 1),
            journal_code=JournalCode.RAN,
            piece_ref="BILAN-OUVERTURE-2025",
            event_id="EVT-CLS-001",
            description="Bilan d'ouverture au 01/01/2025 — Reprise des comptes",
            lines=opening_lines
        )
        self.journal.append(opening_entry)

    def post_event(self, event_id: str, entry_id: str, entry_date: date, piece_ref: str, context: Dict[str, Decimal], description_override: str = "") -> JournalEntry:
        """
        Dynamically resolves the journal template for event_id from config/journal_templates.yaml,
        evaluates debit/credit formulas with context, validates balance, and posts into ledger.
        """
        if event_id not in self.templates_by_event:
            raise KeyError(f"Event ID '{event_id}' not found in journal_templates.yaml")

        tpl = self.templates_by_event[event_id]
        jcode = JournalCode(tpl.get("journal_code", "OD"))
        desc = description_override or tpl.get("description", f"Écriture {event_id}")

        lines = []
        for line_def in tpl.get("lines", []):
            acc_num = str(line_def["account_number"])
            acc_title = self.get_account_meta(acc_num).account_title

            # Evaluate formulas safely using Decimal context
            dr_formula = str(line_def.get("debit_formula", "0.00"))
            cr_formula = str(line_def.get("credit_formula", "0.00"))

            dr_val = self._eval_formula(dr_formula, context)
            cr_val = self._eval_formula(cr_formula, context)

            if dr_val > Decimal("0.00") or cr_val > Decimal("0.00"):
                lines.append(JournalLine(
                    account_number=acc_num,
                    account_title=acc_title,
                    debit=dr_val,
                    credit=cr_val,
                    description=desc
                ))

        entry = JournalEntry(
            entry_id=entry_id,
            entry_date=entry_date,
            journal_code=jcode,
            piece_ref=piece_ref,
            event_id=event_id,
            description=desc,
            lines=lines
        )

        self.post_entry(entry)
        return entry

    def _eval_formula(self, formula: str, context: Dict[str, Decimal]) -> Decimal:
        """Safely evaluates a template formula against context variables."""
        formula = formula.strip()
        if formula in ("0.00", "0", "0.0", ""):
            return Decimal("0.00")

        if formula in context:
            return to_dec(context[formula])

        # Simple arithmetic formula evaluation with Decimal
        local_scope = {k: to_dec(v) for k, v in context.items()}
        # Add basic zero defaults for common template formula variables
        template_vars = [
            "amount_ht", "amount_tva", "amount_ttc", "amount_ht_mad", "lcn_nominal",
            "tpi_mad", "tpi_amount_mad", "import_tva_mad", "tva_import_mad", "cif_mad",
            "gross_permanent", "gross_seasonal", "cnss_employee_total", "ir_withheld_total",
            "cnss_employer_prestations", "cnss_employer_amo_fp", "at_insurance_cost",
            "net_salaries_payable", "total_cnss_due", "total_agio_ttc", "discount_interest_ht",
            "banking_fees_ht", "agio_tva_10", "reject_fee_ht", "reject_fee_tva", "payment_amount",
            "tva_collectee_total", "tva_deductible_charges", "tva_deductible_immob", "tva_due_net",
            "acompte_amount", "total_is_due", "sum_4_acomptes", "tp_amount", "tsc_amount",
            "dda_buildings", "dda_machinery", "dda_vehicles", "dda_furniture", "dda_it",
            "net_accounting_profit", "repair_cost_ht", "repair_cost_tva"
        ]
        for var in template_vars:
            if var not in local_scope:
                local_scope[var] = Decimal("0.00")

        try:
            val = eval(formula, {"__builtins__": {}, "round": round, "min": min, "max": max, "Decimal": Decimal}, local_scope)
            return to_dec(val)
        except Exception as e:
            raise ValueError(f"Failed to evaluate template formula '{formula}' with context {context}: {e}")

    def post_entry(self, entry: JournalEntry) -> bool:
        """Posts a balanced journal entry and updates ledger balances."""
        if not entry.is_balanced:
            diff = entry.total_debit - entry.total_credit
            raise ValueError(
                f"Cannot post imbalanced entry {entry.entry_id} ({entry.piece_ref}): "
                f"Debit={entry.total_debit}, Credit={entry.total_credit}, Imbalance={diff} MAD"
            )

        for line in entry.lines:
            acc_num = line.account_number
            if acc_num not in self.ledger:
                raise KeyError(f"Account '{acc_num}' does not exist in ledger!")
            rec = self.ledger[acc_num]
            rec.period_debit = to_dec(rec.period_debit + line.debit)
            rec.period_credit = to_dec(rec.period_credit + line.credit)
            rec.entries.append((entry.entry_date, entry.entry_id, line.description, line.debit, line.credit))

        self.journal.append(entry)
        return True

    def get_account_net_balance(self, account_prefix: str) -> Decimal:
        total = Decimal("0.00")
        for num, rec in self.ledger.items():
            if num.startswith(account_prefix):
                total += rec.net_balance
        return to_dec(total)

    def get_account_period_debit(self, account_prefix: str) -> Decimal:
        total = Decimal("0.00")
        for num, rec in self.ledger.items():
            if num.startswith(account_prefix):
                total += rec.period_debit
        return to_dec(total)

    def get_account_period_credit(self, account_prefix: str) -> Decimal:
        total = Decimal("0.00")
        for num, rec in self.ledger.items():
            if num.startswith(account_prefix):
                total += rec.period_credit
        return to_dec(total)

    def get_trial_balance(self) -> List[Dict[str, Any]]:
        """Produces the 6-column Trial Balance (Balance Générale)."""
        rows = []
        for num in sorted(self.ledger.keys()):
            rec = self.ledger[num]
            if (rec.opening_debit == Decimal("0.00") and rec.opening_credit == Decimal("0.00") and
                rec.period_debit == Decimal("0.00") and rec.period_credit == Decimal("0.00")):
                continue
            rows.append({
                "account_number": num,
                "account_title": rec.account_title,
                "opening_debit": rec.opening_debit,
                "opening_credit": rec.opening_credit,
                "period_debit": rec.period_debit,
                "period_credit": rec.period_credit,
                "total_debit": rec.total_debit,
                "total_credit": rec.total_credit,
                "final_debit": rec.final_debit_balance,
                "final_credit": rec.final_credit_balance,
            })
        return rows
