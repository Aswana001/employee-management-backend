from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from decimal import Decimal

from .models import LeaveType, LeaveBalance, LeaveRequest, CompOffClaim, LeaveEncashment
from .serializers import (
    LeaveTypeSerializer, LeaveBalanceSerializer, LeaveRequestSerializer,
    CompOffClaimSerializer, LeaveEncashmentSerializer
)
from .services import update_balance_for_request
from .permissions import IsHRUser, IsManagerOrHR

class StandardResponseMixin:
    def finalize_response(self, request, response, *args, **kwargs):
        if 200 <= response.status_code < 300:
            response.data = {"success": True, "message": "Operation successful.", "data": response.data}
        elif response.status_code >= 400:
            response.data = {"success": False, "message": "Operation failed.", "errors": response.data}
        return super().finalize_response(request, response, *args, **kwargs)

# --- Leave Types & Balances ---
class LeaveTypeListCreateAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer

class LeaveBalanceListAPIView(StandardResponseMixin, generics.ListAPIView):
    serializer_class = LeaveBalanceSerializer

    def get_queryset(self):
        emp_id = self.kwargs.get('employee_id')
        return LeaveBalance.objects.filter(employee_id=emp_id)

# --- Leave Request Lifecycle ---
class ApplyLeaveAPIView(StandardResponseMixin, generics.CreateAPIView):
    serializer_class = LeaveRequestSerializer

    def perform_create(self, serializer):
        instance = serializer.save(status='PENDING_L1')
        update_balance_for_request(instance, 'SUBMIT')

class ApproveLeaveAPIView(StandardResponseMixin, APIView):
    permission_classes = [IsManagerOrHR]

    def post(self, request, pk):
        try:
            leave_req = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found."}, status=status.HTTP_404_NOT_FOUND)

        if leave_req.status == 'PENDING_L1':
            leave_req.status = 'PENDING_L2'
            leave_req.level1_approved_at = timezone.now()
            leave_req.save()
            return Response({"message": "Level 1 Approval complete. Moved to Level 2 HR review."})

        elif leave_req.status == 'PENDING_L2':
            leave_req.status = 'APPROVED'
            leave_req.level2_approved_at = timezone.now()
            leave_req.save()
            update_balance_for_request(leave_req, 'APPROVE')
            return Response({"message": "Final Level 2 Approval complete. Leave balance deducted."})

        return Response({"error": f"Cannot approve request with status '{leave_req.status}'."}, status=status.HTTP_400_BAD_REQUEST)

class RejectLeaveAPIView(StandardResponseMixin, APIView):
    permission_classes = [IsManagerOrHR]

    def post(self, request, pk):
        reason = request.data.get('rejection_reason', 'No reason provided')
        try:
            leave_req = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found."}, status=status.HTTP_404_NOT_FOUND)

        if leave_req.status in ['APPROVED', 'CANCELLED', 'REJECTED']:
            return Response({"error": "Cannot reject a closed request."}, status=status.HTTP_400_BAD_REQUEST)

        leave_req.status = 'REJECTED'
        leave_req.rejection_reason = reason
        leave_req.save()
        update_balance_for_request(leave_req, 'REJECT')
        return Response({"message": "Leave request rejected."})

class CancelLeaveAPIView(StandardResponseMixin, APIView):
    def post(self, request, pk):
        try:
            leave_req = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found."}, status=status.HTTP_404_NOT_FOUND)

        if leave_req.status in ['PENDING_L1', 'PENDING_L2']:
            leave_req.status = 'CANCELLED'
            leave_req.save()
            update_balance_for_request(leave_req, 'REJECT')  # Free pending balance
            return Response({"message": "Leave request cancelled."})

        elif leave_req.status == 'APPROVED':
            # Refunds deducted leave balance upon cancellation approval
            leave_req.status = 'CANCELLED'
            leave_req.save()
            update_balance_for_request(leave_req, 'CANCEL')  # Refund used balance
            return Response({"message": "Approved leave cancelled and balance refunded."})

        return Response({"error": "Cannot cancel this request."}, status=status.HTTP_400_BAD_REQUEST)

# --- Comp-Off Workflow ---
class CompOffClaimAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = CompOffClaim.objects.all()
    serializer_class = CompOffClaimSerializer

class ApproveCompOffAPIView(StandardResponseMixin, APIView):
    permission_classes = [IsHRUser]

    def post(self, request, pk):
        try:
            claim = CompOffClaim.objects.get(pk=pk)
        except CompOffClaim.DoesNotExist:
            return Response({"error": "Claim not found."}, status=status.HTTP_404_NOT_FOUND)

        if claim.status != 'PENDING':
            return Response({"error": "Claim already processed."}, status=status.HTTP_400_BAD_REQUEST)

        claim.status = 'APPROVED'
        claim.save()

        # Add +1 day credit to the Comp-Off Leave Balance
        comp_type, _ = LeaveType.objects.get_or_create(code='COMP', defaults={'name': 'Comp-Off'})
        balance, _ = LeaveBalance.objects.get_or_create(
            employee=claim.employee,
            leave_type=comp_type,
            year=claim.worked_date.year
        )
        balance.allocated += Decimal('1.0')
        balance.save()

        return Response({"message": "Comp-off approved and +1.0 day credited to employee balance."})

# --- Leave Encashment Workflow ---
class LeaveEncashmentAPIView(StandardResponseMixin, generics.ListCreateAPIView):
    queryset = LeaveEncashment.objects.all()
    serializer_class = LeaveEncashmentSerializer