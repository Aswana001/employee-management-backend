import calendar
from decimal import Decimal
from django.db import models
from .models import SalaryStructure, PayrollBatch, PayrollRecord, PayrollComponent

def compute_employee_payslip(employee, month, year, batch, lop_days=Decimal('0.0')):
    """
    Core Mathematical Engine for Monthly Payroll Computation.
    Applies Loss of Pay (LOP) dynamically across Earned Salary, PF, ESI, and TDS.
    """
    try:
        structure = employee.salary_structure
    except SalaryStructure.DoesNotExist:
        return None

    # 1. Total days in target month
    num_days = calendar.monthrange(year, month)[1]
    num_days_dec = Decimal(str(num_days))
    
    # 2. Daily Rate & Worked Ratio
    gross_nominal = structure.gross_monthly_nominal
    daily_rate = round(gross_nominal / num_days_dec, 2)
    
    worked_days = max(Decimal('0.0'), num_days_dec - Decimal(str(lop_days)))
    ratio = worked_days / num_days_dec

    # 3. Earned Fixed Components
    earned_basic = round(structure.basic_salary * ratio, 2)
    earned_hra = round(structure.hra * ratio, 2)
    earned_allowances = round((structure.conveyance_allowance + structure.medical_allowance + structure.special_allowance) * ratio, 2)
    lop_deduction = round(daily_rate * Decimal(str(lop_days)), 2)

    # 4. Fetch One-Off Additions (Bonuses, Incentives, Arrears)
    components = PayrollComponent.objects.filter(employee=employee, month=month, year=year, is_processed=False)
    
    bonuses = components.filter(component_type='BONUS').aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
    incentives = components.filter(component_type='INCENTIVE').aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
    arrears = components.filter(component_type='ARREARS').aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    overtime_pay = Decimal('0.00')  # Integrated dynamically from Attendance/Shift module

    # 5. Total Gross Earnings
    gross_earnings = earned_basic + earned_hra + earned_allowances + bonuses + incentives + arrears + overtime_pay

    # 6. Statutory Deductions (Calculated on Earned Basic)
    pf_amount = Decimal('0.00')
    if structure.enable_pf:
        pf_amount = round(earned_basic * (structure.pf_percentage / Decimal('100.00')), 2)

    esi_amount = Decimal('0.00')
    if structure.enable_esi:
        esi_amount = round(gross_earnings * (structure.esi_percentage / Decimal('100.00')), 2)

    tds_amount = structure.tds_monthly

    total_deductions = pf_amount + esi_amount + tds_amount + lop_deduction
    net_salary = max(Decimal('0.00'), gross_earnings - total_deductions)

    # 7. Write to database
    record, _ = PayrollRecord.objects.update_or_create(
        batch=batch,
        employee=employee,
        defaults={
            'total_month_days': num_days,
            'lop_days': lop_days,
            'worked_days': worked_days,
            'daily_rate': daily_rate,
            'earned_basic': earned_basic,
            'earned_hra': earned_hra,
            'earned_allowances': earned_allowances,
            'bonuses': bonuses,
            'incentives': incentives,
            'arrears': arrears,
            'overtime_pay': overtime_pay,
            'gross_earnings': gross_earnings,
            'lop_deduction': lop_deduction,
            'pf_amount': pf_amount,
            'esi_amount': esi_amount,
            'tds_amount': tds_amount,
            'total_deductions': total_deductions,
            'net_salary': net_salary,
        }
    )

    # Mark variable components as processed
    components.update(is_processed=True)
    return record