from django.contrib import admin
from employee.models import (
    Department, Designation, Employee, EmployeeDocument, 
    Promotion, Transfer, Resignation, Termination, EmployeeHistory
)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'first_name', 'last_name', 'email', 'department', 'designation', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'employee_code')
    list_filter = ('department', 'designation', 'is_active', 'gender')
    ordering = ('employee_code',)
    readonly_fields = ('employee_code', 'created_at', 'updated_at')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)

admin.site.register(EmployeeDocument)
admin.site.register(Promotion)
admin.site.register(Transfer)
admin.site.register(Resignation)
admin.site.register(Termination)
admin.site.register(EmployeeHistory)