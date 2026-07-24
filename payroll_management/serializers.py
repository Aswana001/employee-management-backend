from rest_framework import serializers
from .models import SalaryStructure, PayrollBatch, PayrollComponent, PayrollRecord, FinalSettlement

class SalaryStructureSerializer(serializers.ModelSerializer):
    gross_monthly_nominal = serializers.DecimalField(source='gross_monthly_nominal', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = SalaryStructure
        fields = '__all__'

class PayrollComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollComponent
        fields = '__all__'

class PayrollRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.first_name', read_only=True)
    employee_code = serializers.CharField(source='employee.employee_code', read_only=True)

    class Meta:
        model = PayrollRecord
        fields = '__all__'

class PayrollBatchSerializer(serializers.ModelSerializer):
    records = PayrollRecordSerializer(many=True, read_only=True)

    class Meta:
        model = PayrollBatch
        fields = '__all__'

class FinalSettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalSettlement
        fields = '__all__'
        read_only_fields = ['leave_encashment_amount', 'notice_penalty_amount', 'net_settlement_amount']