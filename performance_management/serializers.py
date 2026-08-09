from decimal import Decimal
from rest_framework import serializers
from .models import AppraisalCycle, Goal, KPI, Appraisal, Rating


class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = '__all__'


class GoalSerializer(serializers.ModelSerializer):
    kpis = KPISerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class AppraisalCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppraisalCycle
        fields = '__all__'


class AppraisalSerializer(serializers.ModelSerializer):
    ratings = RatingSerializer(many=True, read_only=True)
    employee_name = serializers.ReadOnlyField(source='employee.get_full_name')
    cycle_name = serializers.ReadOnlyField(source='cycle.name')

    class Meta:
        model = Appraisal
        fields = [
            'id', 'employee', 'employee_name', 'cycle', 'cycle_name',
            'self_feedback', 'manager_feedback', 'final_score',
            'performance_band', 'status', 'ratings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['final_score', 'performance_band', 'status', 'created_at', 'updated_at']


class SelfReviewSerializer(serializers.Serializer):
    score = serializers.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        required=True, 
        min_value=Decimal('1.00'), 
        max_value=Decimal('5.00')
    )
    feedback = serializers.CharField(required=True, allow_blank=False)
    kpi_id = serializers.IntegerField(required=False, allow_null=True)


class ManagerReviewSerializer(serializers.Serializer):
    score = serializers.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        required=True, 
        min_value=Decimal('1.00'), 
        max_value=Decimal('5.00')
    )
    feedback = serializers.CharField(required=True, allow_blank=False)
    kpi_id = serializers.IntegerField(required=False, allow_null=True)