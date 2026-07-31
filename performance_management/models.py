from django.db import models
from employee.models import Employee  

class AppraisalCycle(models.Model):
    name = models.CharField(max_length=150) # e.g., "Annual Review 2026"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Goal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('ACHIEVED', 'Achieved'),
        ('MISSED', 'Missed'),
    ]

    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=255)
    description = models.TextField()
    kpi_metric = models.TextField(help_text="Measurable target, e.g., Response time < 200ms")
    weightage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage weightage e.g., 30.00 for 30%")
    target_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.title} - {self.employee}"


class Appraisal(models.Model):
    STATUS_CHOICES = [
        ('PENDING_SELF', 'Pending Self Review'),
        ('SUBMITTED_SELF', 'Self Review Submitted / Pending Manager'),
        ('COMPLETED', 'Completed & Scored'),
        ('CALIBRATED', 'Calibrated by HR'),
    ]

    BAND_CHOICES = [
        ('EXCEEDS', 'Exceeds Expectations'),
        ('MEETS', 'Meets Expectations'),
        ('NEEDS_IMPROVEMENT', 'Needs Improvement'),
    ]

    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='appraisals')
    cycle = models.ForeignKey(AppraisalCycle, on_delete=models.CASCADE, related_name='appraisals')
    
    # Self Review Fields
    self_feedback = models.TextField(blank=True, null=True)
    self_rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    
    # Manager Review Fields
    manager_feedback = models.TextField(blank=True, null=True)
    manager_rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    
    # Final Calculated Fields
    final_score = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    performance_band = models.CharField(max_length=30, choices=BAND_CHOICES, blank=True, null=True)
    
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING_SELF')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appraisal: {self.employee} ({self.cycle})"