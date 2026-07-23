from django.contrib import admin
from .models import LeaveType, LeaveBalance, LeaveRequest, CompOffClaim, LeaveEncashment

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'max_days_per_year', 'enable_sandwich_policy')

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'leave_type', 'year', 'allocated', 'used', 'pending')
    raw_id_fields = ('employee', 'leave_type')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'leave_type', 'start_date', 'end_date', 'status', 'calculated_days')
    raw_id_fields = ('employee', 'leave_type', 'level1_approved_by', 'level2_approved_by')

@admin.register(CompOffClaim)
class CompOffClaimAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'worked_date', 'status')
    raw_id_fields = ('employee', 'reviewed_by')

@admin.register(LeaveEncashment)
class LeaveEncashmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'leave_type', 'days_to_encash', 'status')
    raw_id_fields = ('employee', 'leave_type', 'approved_by')