from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, time
from decimal import Decimal
from .models import Shift, ShiftAssignment, WeeklySchedule, RotatingShift, ShiftSwapRequest, HolidayShift, OvertimeRule
from .validators import validate_shift_overlap

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'
        read_only_fields = ['total_hours', 'is_night_shift']

class ShiftAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftAssignment
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('shift').is_active:
            raise serializers.ValidationError("Structural State Error: Cannot instantiate assignments targeting inactive shifts.")
        validate_shift_overlap(
            attrs.get('employee'),
            attrs.get('effective_from'),
            attrs.get('effective_to')
        )
        return attrs

class WeeklyScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklySchedule
        fields = '__all__'

class RotatingShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = RotatingShift
        fields = '__all__'

class ShiftSwapRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftSwapRequest
        fields = '__all__'
        read_only_fields = ['status', 'approved_by', 'approved_at']

class HolidayShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayShift
        fields = '__all__'

    def validate(self, attrs):
        # Enforce target structural cross checks
        if HolidayShift.objects.filter(date=attrs['date'], assigned_employee=attrs['assigned_employee']).exists():
            raise serializers.ValidationError("Double Booking Error: This individual has already been assigned to an operational field holiday schedule today.")
        return attrs

class OvertimeRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimeRule
        fields = '__all__'