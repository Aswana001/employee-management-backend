from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from employee.models import Promotion, Transfer, Termination, EmployeeHistory

@receiver(post_save, sender=Promotion)
def log_and_apply_promotion(sender, instance, created, **kwargs):
    if created:
        employee = instance.employee
        
        # Save old values before changing profile
        old_salary = employee.salary
        old_designation = employee.designation
        
        # Mutate core employee data profile directly
        employee.salary = instance.new_salary
        employee.designation = instance.new_designation
        employee.save()
        
        # Establish structural audit historical tracking logs
        EmployeeHistory.objects.create(
            employee=employee,
            action="PROMOTION",
            old_data={"salary": str(old_salary), "designation": old_designation.title},
            new_data={"salary": str(instance.new_salary), "designation": instance.new_designation.title}
        )

@receiver(post_save, sender=Transfer)
def log_and_apply_transfer(sender, instance, created, **kwargs):
    if created:
        employee = instance.employee
        old_department = employee.department
        
        # Sync profile to match department shifts
        employee.department = instance.new_department
        employee.save()
        
        EmployeeHistory.objects.create(
            employee=employee,
            action="TRANSFER",
            old_data={"department": old_department.name},
            new_data={"department": instance.new_department.name}
        )

@receiver(post_save, sender=Termination)
def log_and_apply_termination(sender, instance, created, **kwargs):
    if created:
        employee = instance.employee
        employee.is_active = False
        employee.save()
        
        EmployeeHistory.objects.create(
            employee=employee,
            action="TERMINATION",
            old_data={"is_active": True},
            new_data={"is_active": False, "reason": instance.reason}
        )