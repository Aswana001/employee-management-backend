from django.contrib import admin
from .models import SalaryStructure, PayrollBatch, PayrollComponent, PayrollRecord, FinalSettlement

@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'basic_salary', 'hra', 'gross_monthly_nominal', 'enable_pf')
    raw_id_fields = ('employee',)

@admin.register(PayrollBatch)
class PayrollBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'month', 'year', 'status', 'created_at')

@admin.register(PayrollComponent)
class PayrollComponentAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'component_type', 'amount', 'month', 'year', 'is_processed')
    raw_id_fields = ('employee',)

@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'batch', 'gross_earnings', 'total_deductions', 'net_salary')
    raw_id_fields = ('batch', 'employee')

@admin.register(FinalSettlement)
class FinalSettlementAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'net_settlement_amount', 'status')
    raw_id_fields = ('employee',)