# -*- coding: utf-8 -*-
"""
Procure-to-Pay & Purchase Generation Engine for Souss Agri-Pack SARL.
Generates raw material purchases, EU imports, industrial utilities, and operating expenses.
Posts all journal entries dynamically through journal_templates.yaml using Decimal.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict
import random

from generator.models import (
    Supplier, PurchaseInvoice, PaymentMethod, to_dec, to_dec_4dp
)
from generator.pcm_ledger_engine import PCMLedgerEngine
from generator.parameters_engine import ParameterEngine


class PurchaseGenerator:
    def __init__(self, ledger: PCMLedgerEngine, param_engine: ParameterEngine, seed: int = 43):
        self.ledger = ledger
        self.param_engine = param_engine
        self.rng = random.Random(seed)
        self.suppliers = self._init_suppliers()
        self.invoices: List[PurchaseInvoice] = []
        self.invoice_counter = 1
        self.dum_counter = 1
        self.journal_counter = 500

    def _init_suppliers(self) -> Dict[str, Supplier]:
        return {
            "SUP-001": Supplier("SUP-001", "CMCP International Paper Kenitra", "Papeterie Domestique", "MA", "001555444000011", "30111222", "Maroc", "MAD", "LC 60 jours", PaymentMethod.LC60, False, "44110001"),
            "SUP-002": Supplier("SUP-002", "International Paper Madrid SA", "Papeterie Import EU", "EU", None, "ES-A28001122", "Espagne", "EUR", "LC 90 jours", PaymentMethod.LC90, True, "44110002"),
            "SUP-003": Supplier("SUP-003", "Colorpak Chimie & Encres SARL", "Encres & Colles", "MA", "002222333000044", "30222333", "Maroc", "MAD", "Virement 30 jours", PaymentMethod.VIREMENT30, False, "44110003"),
            "SUP-004": Supplier("SUP-004", "Amidonnerie du Maroc SA", "Amidon & Liants", "MA", "001888777000055", "30333444", "Maroc", "MAD", "Virement 30 jours", PaymentMethod.VIREMENT30, False, "44110004"),
            "SUP-005": Supplier("SUP-005", "ONEE - Branche Électricité Moyenne Tension", "Énergie & Utilités", "MA", "001000111000099", "30444555", "Maroc", "MAD", "Prélèvement fin de mois", PaymentMethod.VIREMENT_DIRECT, False, "44110005"),
            "SUP-006": Supplier("SUP-006", "ONEE - Branche Eau Industrielle", "Eau & Utilités", "MA", "001000222000088", "30555666", "Maroc", "MAD", "Prélèvement fin de mois", PaymentMethod.VIREMENT_DIRECT, False, "44110006"),
            "SUP-007": Supplier("SUP-007", "Afriquia Carburants & Lubrifiants SA", "Carburants & Transport", "MA", "001666555000077", "30666777", "Maroc", "MAD", "Virement 30 jours", PaymentMethod.VIREMENT30, False, "44110007"),
            "SUP-008": Supplier("SUP-008", "RMA Royale Marocaine d'Assurance", "Assurance & Risques", "MA", "001444111000033", "30777888", "Maroc", "MAD", "Virement comptant", PaymentMethod.VIREMENT_DIRECT, False, "44110008"),
            "SUP-009": Supplier("SUP-009", "Transit Express Souss Transitaire", "Douane & Transit", "MA", "002111888000022", "30888999", "Maroc", "MAD", "Virement 15 jours", PaymentMethod.VIREMENT30, False, "44110009"),
            "SUP-010": Supplier("SUP-010", "Cabinet Expertise & Audit Souss (CAC)", "Conseil & Honoraires", "MA", "002333777000066", "30999000", "Maroc", "MAD", "Virement 30 jours", PaymentMethod.VIREMENT30, False, "44110010"),
        }

    def generate_month_purchases(self, year: int, month: int, monthly_multiplier: float) -> List[PurchaseInvoice]:
        month_invoices = []
        month_paper_target = to_dec((Decimal("5900000.00") / Decimal("12.00")) * to_dec(monthly_multiplier))
        cmcp_target = to_dec(month_paper_target * Decimal("0.65"))

        # 1. Domestic Paper Purchases (CMCP Kenitra) ~ 65% of paper -> EVT-PUR-003
        num_cmcp = self.rng.randint(2, 3)
        for i in range(num_cmcp):
            day = max(2, min(28, (i + 1) * 9 + self.rng.randint(-2, 2)))
            inv_date = date(year, month, day)
            ht = to_dec((cmcp_target / Decimal(str(num_cmcp))) * Decimal(str(round(self.rng.uniform(0.95, 1.05), 4))))
            raw_tva = self.param_engine.get_decimal("tva_standard", inv_date)
            tva_factor = raw_tva if raw_tva <= Decimal("1.00") else (raw_tva / Decimal("100.00"))
            tva = to_dec(ht * tva_factor)
            ttc = to_dec(ht + tva)
            num = f"FAC-FOUR-{year}-{self.invoice_counter:05d}"
            self.invoice_counter += 1

            inv = PurchaseInvoice(
                invoice_number=num,
                invoice_date=inv_date,
                due_date=inv_date + timedelta(days=60),
                supplier_id="SUP-001",
                supplier_name="CMCP International Paper Kenitra",
                category="Matières Premières (Papier Kraft/Cannelure)",
                currency="MAD",
                amount_currency=ht,
                exchange_rate=Decimal("1.00"),
                amount_ht_mad=ht,
                tva_rate_pct=to_dec(tva_factor * Decimal("100.00")),
                tva_amount_mad=tva,
                amount_ttc_mad=ttc,
                payment_method=PaymentMethod.LC60
            )
            month_invoices.append(inv)
            self.invoices.append(inv)

            # Post via EVT-PUR-003
            entry_id = f"JRN-{year}-{self.journal_counter:05d}"
            self.journal_counter += 1
            context = {
                "amount_ht": ht,
                "amount_tva": tva,
                "amount_ttc": ttc
            }
            self.ledger.post_event("EVT-PUR-003", entry_id, inv_date, num, context, f"Achat Papier Bobines CMCP Facture {num}")

        # 2. Imported EU Paper Purchases (International Paper Madrid) ~ 35% of paper -> EVT-PUR-004
        if month in (1, 2, 3, 4, 5, 7, 9, 10, 11, 12):
            ip_target_mad = to_dec(month_paper_target * Decimal("0.35"))
            eur_rate = to_dec_4dp(Decimal("10.7400") + to_dec_4dp(self.rng.uniform(-0.08, 0.08)))
            ip_eur = to_dec(ip_target_mad / eur_rate)
            ht_mad = to_dec(ip_eur * eur_rate)
            raw_tpi = self.param_engine.get_decimal("customs_tpi_rate", date(year, month, 15))
            tpi_factor = raw_tpi if raw_tpi <= Decimal("1.00") else (raw_tpi / Decimal("100.00"))
            tpi_mad = to_dec(ht_mad * tpi_factor)
            tva_import = to_dec((ht_mad + tpi_mad) * Decimal("0.20"))
            ttc_mad = to_dec(ht_mad + tpi_mad + tva_import)

            dum_num = f"DUM-{year}-AG-{self.dum_counter:05d}"
            inv_num = f"FAC-FOUR-{year}-{self.invoice_counter:05d}"
            self.dum_counter += 1
            self.invoice_counter += 1
            inv_date = date(year, month, 15)

            inv_eu = PurchaseInvoice(
                invoice_number=inv_num,
                invoice_date=inv_date,
                due_date=inv_date + timedelta(days=90),
                supplier_id="SUP-002",
                supplier_name="International Paper Madrid SA",
                category="Matières Premières Import EU (Testliner/Kraftliner)",
                currency="EUR",
                amount_currency=ip_eur,
                exchange_rate=eur_rate,
                amount_ht_mad=ht_mad,
                tva_rate_pct=Decimal("20.00"),
                tva_amount_mad=tva_import,
                amount_ttc_mad=ttc_mad,
                customs_dum_ref=dum_num,
                droit_import_mad=Decimal("0.00"),
                tpi_mad=tpi_mad,
                payment_method=PaymentMethod.LC90
            )
            month_invoices.append(inv_eu)
            self.invoices.append(inv_eu)

            # Post EVT-PUR-004 (EU Paper Import Purchase)
            entry_id = f"JRN-{year}-{self.journal_counter:05d}"
            self.journal_counter += 1
            eu_context = {
                "cif_mad": ht_mad,
                "tpi_mad": tpi_mad,
                "import_tva_mad": tva_import
            }
            self.ledger.post_event("EVT-PUR-004", entry_id, inv_date, inv_num, eu_context, f"Import Papier Madrid Facture {inv_num}")

        # 3. Chemical Auxiliaries (Inks + Glue) ~ 25,000 MAD/month -> EVT-PUR-007
        ink_ht = to_dec(Decimal("25000.00") * Decimal(str(round(self.rng.uniform(0.9, 1.1), 4))))
        ink_tva = to_dec(ink_ht * Decimal("0.20"))
        ink_ttc = to_dec(ink_ht + ink_tva)
        ink_num = f"FAC-FOUR-{year}-{self.invoice_counter:05d}"
        self.invoice_counter += 1
        inv_date = date(year, month, 12)

        inv_ink = PurchaseInvoice(
            invoice_number=ink_num,
            invoice_date=inv_date,
            due_date=inv_date + timedelta(days=30),
            supplier_id="SUP-003",
            supplier_name="Colorpak Chimie & Encres SARL",
            category="Matières Consommables (Encres & Colles)",
            currency="MAD",
            amount_currency=ink_ht,
            exchange_rate=Decimal("1.00"),
            amount_ht_mad=ink_ht,
            tva_rate_pct=Decimal("20.00"),
            tva_amount_mad=ink_tva,
            amount_ttc_mad=ink_ttc,
            payment_method=PaymentMethod.VIREMENT30
        )
        month_invoices.append(inv_ink)
        self.invoices.append(inv_ink)

        entry_id_ink = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        self.ledger.post_event("EVT-PUR-007", entry_id_ink, inv_date, ink_num, {"amount_ht": ink_ht, "amount_tva": ink_tva, "amount_ttc": ink_ttc}, f"Achats Encres/Colles Facture {ink_num}")

        # 4. Utilities: ONEE Electricity (18% in 2025) -> EVT-PUR-006
        elec_ht = to_dec(Decimal("32000.00") * Decimal(str(round(self.rng.uniform(0.92, 1.08), 4))))
        raw_elec_tva = self.param_engine.get_decimal("tva_electricity_mv", date(year, month, 25))
        elec_tva_factor = raw_elec_tva if raw_elec_tva <= Decimal("1.00") else (raw_elec_tva / Decimal("100.00"))
        elec_tva = to_dec(elec_ht * elec_tva_factor)
        elec_ttc = to_dec(elec_ht + elec_tva)
        elec_num = f"FAC-ONEE-ELEC-{year}-{month:02d}"

        entry_id_elec = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        self.ledger.post_event("EVT-PUR-006", entry_id_elec, date(year, month, 25), elec_num, {"amount_ht": elec_ht, "amount_tva": elec_tva, "amount_ttc": elec_ttc}, f"ONEE Électricité {month:02d}/{year}")

        # 5. Utilities: ONEE Water (9% in 2025) & Transport/Transit -> EVT-PUR-005
        eau_ht = to_dec(Decimal("3500.00") * Decimal(str(round(self.rng.uniform(0.95, 1.05), 4))))
        raw_eau_tva = self.param_engine.get_decimal("tva_water_industrial", date(year, month, 25))
        eau_tva_factor = raw_eau_tva if raw_eau_tva <= Decimal("1.00") else (raw_eau_tva / Decimal("100.00"))
        eau_tva = to_dec(eau_ht * eau_tva_factor)
        eau_ttc = to_dec(eau_ht + eau_tva)
        eau_num = f"FAC-ONEE-EAU-{year}-{month:02d}"

        entry_id_eau = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        self.ledger.post_event("EVT-PUR-005", entry_id_eau, date(year, month, 25), eau_num, {"amount_ht": eau_ht, "amount_tva": eau_tva, "amount_ttc": eau_ttc}, f"ONEE Eau & Services {month:02d}/{year}")

        # 6. Fuel & Diesel (20% TVA) -> EVT-PUR-005
        fuel_ht = to_dec(Decimal("14000.00") * Decimal(str(round(self.rng.uniform(0.9, 1.1), 4))))
        fuel_tva = to_dec(fuel_ht * Decimal("0.20"))
        fuel_ttc = to_dec(fuel_ht + fuel_tva)
        fuel_num = f"FAC-AFRIQUIA-{year}-{month:02d}"

        entry_id_fuel = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        self.ledger.post_event("EVT-PUR-005", entry_id_fuel, date(year, month, 28), fuel_num, {"amount_ht": fuel_ht, "amount_tva": fuel_tva, "amount_ttc": fuel_ttc}, f"Gazole Transport Afriquia {month:02d}/{year}")

        # 7. External Maintenance & Repair -> EVT-RSK-001
        serv_ht = to_dec(Decimal("18000.00") * Decimal(str(round(self.rng.uniform(0.85, 1.15), 4))))
        serv_tva = to_dec(serv_ht * Decimal("0.20"))
        serv_ttc = to_dec(serv_ht + serv_tva)
        serv_num = f"FAC-MAINT-{year}-{month:02d}"

        entry_id_serv = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        self.ledger.post_event("EVT-RSK-001", entry_id_serv, date(year, month, 20), serv_num, {"repair_cost_ht": serv_ht, "repair_cost_tva": serv_tva}, f"Maintenance Ligne Ondulation {month:02d}/{year}")

        return month_invoices
