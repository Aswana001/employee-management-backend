from django.db import models
from django.utils import timezone
from datetime import datetime
from .constants import ASSIGNMENT_TYPES, ASSIGNMENT_STATUS, ROTATION_TYPES, SWAP_STATUS

class Shift(models.Model):
    shift_name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_duration = models.PositiveIntegerField(help_text="Duration in minutes")
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_night_shift = models.BooleanField(default=False)
    grace_in_minutes = models.PositiveIntegerField(default=15)
    grace_out_minutes = models.PositiveIntegerField(default=15)
    overtime_after_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automated Night Shift Verification System Detection Rule Logic
        if self.end_time < self.start_time:
            self.is_night_shift = True
        else:
            self.is_night_shift = False
            
        # Programmatic Duration Aggregation Rule Logic
        today = timezone.now().date()
        dt_start = datetime.combine(today, self.start_time)
        dt_end = datetime.combine(today, self.end_time)
        if self.is_night_shift:
            dt_end += timezone.timedelta(days=1)
        
        total_secs = (dt_end - dt_start).total_seconds()
        self.total_hours = round(max(0.0, (total_secs / 3600.0) - (self.break_duration / 60.0)), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.shift_name} ({self.code})"

class ShiftAssignment(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='shift_assignments')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='assignments')
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    assigned_by = models.ForeignKey('employee.Employee', on_delete=models.SET_NULL, null=True, related_name='+')
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES, default='Permanent')
    status = models.CharField(max_length=15, choices=ASSIGNMENT_STATUS, default='Active')

class WeeklySchedule(models.Model):
    employee = models.OneToOneField('employee.Employee', on_delete=models.CASCADE, related_name='weekly_schedule')
    monday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    tuesday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    wednesday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    thursday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    friday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    saturday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    sunday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

class RotatingShift(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='rotations')
    rotation_name = models.CharField(max_length=100)
    rotation_type = models.CharField(max_length=30, choices=ROTATION_TYPES)
    rotation_start = models.DateField()
    rotation_end = models.DateField(null=True, blank=True)
    next_rotation_date = models.DateField()
    is_active = models.BooleanField(default=True)

class ShiftSwapRequest(models.Model):
    requester = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='swap_requests_made')
    target_employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='swap_requests_received')
    requester_shift = models.ForeignKey(ShiftAssignment, on_delete=models.CASCADE, related_name='+')
    target_shift = models.ForeignKey(ShiftAssignment, on_delete=models.CASCADE, related_name='+')
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=SWAP_STATUS, default='Pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey('employee.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    approved_at = models.DateTimeField(null=True, blank=True)

class HolidayShift(models.Model):
    holiday_name = models.CharField(max_length=100)
    date = models.DateField()
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    assigned_employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='holiday_shifts')
    overtime_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=2.00)
    remarks = models.TextField(blank=True, null=True)

class OvertimeRule(models.Model):
    minimum_hours = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    overtime_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.50)
    maximum_daily_overtime = models.DecimalField(max_digits=4, decimal_places=2, default=4.00)
    maximum_weekly_overtime = models.DecimalField(max_digits=4, decimal_places=2, default=20.00)
    applicable_shift = models.ForeignKey(Shift, on_delete=models.CASCADE, null=True, blank=True, related_name='overtime_rules')
    active = models.BooleanField(default=True)
