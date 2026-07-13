from django.contrib import admin
from .models import Shift, Attendance, AttendanceRegularization


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    fields = ('name', 'start_time', 'end_time', 'grace_period_mins')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    fields = ('employee', 'date', 'shift', 'check_in', 'check_in_latitude', 'check_in_longitude', 'check_out', 'check_out_latitude', 'check_out_longitude')

@admin.register(AttendanceRegularization)
class AttendanceRegularizationAdmin(admin.ModelAdmin):
    fields = ('attendance', 'requested_by', 'reason', 'corrected_check_in', 'corrected_check_out', 'status', 'approved_by_username')