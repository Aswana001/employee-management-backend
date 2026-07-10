from rest_framework import serializers
from django.contrib.auth.models import User
from employee.models import (
    Department, Designation, Employee, EmployeeDocument, 
    Promotion, Transfer, Resignation, Termination, EmployeeHistory
)

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = '__all__'


class EmployeeMinimalSerializer(serializers.ModelSerializer):
    """Used to safely expose nested reporting manager structures without recursion loops."""
    class Meta:
        model = Employee
        fields = ['id', 'employee_code', 'first_name', 'last_name', 'email']


class EmployeeSerializer(serializers.ModelSerializer):
    # Write paths accept simple primary key IDs
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    designation = serializers.PrimaryKeyRelatedField(queryset=Designation.objects.all())
    reporting_manager = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['employee_code', 'is_active', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        """Cross-field evaluation logic validation at the serializer level."""
        # Handle update operations where fields might be partial
        joining_date = data.get('joining_date', getattr(self.instance, 'joining_date', None))
        date_of_birth = data.get('date_of_birth', getattr(self.instance, 'date_of_birth', None))
        reporting_manager = data.get('reporting_manager', getattr(self.instance, 'reporting_manager', None))

        if reporting_manager and self.instance and reporting_manager == self.instance:
            raise serializers.ValidationError({"reporting_manager": "An employee cannot report to themselves."})
            
        if joining_date and date_of_birth and joining_date < date_of_birth:
            raise serializers.ValidationError({"joining_date": "The joining date cannot be prior to the date of birth."})
            
        return data

    def to_representation(self, instance):
        """
        Dynamically intercepts the read pipeline to substitute flat raw IDs
        with fully inflated nested JSON object representations.
        """
        representation = super().to_representation(instance)
        representation['department'] = DepartmentSerializer(instance.department).data
        representation['designation'] = DesignationSerializer(instance.designation).data
        if instance.reporting_manager:
            representation['reporting_manager'] = EmployeeMinimalSerializer(instance.reporting_manager).data
        else:
            representation['reporting_manager'] = None
        return representation


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = '__all__'


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'

    def validate(self, data):
        # Enforce that the promotion changes data logically
        if data['old_designation'] == data['new_designation'] and data['old_salary'] == data['new_salary']:
            raise serializers.ValidationError("A promotion must provide either an updated designation or a salary adjustment.")
        return data


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'


class ResignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resignation
        fields = '__all__'
        read_only_fields = ['status']


class TerminationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Termination
        fields = '__all__'


class EmployeeHistorySerializer(serializers.ModelSerializer):
    performed_by_username = serializers.CharField(source='performed_by.username', read_only=True)

    class Meta:
        model = EmployeeHistory
        fields = ['id', 'employee', 'action', 'old_data', 'new_data', 'performed_by_username', 'timestamp']