from django.db import models
from django.conf import settings

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)  # e.g., Travel, Client Lunch, Office Supplies
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class ExpenseClaim(models.Model):
    STATUS_CHOICES = [
        ('PENDING_MANAGER', 'Pending Manager Approval'),
        ('APPROVED_MANAGER', 'Manager Approved / Pending Finance'),
        ('REJECTED', 'Rejected'),
        ('REIMBURSED', 'Reimbursed / Paid'),
    ]

    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='expense_claims')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='claims')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    description = models.TextField()
    receipt = models.FileField(upload_to='receipts/%Y/%m/', blank=True, null=True)

    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING_MANAGER')
    rejection_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.amount} ({self.status})"