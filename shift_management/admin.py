from django.contrib import admin
from .models import Shift, ShiftAssignment, WeeklySchedule, RotatingShift, ShiftSwapRequest, HolidayShift, OvertimeRule


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    fields = ('shift_name', 'code', 'description', 'start_time', 'end_time', 'break_duration', 'grace_in_minutes', 'grace_out_minutes', 'overtime_after_hours', 'is_active')

@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    fields = ('employee', 'shift', 'effective_from', 'effective_to', 'assignment_type', 'status')
    raw_id_fields = ('employee', 'shift')

@admin.register(WeeklySchedule)
class WeeklyScheduleAdmin(admin.ModelAdmin):
    raw_id_fields = ('employee',)

@admin.register(RotatingShift)
class RotatingShiftAdmin(admin.ModelAdmin):
    raw_id_fields = ('employee',)

@admin.register(ShiftSwapRequest)
class ShiftSwapRequestAdmin(admin.ModelAdmin):
    raw_id_fields = ('requester', 'target_employee', 'requester_shift', 'target_shift')

@admin.register(HolidayShift)
class HolidayShiftAdmin(admin.ModelAdmin):
    raw_id_fields = ('shift', 'assigned_employee')

@admin.register(OvertimeRule)
class OvertimeRuleAdmin(admin.ModelAdmin):
    raw_id_fields = ('applicable_shift',)