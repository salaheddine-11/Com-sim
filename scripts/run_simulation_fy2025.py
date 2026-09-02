# -*- coding: utf-8 -*-
"""
Master Simulation Runner for Souss Agri-Pack SARL — FY 2025.
Executes the full 365-day operational, fiscal, payroll, banking, and accounting simulation.
Outputs operational CSVs, double-entry general ledgers, financial statements, and an SQLite database.
All journal postings resolved dynamically through config/journal_templates.yaml with Decimal.
"""

import os
import sys
import csv
import json
import sqlite3
import yaml
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Any, List

# Add parent directory to path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from generator.models import PaymentMethod, to_dec
from generator.simulation_clock import SimulationClock
from generator.parameters_engine import ParameterEngine
from generator.pcm_ledger_engine import PCMLedgerEngine
from generator.sales_generator import SalesGenerator
from generator.purchase_generator import PurchaseGenerator
from generator.payroll_generator import PayrollGenerator
from generator.treasury_generator import TreasuryGenerator
from generator.tax_compliance_generator import TaxComplianceGenerator
from generator.closing_generator import ClosingGenerator
from generator.financial_reports import FinancialReportsGenerator


def main():
    print("=" * 80)
    print("SOUSS AGRI-PACK SARL — FY 2025 SYNTHETIC DATA & SIMULATION ENGINE")
    print("=" * 80)

    # 1. Output Directories Setup
    out_dir = os.path.join(base_dir, "data", "fy2025")
    db_dir = os.path.join(out_dir, "database")
    op_dir = os.path.join(out_dir, "operational")
    acc_dir = os.path.join(out_dir, "accounting")
    rep_dir = os.path.join(out_dir, "reports")

    for d in [db_dir, op_dir, acc_dir, rep_dir]:
        os.makedirs(d, exist_ok=True)

    # 2. Config Paths
    coa_path = os.path.join(base_dir, "config", "chart_of_accounts.yaml")
    obs_path = os.path.join(base_dir, "config", "opening_balance_sheet.yaml")
    tpl_path = os.path.join(base_dir, "config", "journal_templates.yaml")
    param_path = os.path.join(base_dir, "config", "parameters.yaml")
    payroll_grid_path = os.path.join(base_dir, "config", "payroll_grid.yaml")
    risk_path = os.path.join(base_dir, "config", "risk_events_probabilities.yaml")

    # Load master seed from risk probabilities
    with open(risk_path, "r", encoding="utf-8") as f:
        risk_data = yaml.safe_load(f)
    master_seed = risk_data.get("risk_events", [{}])[0].get("prng_seed", 42001)

    print("[1/6] Initializing Parameter Engine and Loading Parameters (parameters.yaml)...")
    param_engine = ParameterEngine(param_path)

    print("[2/6] Initializing PCM Ledger Engine & Journal Templates (journal_templates.yaml)...")
    ledger = PCMLedgerEngine(coa_path, tpl_path)
    ledger.load_opening_balance_sheet(obs_path)

    # 3. Instantiate Domain Generators
    clock = SimulationClock(2025)
    sales_gen = SalesGenerator(ledger, param_engine, seed=master_seed)
    purch_gen = PurchaseGenerator(ledger, param_engine, seed=master_seed + 1)
    pay_gen = PayrollGenerator(ledger, param_engine, payroll_grid_path)
    treasury_gen = TreasuryGenerator(ledger, param_engine, seed=master_seed + 2)
    tax_gen = TaxComplianceGenerator(ledger, param_engine)
    closing_gen = ClosingGenerator(ledger, param_engine)

    # Monthly Seasonality Multipliers (Sum = 12.00)
    seasonality_multipliers = {
        1: 1.35, 2: 1.45, 3: 1.25, 4: 0.90, 5: 0.70, 6: 0.50,
        7: 0.40, 8: 0.50, 9: 0.95, 10: 1.15, 11: 1.35, 12: 1.45
    }

    print("[3/6] Executing Daily Simulation Clock across FY 2025 (12 Months)...")
    all_sales_invoices = []
    all_purch_invoices = []

    for month in range(1, 13):
        mult = seasonality_multipliers[month]
        print(f"  -> Processing Month {month:02d}/2025 (Seasonality Multiplier: {mult:.2f}x)...")

        # 1. Sales Generation
        month_sales = sales_gen.generate_month_sales(2025, month, mult)
        all_sales_invoices.extend(month_sales)

        # 2. Purchases Generation
        month_purch = purch_gen.generate_month_purchases(2025, month, mult)
        all_purch_invoices.extend(month_purch)

        # 3. Monthly Payroll Computation & Posting (EVT-PAY-001/002/003)
        month_slips = pay_gen.generate_month_payroll(2025, month)

        # 4. Treasury & Banking Flows
        # Commercial paper discounting on Day 15
        cur_papers = [p for p in sales_gen.commercial_papers if p.status == "PORTFOLIO"]
        if cur_papers:
            treasury_gen.process_escompte_discounting(cur_papers, date(2025, month, 15))

        # Daily maturities and settlements
        days_in_month = 31 if month in (1, 3, 5, 7, 8, 10, 12) else (30 if month in (4, 6, 9, 11) else 28)
        for d in range(1, days_in_month + 1):
            cur_date = date(2025, month, d)
            treasury_gen.process_commercial_paper_maturities(cur_date, sales_gen.commercial_papers)
            treasury_gen.process_supplier_payments(cur_date, purch_gen.invoices)

        # Month-end salary disbursement (EVT-PAY-004)
        end_of_month = clock.get_month_end_date(2025, month)
        treasury_gen.process_monthly_payroll_disbursement(end_of_month, 2025, month)

        # 5. Tax & Social Tele-payments
        # Day 10: CNSS Damancom (settling prior month, or opening for Jan)
        tax_gen.process_monthly_cnss_payment(date(2025, month, 10), 2025, month)
        # End of Month: SIMPL-IR and SIMPL-TVA liquidation
        tax_gen.process_monthly_ir_payment(end_of_month, 2025, month)
        tax_gen.process_monthly_tva_liquidation(end_of_month, 2025, month)

        # Quarterly IS Acomptes & Local Taxes
        if month == 3:
            tax_gen.process_quarterly_is_acompte(date(2025, 3, 31), 1, 2025)
            tax_gen.process_prior_year_is_solde(date(2025, 3, 31), 2025)
        elif month == 6:
            tax_gen.process_quarterly_is_acompte(date(2025, 6, 30), 2, 2025)
            tax_gen.process_annual_local_taxes(date(2025, 6, 30), 2025)
        elif month == 9:
            tax_gen.process_quarterly_is_acompte(date(2025, 9, 30), 3, 2025)
        elif month == 12:
            tax_gen.process_quarterly_is_acompte(date(2025, 12, 31), 4, 2025)

    # 4. Year-End Closing on Dec 31, 2025
    print("[4/6] Executing Year-End Closing Operations (DDA, IS Liquidation, Result Transfer)...")
    closing_summary = closing_gen.execute_year_end_closing(date(2025, 12, 31))

    # 5. Financial Reports Compilation
    print("[5/6] Compiling Moroccan Financial Statements (Bilan, CPC, Liasse Fiscale)...")
    fin_gen = FinancialReportsGenerator(ledger, closing_summary)
    bilan_md = fin_gen.generate_bilan_markdown()
    cpc_md = fin_gen.generate_cpc_markdown()
    passage_md = fin_gen.generate_tableau_passage_markdown()

    with open(os.path.join(rep_dir, "bilan_2025.md"), "w", encoding="utf-8") as f:
        f.write(bilan_md)
    with open(os.path.join(rep_dir, "cpc_2025.md"), "w", encoding="utf-8") as f:
        f.write(cpc_md)
    with open(os.path.join(rep_dir, "liasse_fiscale_2025.md"), "w", encoding="utf-8") as f:
        f.write(passage_md)

    # Convert Decimals in summary for JSON
    summary_json = {k: str(v) if isinstance(v, Decimal) else v for k, v in closing_summary.items()}
    with open(os.path.join(rep_dir, "financial_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=2)

    # 6. Exporting CSVs and SQLite Database
    print("[6/6] Exporting CSV Datasets and SQLite Database...")

    with open(os.path.join(op_dir, "sales_invoices.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["invoice_number", "invoice_date", "due_date", "customer_id", "customer_name", "customer_ice", "total_ht_mad", "total_tva_mad", "total_ttc_mad", "payment_method", "is_export", "status"])
        for inv in sales_gen.invoices:
            writer.writerow([inv.invoice_number, inv.invoice_date.isoformat(), inv.due_date.isoformat(), inv.customer_id, inv.customer_name, inv.customer_ice, str(inv.total_ht), str(inv.total_tva), str(inv.total_ttc), inv.payment_method.value, inv.is_export, inv.status])

    with open(os.path.join(op_dir, "purchase_invoices.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["invoice_number", "invoice_date", "due_date", "supplier_id", "supplier_name", "category", "currency", "amount_ht_mad", "tva_amount_mad", "amount_ttc_mad", "customs_dum_ref", "status"])
        for pinv in purch_gen.invoices:
            writer.writerow([pinv.invoice_number, pinv.invoice_date.isoformat(), pinv.due_date.isoformat(), pinv.supplier_id, pinv.supplier_name, pinv.category, pinv.currency, str(pinv.amount_ht_mad), str(pinv.tva_amount_mad), str(pinv.amount_ttc_mad), pinv.customs_dum_ref or "", pinv.status])

    with open(os.path.join(op_dir, "payroll_slips.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["slip_id", "month_period", "employee_id", "employee_name", "position", "gross_salary_mad", "cnss_employee_mad", "amo_employee_mad", "ir_net_withheld_mad", "net_payable_mad", "cnss_employer_mad", "at_insurance_mad", "total_employer_cost_mad"])
        for ps in pay_gen.payroll_slips:
            writer.writerow([ps.slip_id, ps.month_period, ps.employee_id, ps.employee_name, ps.position, str(ps.gross_salary_mad), str(ps.cnss_prestations_employee_mad), str(ps.amo_employee_mad), str(ps.ir_net_withheld_mad), str(ps.net_payable_mad), str(ps.total_cnss_employer_mad), str(ps.at_insurance_employer_mad), str(ps.total_employer_cost_mad)])

    with open(os.path.join(op_dir, "commercial_papers.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["effet_id", "invoice_number", "customer_id", "customer_name", "draw_date", "due_date", "nominal_amount_mad", "status", "bank_discounted", "agio_interet_mad", "agio_endos_mad", "total_agio_mad", "net_cash_received_mad"])
        for cp in sales_gen.commercial_papers:
            writer.writerow([cp.effet_id, cp.invoice_number, cp.customer_id, cp.customer_name, cp.draw_date.isoformat(), cp.due_date.isoformat(), str(cp.nominal_amount_mad), cp.status, cp.bank_discounted or "", str(cp.agio_interet_mad), str(cp.agio_endos_mad), str(cp.total_agio_mad), str(cp.net_cash_received_mad)])

    with open(os.path.join(acc_dir, "journal_general.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["entry_id", "entry_date", "journal_code", "piece_ref", "event_id", "account_number", "account_title", "debit_mad", "credit_mad", "description"])
        for entry in ledger.journal:
            for line in entry.lines:
                writer.writerow([entry.entry_id, entry.entry_date.isoformat(), entry.journal_code.value, entry.piece_ref, entry.event_id, line.account_number, line.account_title, str(line.debit), str(line.credit), line.description])

    tb_rows = ledger.get_trial_balance()
    with open(os.path.join(acc_dir, "balance_generale.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["account_number", "account_title", "opening_debit_mad", "opening_credit_mad", "period_debit_mad", "period_credit_mad", "total_debit_mad", "total_credit_mad", "final_debit_balance_mad", "final_credit_balance_mad"])
        for row in tb_rows:
            writer.writerow([row["account_number"], row["account_title"], str(row["opening_debit"]), str(row["opening_credit"]), str(row["period_debit"]), str(row["period_credit"]), str(row["total_debit"]), str(row["total_credit"]), str(row["final_debit"]), str(row["final_credit"])])

    # SQLite
    db_path = os.path.join(db_dir, "souss_sim_2025.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            company_name TEXT,
            trade_name TEXT,
            segment TEXT,
            ice TEXT,
            identifiant_fiscal TEXT,
            registre_commerce TEXT,
            payment_terms TEXT,
            credit_limit_mad REAL
        );
    """)

    cur.execute("""
        CREATE TABLE sales_invoices (
            invoice_number TEXT PRIMARY KEY,
            invoice_date TEXT,
            due_date TEXT,
            customer_id TEXT,
            total_ht_mad REAL,
            total_tva_mad REAL,
            total_ttc_mad REAL,
            payment_method TEXT,
            status TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id TEXT,
            entry_date TEXT,
            journal_code TEXT,
            piece_ref TEXT,
            event_id TEXT,
            account_number TEXT,
            account_title TEXT,
            debit_mad REAL,
            credit_mad REAL,
            description TEXT
        );
    """)

    for c in sales_gen.customers:
        cur.execute("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (c.customer_id, c.company_name, c.trade_name, c.segment, c.ice, c.identifiant_fiscal, c.registre_commerce, c.payment_terms, float(c.credit_limit_mad)))

    for inv in sales_gen.invoices:
        cur.execute("INSERT INTO sales_invoices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (inv.invoice_number, inv.invoice_date.isoformat(), inv.due_date.isoformat(), inv.customer_id, float(inv.total_ht), float(inv.total_tva), float(inv.total_ttc), inv.payment_method.value, inv.status))

    for entry in ledger.journal:
        for line in entry.lines:
            cur.execute("INSERT INTO journal_entries (entry_id, entry_date, journal_code, piece_ref, event_id, account_number, account_title, debit_mad, credit_mad, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (entry.entry_id, entry.entry_date.isoformat(), entry.journal_code.value, entry.piece_ref, entry.event_id, line.account_number, line.account_title, float(line.debit), float(line.credit), line.description))

    conn.commit()
    conn.close()

    print("\n" + "=" * 80)
    print("SIMULATION COMPLETED SUCCESSFULLY!")
    print(f"Total Sales Invoices Generated : {len(sales_gen.invoices)}")
    print(f"Total Commercial Papers Drawn  : {len(sales_gen.commercial_papers)}")
    print(f"Total Purchase Invoices Posted : {len(purch_gen.invoices)}")
    print(f"Total Payroll Slips Issued     : {len(pay_gen.payroll_slips)}")
    print(f"Total Journal Entries Posted   : {len(ledger.journal)}")
    print(f"Annual Chiffre d'Affaires (HT) : {closing_summary['ca_turnover_ht']:,.2f} MAD")
    print(f"Pre-Tax Accounting Profit      : {closing_summary['pre_tax_accounting_profit']:,.2f} MAD")
    print(f"Taxable Fiscal Profit          : {closing_summary['fiscal_result']:,.2f} MAD")
    print(f"Corporate Tax (IS 2025) Due    : {closing_summary['is_final_due']:,.2f} MAD")
    print(f"Net Result of the Year (Profit): {closing_summary['net_profit']:,.2f} MAD")
    print("=" * 80)


if __name__ == "__main__":
    main()
