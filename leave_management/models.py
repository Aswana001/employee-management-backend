from django.db import models
from django.utils import timezone
from .constants import (
    LEAVE_SPAN_CHOICES, APPROVAL_STATUS_CHOICES, 
    COMP_OFF_STATUS_CHOICES, ENCASHMENT_STATUS_CHOICES
)

class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "Casual Leave", "Sick Leave", "Comp-Off"
    code = models.CharField(max_length=10, unique=True)  # e.g., "CL", "SL", "COMP"
    max_days_per_year = models.DecimalField(max_digits=5, decimal_places=1, default=12.0)
    allow_half_day = models.BooleanField(default=True)
    is_encashable = models.BooleanField(default=False)
    enable_sandwich_policy = models.BooleanField(default=False)
    requires_attachment = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class LeaveBalance(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(default=2026)
    allocated = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    used = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    pending = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)

    class Meta:
        unique_together = ('employee', 'leave_type', 'year')

    @property
    def remaining(self):
        return self.allocated - self.used - self.pending

    def __str__(self):
        return f"Emp {self.employee_id} - {self.leave_type.code}: {self.remaining} left"

class LeaveRequest(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_span = models.CharField(max_length=20, choices=LEAVE_SPAN_CHOICES, default='FULL_DAY')
    calculated_days = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    sandwiched_days = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    reason = models.TextField()
    attachment = models.FileField(upload_to='leave_attachments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='PENDING_L1')
    
    # Audit Trail
    level1_approved_by = models.ForeignKey('employee.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    level1_approved_at = models.DateTimeField(null=True, blank=True)
    level2_approved_by = models.ForeignKey('employee.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    level2_approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.id} - Emp {self.employee_id} ({self.status})"

class CompOffClaim(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='comp_off_claims')
    worked_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=COMP_OFF_STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey('employee.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

class LeaveEncashment(models.Model):
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='encashment_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    days_to_encash = models.DecimalField(max_digits=4, decimal_places=1)
    status = models.CharField(max_length=15, choices=ENCASHMENT_STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey('employee.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)