from rest_framework import serializers
from .models import ExpenseCategory, ExpenseClaim

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'


class ExpenseClaimSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = ExpenseClaim
        fields = [
            'id', 'employee', 'category', 'category_name', 'amount',
            'expense_date', 'description', 'receipt', 'status',
            'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'rejection_reason', 'created_at', 'updated_at']