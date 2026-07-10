import django_filters
from employee.models import Employee

class EmployeeFilter(django_filters.FilterSet):
    """
    Enterprise-grade declarative filter engine for the Employee model dataset.
    Permits clean, type-safe filtering across structural entity keys.
    """
    department = django_filters.NumberFilter(field_name='department__id', lookup_expr='exact')
    designation = django_filters.NumberFilter(field_name='designation__id', lookup_expr='exact')
    reporting_manager = django_filters.NumberFilter(field_name='reporting_manager__id', lookup_expr='exact')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Employee
        fields = ['department', 'designation', 'reporting_manager', 'is_active']