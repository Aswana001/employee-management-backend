from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Sum
from .models import ExpenseCategory, ExpenseClaim
from .serializers import ExpenseCategorySerializer, ExpenseClaimSerializer


class ExpenseCategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [AllowAny]


class ExpenseClaimListCreateAPIView(generics.ListCreateAPIView):
    queryset = ExpenseClaim.objects.all()
    serializer_class = ExpenseClaimSerializer
    permission_classes = [AllowAny]


class ApproveManagerAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            claim = ExpenseClaim.objects.get(pk=pk)
            claim.status = 'APPROVED_MANAGER'
            claim.save()
            return Response(
                {"message": "Expense claim approved by manager.", "status": claim.status},
                status=status.HTTP_200_OK
            )
        except ExpenseClaim.DoesNotExist:
            return Response({"error": "Expense claim not found."}, status=status.HTTP_404_NOT_FOUND)


class ApproveFinanceAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            claim = ExpenseClaim.objects.get(pk=pk)
            claim.status = 'REIMBURSED'
            claim.save()
            return Response(
                {"message": "Expense claim reimbursed by finance.", "status": claim.status},
                status=status.HTTP_200_OK
            )
        except ExpenseClaim.DoesNotExist:
            return Response({"error": "Expense claim not found."}, status=status.HTTP_404_NOT_FOUND)


class RejectExpenseAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        reason = request.data.get('reason', 'No reason provided.')
        try:
            claim = ExpenseClaim.objects.get(pk=pk)
            claim.status = 'REJECTED'
            claim.rejection_reason = reason
            claim.save()
            return Response(
                {"message": "Expense claim rejected.", "status": claim.status, "reason": reason},
                status=status.HTTP_200_OK
            )
        except ExpenseClaim.DoesNotExist:
            return Response({"error": "Expense claim not found."}, status=status.HTTP_404_NOT_FOUND)


class ExpenseReportSummaryAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        total_requested = ExpenseClaim.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        total_reimbursed = ExpenseClaim.objects.filter(status='REIMBURSED').aggregate(Sum('amount'))['amount__sum'] or 0
        pending_count = ExpenseClaim.objects.filter(status__in=['PENDING_MANAGER', 'APPROVED_MANAGER']).count()

        return Response({
            "total_requested_amount": total_requested,
            "total_reimbursed_amount": total_reimbursed,
            "pending_claims_count": pending_count,
            "total_claims_count": ExpenseClaim.objects.count()
        }, status=status.HTTP_200_OK)