from django.db import models
from django.conf import settings


class JobOpening(models.Model):
    JOB_TYPE_CHOICES = (
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERN', 'Internship'),
    )
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('ON_HOLD', 'On Hold'),
    )

    title = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='FULL_TIME')
    description = models.TextField()
    requirements = models.TextField()
    openings_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.department}"


class Candidate(models.Model):
    STAGE_CHOICES = (
        ('APPLIED', 'Applied'),
        ('SCREENING', 'Screening'),
        ('INTERVIEW', 'Interviewing'),
        ('OFFERED', 'Offer Extended'),
        ('HIRED', 'Hired'),
        ('REJECTED', 'Rejected'),
    )

    job_opening = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name='candidates')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='APPLIED')
    notes = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.job_opening.title})"


class Interview(models.Model):
    INTERVIEW_TYPE_CHOICES = (
        ('SCREENING', 'HR Screening'),
        ('TECHNICAL', 'Technical Round'),
        ('MANAGER', 'Managerial Round'),
        ('HR_FINAL', 'Final HR Round'),
    )
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='interviews')
    interviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conducted_interviews')
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=45)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    feedback = models.TextField(blank=True, null=True)
    rating = models.PositiveSmallIntegerField(blank=True, null=True)  # Scale 1-5

    def __str__(self):
        return f"{self.interview_type} for {self.candidate.first_name} on {self.scheduled_at}"


class Offer(models.Model):
    STATUS_CHOICES = (
        ('GENERATED', 'Generated'),
        ('SENT', 'Sent'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    )

    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='offer')
    designation = models.CharField(max_length=255)
    offered_salary = models.DecimalField(max_digits=12, decimal_places=2)
    joining_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='GENERATED')
    offer_letter_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer for {self.candidate.first_name} - {self.designation}"


class OnboardingChecklist(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    )

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='onboarding_tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    due_date = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.candidate.first_name} ({self.status})"