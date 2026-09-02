# -*- coding: utf-8 -*-
"""
Payroll & Social Security Generation Engine for Souss Agri-Pack SARL.
Generates monthly bulletins de paie, CNSS/AMO contributions, and IR withholdings.
Posts all journal entries dynamically through journal_templates.yaml using Decimal.
"""

from datetime import date
from decimal import Decimal
from typing import List, Dict, Tuple
import yaml

from generator.models import Employee, PayrollSlip, to_dec
from generator.pcm_ledger_engine import PCMLedgerEngine
from generator.parameters_engine import ParameterEngine


class PayrollGenerator:
    def __init__(self, ledger: PCMLedgerEngine, param_engine: ParameterEngine, payroll_grid_path: str):
        self.ledger = ledger
        self.param_engine = param_engine
        self.employees = self._load_employees(payroll_grid_path)
        self.payroll_slips: List[PayrollSlip] = []
        self.slip_counter = 1
        self.journal_counter = 1000

    def _load_employees(self, path: str) -> List[Employee]:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        employees = []
        for emp in data.get("employees", []):
            name_parts = emp.get("full_name", "").split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            is_seasonal = (emp.get("contract_type") == "CDD Saisonnier") or (emp.get("months_active", 12) == 6)

            employees.append(Employee(
                employee_id=emp["id"],
                first_name=first_name,
                last_name=last_name,
                cin=emp["cin"],
                cnss_number=str(emp["cnss"]),
                department=emp["department"],
                position=emp["job_title"],
                hire_date="2020-01-02",
                monthly_gross_mad=to_dec(emp["monthly_gross_mad"]),
                dependents_count=int(emp.get("dependents_count", 2)),
                is_seasonal=is_seasonal,
                seasonal_months=[1, 2, 3, 10, 11, 12] if is_seasonal else []
            ))
        return employees

    def _compute_ir_monthly(self, gross: Decimal, cnss_sal: Decimal, amo_sal: Decimal, dependents: int) -> Tuple[Decimal, Decimal, Decimal]:
        sbi = to_dec(gross - (cnss_sal + amo_sal))
        frais_pro = min(to_dec(sbi * Decimal("0.20")), Decimal("2500.00"))
        sni = max(Decimal("0.00"), to_dec(sbi - frais_pro))
        annual_sni = to_dec(sni * Decimal("12.00"))

        if annual_sni <= Decimal("40000.00"):
            rate = Decimal("0.00")
            deduction = Decimal("0.00")
        elif annual_sni <= Decimal("60000.00"):
            rate = Decimal("0.10")
            deduction = Decimal("4000.00")
        elif annual_sni <= Decimal("80000.00"):
            rate = Decimal("0.20")
            deduction = Decimal("10000.00")
        elif annual_sni <= Decimal("100000.00"):
            rate = Decimal("0.30")
            deduction = Decimal("18000.00")
        elif annual_sni <= Decimal("180000.00"):
            rate = Decimal("0.34")
            deduction = Decimal("22000.00")
        else:
            rate = Decimal("0.37")
            deduction = Decimal("27400.00")

        annual_ir_brut = max(Decimal("0.00"), to_dec((annual_sni * rate) - deduction))
        monthly_ir_brut = to_dec(annual_ir_brut / Decimal("12.00"))

        dep_count = min(dependents, 6)
        family_ded_monthly = to_dec((Decimal("500.00") * Decimal(str(dep_count))) / Decimal("12.00"))
        ir_net_withheld = max(Decimal("0.00"), to_dec(monthly_ir_brut - family_ded_monthly))

        return frais_pro, monthly_ir_brut, ir_net_withheld

    def generate_month_payroll(self, year: int, month: int) -> List[PayrollSlip]:
        slips = []
        gross_perm = Decimal("0.00")
        gross_seas = Decimal("0.00")
        cnss_emp_total = Decimal("0.00")
        ir_total = Decimal("0.00")
        cnss_pat_prest = Decimal("0.00")
        cnss_pat_amo_fp = Decimal("0.00")
        at_ins_total = Decimal("0.00")

        period_str = f"{year}-{month:02d}"
        payroll_date = date(year, month, 28 if month == 2 else 30)

        for emp in self.employees:
            if emp.is_seasonal and month not in emp.seasonal_months:
                continue

            gross = emp.monthly_gross_mad
            cnss_cap = Decimal("6000.00")
            cnss_sal = to_dec(min(gross, cnss_cap) * Decimal("0.0448"))
            amo_sal = to_dec(gross * Decimal("0.0226"))
            frais_pro, ir_brut, ir_net = self._compute_ir_monthly(gross, cnss_sal, amo_sal, emp.dependents_count)
            net_payable = to_dec(gross - (cnss_sal + amo_sal + ir_net))

            cnss_prest_pat = to_dec(min(gross, cnss_cap) * Decimal("0.0898"))
            alloc_fam = to_dec(gross * Decimal("0.0640"))
            form_pro = to_dec(gross * Decimal("0.0160"))
            amo_pat = to_dec(gross * Decimal("0.0226"))
            amo_sol = to_dec(gross * Decimal("0.0185"))
            total_emp_cnss = to_dec(cnss_prest_pat + alloc_fam + form_pro + amo_pat + amo_sol)
            at_ins = to_dec(gross * Decimal("0.0380"))

            slip = PayrollSlip(
                slip_id=f"BUL-{year}-{self.slip_counter:05d}",
                month_period=period_str,
                employee_id=emp.employee_id,
                employee_name=f"{emp.first_name} {emp.last_name}",
                position=emp.position,
                cin=emp.cin,
                cnss_number=emp.cnss_number,
                gross_salary_mad=gross,
                cnss_prestations_employee_mad=cnss_sal,
                amo_employee_mad=amo_sal,
                salaire_brut_imposable_mad=to_dec(gross - (cnss_sal + amo_sal)),
                frais_professionnels_mad=frais_pro,
                salaire_net_imposable_mad=to_dec(gross - (cnss_sal + amo_sal + frais_pro)),
                ir_brut_mad=ir_brut,
                family_deductions_mad=to_dec(min(emp.dependents_count, 6) * (Decimal("500.00") / Decimal("12.00"))),
                ir_net_withheld_mad=ir_net,
                net_payable_mad=net_payable,
                cnss_prestations_employer_mad=cnss_prest_pat,
                allocations_familiales_mad=alloc_fam,
                formation_pro_mad=form_pro,
                amo_employer_mad=amo_pat,
                amo_solidarite_mad=amo_sol,
                total_cnss_employer_mad=total_emp_cnss,
                at_insurance_employer_mad=at_ins,
                total_employer_cost_mad=to_dec(gross + total_emp_cnss + at_ins)
            )
            slips.append(slip)
            self.payroll_slips.append(slip)
            self.slip_counter += 1

            if emp.is_seasonal:
                gross_seas += gross
            else:
                gross_perm += gross

            cnss_emp_total += (cnss_sal + amo_sal)
            ir_total += ir_net
            cnss_pat_prest += (cnss_prest_pat + alloc_fam)
            cnss_pat_amo_fp += (form_pro + amo_pat + amo_sol)
            at_ins_total += at_ins

        # Post EVT-PAY-001 (Salaires bruts)
        entry_id_1 = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        ctx_pay1 = {
            "gross_permanent": gross_perm,
            "gross_seasonal": gross_seas
        }
        self.ledger.post_event("EVT-PAY-001", entry_id_1, payroll_date, f"PAIE-{period_str}", ctx_pay1, f"Salaires bruts {period_str}")

        # Post EVT-PAY-002 (Retenues salariales)
        entry_id_2 = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        ctx_pay2 = {
            "cnss_employee_total": cnss_emp_total,
            "ir_withheld_total": ir_total
        }
        self.ledger.post_event("EVT-PAY-002", entry_id_2, payroll_date, f"RET-{period_str}", ctx_pay2, f"Retenues CNSS/IR {period_str}")

        # Post EVT-PAY-003 (Charges patronales & AT)
        entry_id_3 = f"JRN-{year}-{self.journal_counter:05d}"
        self.journal_counter += 1
        ctx_pay3 = {
            "cnss_employer_prestations": cnss_pat_prest,
            "cnss_employer_amo_fp": cnss_pat_amo_fp,
            "at_insurance_cost": at_ins_total
        }
        self.ledger.post_event("EVT-PAY-003", entry_id_3, payroll_date, f"CHG-SOC-{period_str}", ctx_pay3, f"Charges patronales {period_str}")

        return slips
