from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


# 1. SOFT DELETE ENGINE CORE

class NonDeletedManager(models.Manager):
    """Custom manager to exclude soft-deleted records by default."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class SoftDeleteModel(models.Model):
    """Abstract base model implementing high-performance logical deletion indices."""
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Base managers architecture assignment
    objects = NonDeletedManager()      # Standard access queries
    all_objects = models.Manager()     # System audit access queries

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """Intercepts hard drop requests and redirects to timestamped soft-deletion flags."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

# 2. CORE MASTER DATA LOOKUPS

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)  # Add null=True, blank=True
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)      # Add null=True, blank=True
    def __str__(self):
        return self.name

class Designation(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)  # Add null=True, blank=True
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)      # Add null=True, blank=True
   
    def __str__(self):
        return self.title


# 3. CORE EMPLOYEE ENTITY

class Employee(SoftDeleteModel):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    # Primary structural fields
    employee_code = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Financial and Organization Fields
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    joining_date = models.DateField()
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Relational foreign constraints
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='employees')
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')

    # Auditing metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_code})"

    @property
    def full_name(self):
        """Calculated field layer aggregating composite name configurations."""
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        """Cross-field enterprise level business validation layer rules."""
        super().clean()
        errors = {}

        # 1. Prevent impossible age configurations
        if self.date_of_birth and (timezone.now().date() - self.date_of_birth).days < 18 * 365:
            errors['date_of_birth'] = "Employee must be at least 18 years old."

        # 2. Logical sequence tracking checks
        if self.joining_date and self.date_of_birth and self.joining_date < self.date_of_birth:
            errors['joining_date'] = "Joining date cannot be prior to birth date."

        # 3. Financial field rule validation
        if self.salary and self.salary <= 0:
            errors['salary'] = "Base allocation salary must be a positive value."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Intercepts saves to compile dynamic sequence generations cleanly."""
        # Auto-Increment Serial Sequence Assignment Blocks
        if not self.employee_code:
            last_emp = Employee._base_manager.all().order_by('-id').first()
            if last_emp and last_emp.id:
                next_number = last_emp.id + 1
            else:
                next_number = 1
            self.employee_code = f"EMP{next_number:04d}"
            
        super().save(*args, **kwargs)


# 4. DOCUMENT AUDIT SUBSYSTEM


def validate_file_extension(value):
    """File attachment whitelist security validator."""
    import os
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError(f'Unsupported file format. Allowed: {", ".join(valid_extensions)}')

class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=100, default='Placeholder Document') # Added default
    file = models.FileField(upload_to='employee_vault/', validators=[validate_file_extension], default='placeholder.pdf') # Added default
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_name} - {self.employee.employee_code}"

# 5. CORE WORKFLOW MODELLING DATA LAYERS


# Look for this class at the bottom of employee/models.py:
class Promotion(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='promotions')
    old_designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='+', null=True, blank=True)
    new_designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='+')
    old_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_salary = models.DecimalField(max_digits=12, decimal_places=2)
    effective_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)

class Transfer(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='transfers')
    old_department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='+', null=True, blank=True)
    new_department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='+')
    transfer_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)

# 6. LIFECYCLE TERMINATION RECORDS
class Resignation(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Review'),
        ('Approved', 'Approved/Processed'),
        ('Rejected', 'Rejected/Retained'),
    ]
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='resignation')
    submission_date = models.DateField(null=True, blank=True, auto_now_add=True)
    notice_end_date = models.DateField(null=True, blank=True)
    
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending', db_index=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)


class Termination(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='termination')
    termination_date = models.DateField()
    reason = models.TextField()
    severance_package = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)

# 7. MUTABLE AUDIT HISTORY TRAIL SYSTEM


class EmployeeHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='history_logs')
    action = models.CharField(max_length=50, db_index=True)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    performed_by_username = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']