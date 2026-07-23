from rest_framework import serializers
from decimal import Decimal
from .models import LeaveType, LeaveBalance, LeaveRequest, CompOffClaim, LeaveEncashment
from .services import calculate_leave_days

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_code = serializers.CharField(source='leave_type.code', read_only=True)
    remaining_days = serializers.DecimalField(source='remaining', max_digits=5, decimal_places=1, read_only=True)

    class Meta:
        model = LeaveBalance
        fields = '__all__'

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['calculated_days', 'sandwiched_days', 'status', 'level1_approved_by', 'level2_approved_by']

    def validate(self, attrs):
        start = attrs.get('start_date')
        end = attrs.get('end_date')
        leave_type = attrs.get('leave_type')
        employee = attrs.get('employee')
        span = attrs.get('leave_span', 'FULL_DAY')

        if end < start:
            raise serializers.ValidationError("Validation Error: End date cannot be earlier than start date.")

        if span in ['FIRST_HALF', 'SECOND_HALF'] and start != end:
            raise serializers.ValidationError("Validation Error: Half-day requests must be for a single day.")

        # Calculate days & sandwich additions
        total_days, sandwich_days = calculate_leave_days(start, end, span, leave_type.enable_sandwich_policy)

        # Balance check
        balance = LeaveBalance.objects.filter(employee=employee, leave_type=leave_type, year=start.year).first()
        available = balance.remaining if balance else Decimal('0.0')

        if available < total_days:
            raise serializers.ValidationError(f"Insufficient Balance: Required {total_days} days, but only {available} days available.")

        attrs['calculated_days'] = total_days
        attrs['sandwiched_days'] = sandwich_days
        return attrs

class CompOffClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompOffClaim
        fields = '__all__'
        read_only_fields = ['status', 'reviewed_by']

class LeaveEncashmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveEncashment
        fields = '__all__'
        read_only_fields = ['status', 'approved_by']