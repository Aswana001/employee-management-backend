from rest_framework import serializers
from .models import ShiftAssignment

def validate_shift_overlap(employee, effective_from, effective_to, current_id=None):
    # Validates absolute timeline intersection matrices to protect against parallel duplicate schedules
    qs = ShiftAssignment.objects.filter(employee=employee, status='Active')
    if current_id:
        qs = qs.exclude(id=current_id)
        
    for assignment in qs:
        # Evaluate date convergence fields
        start_max = max(assignment.effective_from, effective_from)
        end_min = min(assignment.effective_to, effective_to) if (assignment.effective_to and effective_to) else (assignment.effective_to or effective_to)
        
        if end_min is None or start_max <= end_min:
            raise serializers.ValidationError("Operational Constraint Collision: Employee has an overlapping shift block assigned within this date window.")