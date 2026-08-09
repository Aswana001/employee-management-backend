from django.db import models
from employee.models import Employee  

class AppraisalCycle(models.Model):
    name = models.CharField(max_length=150)
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
    weightage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weightage percentage e.g., 30.00")
    target_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.title} - {self.employee}"


class KPI(models.Model):
    """Separate model to define specific, measurable targets attached to a Goal."""
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='kpis')
    title = models.CharField(max_length=255)
    target_value = models.CharField(max_length=100, help_text="e.g., Response time < 200ms or 95% resolution")
    achieved_value = models.CharField(max_length=100, blank=True, null=True)
    is_met = models.BooleanField(default=False)

    def __str__(self):
        return f"KPI: {self.title} (Goal: {self.goal.title})"


class Appraisal(models.Model):
    STATUS_CHOICES = [
        ('PENDING_SELF', 'Pending Self Review'),
        ('SUBMITTED_SELF', 'Self Review Submitted'),
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
    self_feedback = models.TextField(blank=True, null=True)
    manager_feedback = models.TextField(blank=True, null=True)
    final_score = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    performance_band = models.CharField(max_length=30, choices=BAND_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING_SELF')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appraisal: {self.employee} ({self.cycle.name})"


class Rating(models.Model):
    """Separate model to store individual ratings given during self and manager reviews."""
    RATING_TYPE_CHOICES = [
        ('SELF', 'Self Rating'),
        ('MANAGER', 'Manager Rating'),
        ('HR', 'HR Rating'),
    ]

    appraisal = models.ForeignKey(Appraisal, on_delete=models.CASCADE, related_name='ratings')
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, related_name='ratings', null=True, blank=True)
    rating_type = models.CharField(max_length=10, choices=RATING_TYPE_CHOICES)
    score = models.DecimalField(max_digits=3, decimal_places=2, help_text="Rating score e.g., 4.50 out of 5.0")
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating_type} ({self.score}) - Appraisal #{self.appraisal.id}"
    