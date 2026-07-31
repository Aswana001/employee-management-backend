from rest_framework import serializers
from .models import AppraisalCycle, Goal, Appraisal

class AppraisalCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppraisalCycle
        fields = '__all__'


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'


class AppraisalSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.get_full_name')
    cycle_name = serializers.ReadOnlyField(source='cycle.name')

    class Meta:
        model = Appraisal
        fields = [
            'id', 'employee', 'employee_name', 'cycle', 'cycle_name',
            'self_feedback', 'self_rating', 'manager_feedback', 'manager_rating',
            'final_score', 'performance_band', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['final_score', 'performance_band', 'status', 'created_at', 'updated_at']


class SelfReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appraisal
        fields = ['self_feedback', 'self_rating']


class ManagerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appraisal
        fields = ['manager_feedback', 'manager_rating']


class CalibrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appraisal
        fields = ['final_score', 'performance_band']