from django.db import models
from django.utils import timezone
from .constants import BATCH_STATUS_CHOICES, COMPONENT_TYPE_CHOICES, SETTLEMENT_STATUS_CHOICES

class SalaryStructure(models.Model):
    employee = models.OneToOneField('employee.Employee', on_delete=models.CASCADE, related_name='salary_structure')
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    conveyance_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Statutory Configurations
    enable_pf = models.BooleanField(default=True)
    pf_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=12.00) # 12%
    enable_esi = models.BooleanField(default=False)
    esi_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0.75) # 0.75%
    tds_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def gross_monthly_nominal(self):
        return self.basic_salary + self.hra + self.conveyance_allowance + self.medical_allowance + self.special_allowance

    def __str__(self):
        return f"Salary Structure - Emp #{self.employee_id}"

class PayrollBatch(models.Model):
    month = models.PositiveIntegerField() # 1-12
    year = models.PositiveIntegerField()  # e.g., 2026
    status = models.CharField(max_length=20, choices=BATCH_STATUS_CHOICES, default='DRAFT')
    processed_by = models.ForeignKey('employee.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('month', 'year')

    def __str__(self):
        return f"Payroll Batch {self.month}/{self.year} [{self.status}]"

class PayrollComponent(models.Model):
    """ One-off Variable Additions (Bonuses, Incentives, Arrears) """
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='payroll_components')
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.component_type} - Emp #{self.employee_id}: ${self.amount}"

class PayrollRecord(models.Model):
    """ The Individual Monthly Payslip """
    batch = models.ForeignKey(PayrollBatch, on_delete=models.CASCADE, related_name='records')
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='payroll_records')
    
    # Days & Rates
    total_month_days = models.PositiveIntegerField(default=30)
    lop_days = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    worked_days = models.DecimalField(max_digits=4, decimal_places=1, default=30.0)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Earned Incomes (Post LOP Adjustment)
    earned_basic = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    earned_hra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    earned_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Additions
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    incentives = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    gross_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Deductions
    lop_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pf_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    esi_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tds_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('batch', 'employee')

    def __str__(self):
        return f"Payslip Emp #{self.employee_id} ({self.batch.month}/{self.batch.year})"

class FinalSettlement(models.Model):
    """ Full & Final (F&F) Settlement for Departing Staff """
    employee = models.OneToOneField('employee.Employee', on_delete=models.CASCADE, related_name='final_settlement')
    resignation_date = models.DateField()
    last_working_day = models.DateField()
    
    # Calculations
    encashable_leave_days = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    leave_encashment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    notice_period_shortfall_days = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    notice_penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    other_pending_dues = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    asset_damage_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    net_settlement_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=SETTLEMENT_STATUS_CHOICES, default='PENDING')
    processed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"F&F Settlement - Emp #{self.employee_id} (${self.net_settlement_amount})"