import django_filters
from .models import Shift, ShiftAssignment

class ShiftFilter(django_filters.FilterSet):
    class Meta:
        model = Shift
        fields = {
            'is_night_shift': ['exact'],
            'is_active': ['exact'],
            'shift_name': ['icontains'],
            'code': ['exact'],
        }

class ShiftAssignmentFilter(django_filters.FilterSet):
    department = django_filters.NumberFilter(field_name='employee__department_id')
    
    class Meta:
        model = ShiftAssignment
        fields = {
            'employee': ['exact'],
            'shift': ['exact'],
            'status': ['exact'],
            'effective_from': ['gte', 'lte'],
        }