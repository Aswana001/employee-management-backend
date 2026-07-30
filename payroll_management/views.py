from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from decimal import Decimal

from .models import SalaryStructure, PayrollBatch, PayrollComponent, PayrollRecord, FinalSettlement
from .serializers import (
    SalaryStructureSerializer, PayrollComponentSerializer, 
    PayrollBatchSerializer, PayrollRecordSerializer, FinalSettlementSerializer
)
from .services import compute_employee_payslip
from .permissions import IsHRUser
from employee.models import Employee

class StandardResponseMixin:
    def finalize_response(self, request, response, *args, **kwargs):
        if 200 <= response.status_code < 300:
            response.data = {"success": True, "message": "Operation successful.", "data": response.data}
        elif response.status_code >= 400:
            response.data = {"success": False, "message": "Operation failed.", "errors": response.data}
        return super().finalize_response(request, response, *args, **kwargs)

# --- Salary Structures ---
class SalaryStructureListCreateAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = SalaryStructure.objects.all()
    serializer_class = SalaryStructureSerializer
    # permission_classes = [IsHRUser]  # Keep commented while testing locally

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get('employee')
        
        # Check if structure already exists for this employee
        structure = SalaryStructure.objects.filter(employee_id=employee_id).first()
        
        if structure:
            # Update existing structure instead of throwing a 500 error
            serializer = self.get_serializer(structure, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        return super().create(request, *args, **kwargs)

class SalaryStructureDetailAPIView(StandardResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = SalaryStructure.objects.all()
    serializer_class = SalaryStructureSerializer
    lookup_field = 'employee_id'

# --- One-off Additions (Bonuses/Incentives) ---
class PayrollComponentListCreateAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = PayrollComponent.objects.all()
    serializer_class = PayrollComponentSerializer
    permission_classes = [IsHRUser]

# --- Batch Processing Engine ---
class GeneratePayrollAPIView(StandardResponseMixin, APIView):
    permission_classes = [IsHRUser]

    def post(self, request):
        month = int(request.data.get('month', timezone.now().month))
        year = int(request.data.get('year', timezone.now().year))

        batch, created = PayrollBatch.objects.get_or_create(
            month=month,
            year=year,
            defaults={'status': 'PROCESSED'}
        )

        active_employees = Employee.objects.filter(is_active=True)
        count = 0

        for emp in active_employees:
            # Generate payslip for each employee
            record = compute_employee_payslip(emp, month, year, batch)
            if record:
                count += 1

        return Response({
            "batch_id": batch.id,
            "month": month,
            "year": year,
            "total_payslips_generated": count,
            "status": batch.status
        }, status=status.HTTP_201_CREATED)

class LockPayrollBatchAPIView(StandardResponseMixin, APIView):
    permission_classes = [IsHRUser]

    def post(self, request, pk):
        try:
            batch = PayrollBatch.objects.get(pk=pk)
        except PayrollBatch.DoesNotExist:
            return Response({"error": "Payroll batch not found."}, status=status.HTTP_404_NOT_FOUND)

        batch.status = 'PAID'
        batch.save()
        return Response({"message": f"Payroll Batch {batch.month}/{batch.year} has been locked and marked as PAID."})

# --- Payslips & Reports ---
class EmployeePayslipAPIView(StandardResponseMixin, APIView):
    def get(self, request, employee_id, month, year):
        try:
            record = PayrollRecord.objects.get(employee_id=employee_id, batch__month=month, batch__year=year)
            return Response(PayrollRecordSerializer(record).data)
        except PayrollRecord.DoesNotExist:
            return Response({"error": "Payslip record not found for given month/year."}, status=status.HTTP_404_NOT_FOUND)

class PayrollSummaryReportAPIView(StandardResponseMixin, APIView):
    permission_classes = [IsHRUser]

    def get(self, request):
        month = request.query_params.get('month', timezone.now().month)
        year = request.query_params.get('year', timezone.now().year)

        records = PayrollRecord.objects.filter(batch__month=month, batch__year=year)

        total_gross = sum(r.gross_earnings for r in records)
        total_pf = sum(r.pf_amount for r in records)
        total_esi = sum(r.esi_amount for r in records)
        total_tds = sum(r.tds_amount for r in records)
        total_net_payout = sum(r.net_salary for r in records)

        return Response({
            "month": int(month),
            "year": int(year),
            "total_employees_paid": records.count(),
            "financial_summary": {
                "total_gross_disbursed": float(total_gross),
                "total_pf_collected": float(total_pf),
                "total_esi_collected": float(total_esi),
                "total_tds_collected": float(total_tds),
                "total_net_bank_transfer": float(total_net_payout)
            }
        })

# --- Full & Final (F&F) Settlement ---
class FinalSettlementAPIView(StandardResponseMixin, generics.CreateAPIView):
    serializer_class = FinalSettlementSerializer
    permission_classes = [IsHRUser]

    def perform_create(self, serializer):
        emp = serializer.validated_data['employee']
        encash_days = serializer.validated_data.get('encashable_leave_days', Decimal('0.0'))
        shortfall_days = serializer.validated_data.get('notice_period_shortfall_days', Decimal('0.0'))
        dues = serializer.validated_data.get('other_pending_dues', Decimal('0.00'))
        damage = serializer.validated_data.get('asset_damage_deductions', Decimal('0.00'))

        # Get Daily Rate
        daily_rate = Decimal('0.00')
        if hasattr(emp, 'salary_structure'):
            daily_rate = emp.salary_structure.gross_monthly_nominal / Decimal('30.0')

        encash_amount = round(daily_rate * encash_days, 2)
        penalty_amount = round(daily_rate * shortfall_days, 2)

        net_settlement = encash_amount - penalty_amount + dues - damage

        serializer.save(
            leave_encashment_amount=encash_amount,
            notice_penalty_amount=penalty_amount,
            net_settlement_amount=net_settlement,
            status='APPROVED'
        )