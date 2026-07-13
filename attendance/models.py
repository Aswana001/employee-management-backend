from django.db import models
from django.utils import timezone

class Shift(models.Model):
    name = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_period_mins = models.IntegerField(default=15)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    # Cross-app link using lazy string referencing
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, null=True, blank=True)
    
    check_in = models.DateTimeField(null=True, blank=True)
    check_in_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    check_in_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    check_out = models.DateTimeField(null=True, blank=True)
    check_out_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    check_out_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    is_late = models.BooleanField(default=False)
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    is_valid_geofence = models.BooleanField(default=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"Emp ID {self.employee_id} - {self.date}"

class AttendanceRegularization(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='regularizations')
    requested_by = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='+')
    reason = models.TextField()
    corrected_check_in = models.DateTimeField(null=True, blank=True)
    corrected_check_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    approved_by_username = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
