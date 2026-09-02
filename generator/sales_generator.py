# -*- coding: utf-8 -*-
"""
Order-to-Cash & Sales Generation Engine for Souss Agri-Pack SARL.
Generates commercial invoices, delivery notes, and commercial paper across all 6 client segments.
Posts all journal entries dynamically through journal_templates.yaml using Decimal.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import List, Tuple, Dict
import random

from generator.models import (
    Customer, Product, SalesInvoice, InvoiceLine,
    CommercialPaper, PaymentMethod, to_dec, to_dec_4dp
)
from generator.pcm_ledger_engine import PCMLedgerEngine
from generator.parameters_engine import ParameterEngine


class SalesGenerator:
    def __init__(self, ledger: PCMLedgerEngine, param_engine: ParameterEngine, seed: int = 42):
        self.ledger = ledger
        self.param_engine = param_engine
        self.rng = random.Random(seed)
        self.products = self._init_products()
        self.customers = self._init_customers()
        self.invoices: List[SalesInvoice] = []
        self.commercial_papers: List[CommercialPaper] = []
        self.invoice_counter = 1
        self.bl_counter = 1
        self.effet_counter = 1
        self.journal_counter = 2

    def _init_products(self) -> Dict[str, Product]:
        return {
            "P001": Product("P001", "Caisse agrumes standard 10kg", "Agrumes", 400, 300, 200, Decimal("0.640"), Decimal("5.500"), Decimal("3.520"), Decimal("1.980"), Decimal("20.00")),
            "P002": Product("P002", "Caisse tomates renforcée export", "Tomates", 500, 300, 250, Decimal("0.850"), Decimal("5.800"), Decimal("4.930"), Decimal("2.650"), Decimal("20.00")),
            "P003": Product("P003", "Plateau avocats premium imprimé", "Avocats", 400, 300, 100, Decimal("0.460"), Decimal("6.500"), Decimal("2.990"), Decimal("1.550"), Decimal("20.00")),
            "P004": Product("P004", "Barquette fraises 500g étanche", "Fruits Rouges", 300, 200, 100, Decimal("0.260"), Decimal("6.200"), Decimal("1.612"), Decimal("0.880"), Decimal("20.00")),
            "P005": Product("P005", "Emballage sur-mesure agro-industriel", "Industrie", 600, 400, 300, Decimal("1.360"), Decimal("5.400"), Decimal("7.344"), Decimal("4.250"), Decimal("20.00")),
        }

    def _init_customers(self) -> List[Customer]:
        return [
            Customer(
                "CLI-001", "Les Domaines Agricoles du Souss SA", "Domaines Souss",
                "Agri-Exportateurs", "001987654000088", "40123456", "24110", "30100110",
                "Route de Taroudant, Km 12", "Agadir", "LC 60 jours", PaymentMethod.LC60,
                Decimal("2500000.00"), 0.01, 0.22, False, "34210001"
            ),
            Customer(
                "CLI-002", "Delassus Group Souss SARL", "Delassus",
                "Agri-Exportateurs", "002123456000077", "40234567", "25220", "30100220",
                "Zone Industrielle Tassila", "Agadir", "Virement 30 jours", PaymentMethod.VIREMENT30,
                Decimal("1500000.00"), 0.005, 0.12, False, "34210002"
            ),
            Customer(
                "CLI-003", "Azura Souss Primeurs Export", "Azura",
                "Agri-Exportateurs", "001555666000033", "40345678", "26330", "30100330",
                "Boulevard Mohammed V", "Agadir", "LC 60 jours", PaymentMethod.LC60,
                Decimal("1000000.00"), 0.01, 0.08, False, "34210003"
            ),
            Customer(
                "CLI-004", "Marjane Holding SA", "Marjane",
                "Grande Distribution (GMS)", "001777888000044", "40456789", "27440", "30100440",
                "Zone Industrielle Sidi Bernoussi", "Casablanca", "LC 120 jours", PaymentMethod.LC120,
                Decimal("2000000.00"), 0.02, 0.16, False, "34210004"
            ),
            Customer(
                "CLI-005", "LabelVie / Carrefour Hyper SA", "LabelVie",
                "Grande Distribution (GMS)", "001888999000055", "40567890", "28550", "30100550",
                "Route des Chaux", "Rabat", "LC 120 jours", PaymentMethod.LC120,
                Decimal("1500000.00"), 0.02, 0.10, False, "34210005"
            ),
            Customer(
                "CLI-006", "Comptoir Grossistes Souk El Had", "Grossiste Souk El Had",
                "Grossistes & Marché Traditionnel", "002444555000066", "40678901", "29660", "30100660",
                "Marché Municipal Souk El Had", "Agadir", "Chèque / Espèces à réception", PaymentMethod.CASH,
                Decimal("300000.00"), 0.03, 0.07, False, "34210006"
            ),
            Customer(
                "CLI-007", "Société des Grossistes d'Inezgane SARL", "Grossistes Inezgane",
                "Grossistes & Marché Traditionnel", "002333444000077", "40789012", "30770", "30100770",
                "Zone de Marché de Gros", "Inezgane", "Chèque 15 jours", PaymentMethod.CHEQUE,
                Decimal("300000.00"), 0.03, 0.05, False, "34210007"
            ),
            Customer(
                "CLI-008", "Uniconserves Souss SA", "Uniconserves",
                "Agro-Industrie & Conserves", "001444333000022", "40890123", "31880", "30100880",
                "Port d'Agadir, Zone Industrielle", "Agadir", "LC 90 jours", PaymentMethod.LC90,
                Decimal("800000.00"), 0.02, 0.06, False, "34210008"
            ),
            Customer(
                "CLI-009", "Huiles et Olives du Souss SARL", "Huiles Souss",
                "Agro-Industrie & Conserves", "001333222000011", "40901234", "32990", "30100990",
                "Zone Industrielle Ouled Teima", "Taroudant", "Virement 30 jours", PaymentMethod.VIREMENT30,
                Decimal("500000.00"), 0.015, 0.04, False, "34210009"
            ),
            Customer(
                "CLI-010", "EuroAgri Logistics & Imports SL", "EuroAgri Spain",
                "Export Direct (Union Européenne)", "000000000000000", "ES-B12345678", "ES-MAD-12", "30101000",
                "Mercabarna, Calle Mayor 45", "Barcelone (Espagne)", "Virement 30 jours (EUR)", PaymentMethod.VIREMENT30,
                Decimal("1000000.00"), 0.005, 0.06, True, "34210010"
            ),
            Customer(
                "CLI-011", "Coopérative Agricole Souss-Massa Export (Copag)", "Copag Souss",
                "Coopératives Agricoles", "001666777000099", "40111222", "33110", "30101110",
                "Zone Agricole Chtouka", "Ait Baha", "LC 90 jours", PaymentMethod.LC90,
                Decimal("600000.00"), 0.15, 0.04, False, "34210011"
            )
        ]

    def generate_month_sales(self, year: int, month: int, monthly_multiplier: float, target_annual_ca: Decimal = Decimal("10930700.00")) -> List[SalesInvoice]:
        month_target_ht = to_dec((target_annual_ca / Decimal("12.00")) * to_dec(monthly_multiplier))
        generated_invoices = []

        num_invoices = self.rng.randint(18, 26)
        base_amount_per_invoice = month_target_ht / Decimal(str(num_invoices))

        days_in_month = 31 if month in (1, 3, 5, 7, 8, 10, 12) else (30 if month in (4, 6, 9, 11) else 28)
        current_month_ht = Decimal("0.00")

        for i in range(num_invoices):
            day = min(int((i + 1) * (days_in_month / (num_invoices + 1))) + self.rng.randint(0, 1), days_in_month)
            day = max(1, day)
            inv_date = date(year, month, day)

            cust = self.rng.choices(self.customers, weights=[c.annual_volume_share_pct for c in self.customers], k=1)[0]

            if cust.segment == "Agri-Exportateurs":
                skus = ["P001", "P002", "P003"]
                weights = [0.4, 0.4, 0.2]
            elif cust.segment == "Grande Distribution (GMS)":
                skus = ["P001", "P002", "P004"]
                weights = [0.3, 0.5, 0.2]
            elif cust.segment == "Grossistes & Marché Traditionnel":
                skus = ["P001", "P002"]
                weights = [0.7, 0.3]
            elif cust.segment == "Export Direct (Union Européenne)":
                skus = ["P002", "P003", "P004"]
                weights = [0.4, 0.4, 0.2]
            elif cust.segment == "Agro-Industrie & Conserves":
                skus = ["P005", "P002"]
                weights = [0.8, 0.2]
            else:
                skus = ["P001", "P002"]
                weights = [0.5, 0.5]

            selected_sku = self.rng.choices(skus, weights=weights, k=1)[0]
            prod = self.products[selected_sku]

            target_inv_ht = base_amount_per_invoice * Decimal(str(round(self.rng.uniform(0.75, 1.25), 4)))
            if i == num_invoices - 1:
                target_inv_ht = max(Decimal("5000.00"), month_target_ht - current_month_ht)

            qty = max(500, int(round(float(target_inv_ht / prod.unit_selling_price_mad), -2)))
            total_ht = to_dec(Decimal(str(qty)) * prod.unit_selling_price_mad)
            current_month_ht += total_ht

            raw_tva = Decimal("0.00") if cust.is_export else self.param_engine.get_decimal("tva_standard", inv_date)
            tva_factor = raw_tva if raw_tva <= Decimal("1.00") else (raw_tva / Decimal("100.00"))
            tva_rate_pct = to_dec(tva_factor * Decimal("100.00"))
            total_tva = to_dec(total_ht * tva_factor)
            total_ttc = to_dec(total_ht + total_tva)

            inv_number = f"FAC-{year}-{self.invoice_counter:05d}"
            bl_number = f"BL-{year}-{self.bl_counter:05d}"
            self.invoice_counter += 1
            self.bl_counter += 1

            if cust.payment_method == PaymentMethod.LC120:
                due_date = inv_date + timedelta(days=120)
            elif cust.payment_method == PaymentMethod.LC90:
                due_date = inv_date + timedelta(days=90)
            elif cust.payment_method == PaymentMethod.LC60:
                due_date = inv_date + timedelta(days=60)
            elif cust.payment_method == PaymentMethod.VIREMENT30:
                due_date = inv_date + timedelta(days=30)
            elif cust.payment_method == PaymentMethod.CHEQUE:
                due_date = inv_date + timedelta(days=15)
            else:  # CASH
                due_date = inv_date

            inv_line = InvoiceLine(
                sku=prod.sku,
                description=prod.name,
                quantity=qty,
                unit_price_ht=prod.unit_selling_price_mad,
                surface_m2_total=to_dec(Decimal(str(qty)) * prod.surface_m2),
                total_ht=total_ht,
                tva_rate_pct=tva_rate_pct,
                total_tva=total_tva,
                total_ttc=total_ttc
            )

            invoice = SalesInvoice(
                invoice_number=inv_number,
                invoice_date=inv_date,
                due_date=due_date,
                customer_id=cust.customer_id,
                customer_name=cust.company_name,
                customer_ice=cust.ice,
                delivery_note_ref=bl_number,
                lines=[inv_line],
                total_ht=total_ht,
                total_tva=total_tva,
                total_ttc=total_ttc,
                tva_rate_pct=tva_rate_pct,
                payment_method=cust.payment_method,
                is_export=cust.is_export,
                status="ISSUED"
            )
            generated_invoices.append(invoice)
            self.invoices.append(invoice)

            # Post Journal Entry via journal_templates.yaml
            entry_id = f"JRN-{year}-{self.journal_counter:05d}"
            self.journal_counter += 1

            if cust.is_export:
                context = {
                    "amount_ht_mad": total_ht,
                    "amount_ttc": total_ttc
                }
                self.ledger.post_event("EVT-SAL-004", entry_id, inv_date, inv_number, context, f"Vente Export {inv_number} - {cust.trade_name}")
            else:
                context = {
                    "amount_ttc": total_ttc,
                    "amount_ht": total_ht,
                    "amount_tva": total_tva
                }
                self.ledger.post_event("EVT-SAL-003", entry_id, inv_date, inv_number, context, f"Facturation Vente {inv_number} - {cust.trade_name}")

            # Draw LCN / Commercial Paper for the invoice and post EVT-BNK-001
            effet_id = f"LCR-{year}-{self.effet_counter:05d}"
            self.effet_counter += 1
            paper = CommercialPaper(
                effet_id=effet_id,
                invoice_number=inv_number,
                customer_id=cust.customer_id,
                customer_name=cust.company_name,
                draw_date=inv_date + timedelta(days=2),
                due_date=due_date,
                nominal_amount_mad=total_ttc,
                status="PORTFOLIO"
            )
            self.commercial_papers.append(paper)

            j_entry_id = f"JRN-{year}-{self.journal_counter:05d}"
            self.journal_counter += 1
            cp_context = {
                "lcn_nominal": total_ttc
            }
            self.ledger.post_event("EVT-BNK-001", j_entry_id, paper.draw_date, effet_id, cp_context, f"Création Traite {effet_id} Facture {inv_number}")

        return generated_invoices
