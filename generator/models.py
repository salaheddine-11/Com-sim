# -*- coding: utf-8 -*-
"""
Data models and typed structures for Souss Agri-Pack SARL simulation.
Using Decimal throughout for zero-drift financial and accounting integrity.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict, Any
from enum import Enum


def to_dec(val: Any) -> Decimal:
    """Safely converts float/int/str/Decimal to quantized Decimal at 2 decimal places."""
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def to_dec_4dp(val: Any) -> Decimal:
    """Converts to quantized Decimal at 4 decimal places (for unit prices/rates)."""
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    return Decimal(str(val)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


class JournalCode(str, Enum):
    RAN = "RAN"      # Report à nouveau (Opening entries)
    ACH = "ACH"      # Achats
    VEN = "VEN"      # Ventes
    BQ_AWB = "BQ-AWB"  # Banque Attijariwafa Bank
    BQ_BP = "BQ-BP"    # Banque Populaire
    BQ_CAM = "BQ-CAM"  # Banque Crédit Agricole du Maroc
    BQ_BMCE = "BQ-BMCE" # Banque BMCE
    CAI = "CAI"      # Caisse centrale
    PAI = "PAI"      # Paie et charges sociales
    OD = "OD"        # Opérations diverses (inventaire, amortissements, régularisations)


class PaymentMethod(str, Enum):
    LC60 = "LC_60D"      # Lettre de change / Traite à 60 jours
    LC90 = "LC_90D"      # Lettre de change / Traite à 90 jours
    LC120 = "LC_120D"    # Lettre de change / Traite à 120 jours (GMS)
    VIREMENT30 = "VIR_30D" # Virement bancaire 30 jours
    VIREMENT_DIRECT = "VIR_DIRECT"
    CASH = "CASH"        # Espèces (Souk / Caisse)
    CHEQUE = "CHEQUE"    # Chèque bancaire


@dataclass
class Customer:
    customer_id: str
    company_name: str
    trade_name: str
    segment: str
    ice: str
    identifiant_fiscal: str
    registre_commerce: str
    taxe_professionnelle: str
    address: str
    city: str
    payment_terms: str
    payment_method: PaymentMethod
    credit_limit_mad: Decimal
    impaye_probability: float
    annual_volume_share_pct: float
    is_export: bool = False
    auxiliary_account: str = "34210000"


@dataclass
class Supplier:
    supplier_id: str
    company_name: str
    category: str
    origin: str  # "MA", "EU", "NON_EU"
    ice: Optional[str]
    tax_id: str
    country: str
    currency: str  # "MAD", "EUR", "USD"
    payment_terms: str
    payment_method: PaymentMethod
    is_eu_origin: bool = False
    auxiliary_account: str = "44110000"


@dataclass
class Product:
    sku: str
    name: str
    category: str
    box_length_mm: float
    box_width_mm: float
    box_height_mm: float
    surface_m2: Decimal
    target_selling_price_mad_m2: Decimal
    unit_selling_price_mad: Decimal
    unit_material_cost_mad: Decimal
    tva_rate_pct: Decimal = Decimal("20.00")


@dataclass
class Employee:
    employee_id: str
    first_name: str
    last_name: str
    cin: str
    cnss_number: str
    department: str
    position: str
    hire_date: str
    monthly_gross_mad: Decimal
    dependents_count: int
    is_seasonal: bool
    seasonal_months: List[int] = field(default_factory=list)


@dataclass
class InvoiceLine:
    sku: str
    description: str
    quantity: int
    unit_price_ht: Decimal
    surface_m2_total: Decimal
    total_ht: Decimal
    tva_rate_pct: Decimal
    total_tva: Decimal
    total_ttc: Decimal


@dataclass
class SalesInvoice:
    invoice_number: str
    invoice_date: date
    due_date: date
    customer_id: str
    customer_name: str
    customer_ice: str
    delivery_note_ref: str
    lines: List[InvoiceLine]
    total_ht: Decimal
    total_tva: Decimal
    total_ttc: Decimal
    tva_rate_pct: Decimal
    payment_method: PaymentMethod
    is_export: bool
    status: str = "ISSUED"  # ISSUED, COMMERCIAL_PAPER_DRAWN, DISCOUNTED, PAID, OVERDUE, DEFAULTED


@dataclass
class CommercialPaper:
    effet_id: str
    invoice_number: str
    customer_id: str
    customer_name: str
    draw_date: date
    due_date: date
    nominal_amount_mad: Decimal
    status: str = "PORTFOLIO"  # PORTFOLIO, DISCOUNTED, COLLECTED_AT_MATURITY, IMPAYE, RECOVERED
    bank_discounted: Optional[str] = None
    discount_date: Optional[date] = None
    agio_interet_mad: Decimal = Decimal("0.00")
    agio_endos_mad: Decimal = Decimal("0.00")
    agio_service_mad: Decimal = Decimal("0.00")
    agio_tva_10_mad: Decimal = Decimal("0.00")
    total_agio_mad: Decimal = Decimal("0.00")
    net_cash_received_mad: Decimal = Decimal("0.00")


@dataclass
class PurchaseInvoice:
    invoice_number: str
    invoice_date: date
    due_date: date
    supplier_id: str
    supplier_name: str
    category: str
    currency: str
    amount_currency: Decimal
    exchange_rate: Decimal
    amount_ht_mad: Decimal
    tva_rate_pct: Decimal
    tva_amount_mad: Decimal
    amount_ttc_mad: Decimal
    customs_dum_ref: Optional[str] = None
    droit_import_mad: Decimal = Decimal("0.00")
    tpi_mad: Decimal = Decimal("0.00")
    payment_method: PaymentMethod = PaymentMethod.VIREMENT30
    status: str = "PENDING"  # PENDING, PAID


@dataclass
class PayrollSlip:
    slip_id: str
    month_period: str  # YYYY-MM
    employee_id: str
    employee_name: str
    position: str
    cin: str
    cnss_number: str
    gross_salary_mad: Decimal
    cnss_prestations_employee_mad: Decimal  # capped at 6000
    amo_employee_mad: Decimal               # uncapped 2.26%
    salaire_brut_imposable_mad: Decimal
    frais_professionnels_mad: Decimal       # 20% capped at 2500/m
    salaire_net_imposable_mad: Decimal
    ir_brut_mad: Decimal
    family_deductions_mad: Decimal          # 500 MAD/yr / 12 per dep
    ir_net_withheld_mad: Decimal
    net_payable_mad: Decimal
    # Employer charges
    cnss_prestations_employer_mad: Decimal  # capped 8.98%
    allocations_familiales_mad: Decimal     # uncapped 6.40%
    formation_pro_mad: Decimal              # uncapped 1.60%
    amo_employer_mad: Decimal               # uncapped 2.26%
    amo_solidarite_mad: Decimal             # uncapped 1.85%
    total_cnss_employer_mad: Decimal        # sum of above = 21.09%
    at_insurance_employer_mad: Decimal      # 3.80%
    total_employer_cost_mad: Decimal


@dataclass
class JournalLine:
    account_number: str
    account_title: str
    debit: Decimal
    credit: Decimal
    description: str


@dataclass
class JournalEntry:
    entry_id: str
    entry_date: date
    journal_code: JournalCode
    piece_ref: str
    event_id: str
    description: str
    lines: List[JournalLine] = field(default_factory=list)

    @property
    def total_debit(self) -> Decimal:
        return to_dec(sum(l.debit for l in self.lines))

    @property
    def total_credit(self) -> Decimal:
        return to_dec(sum(l.credit for l in self.lines))

    @property
    def is_balanced(self) -> bool:
        return self.total_debit == self.total_credit
