from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Attendance, AttendanceRegularization
from .serializers import (
    CheckInSerializer, CheckOutSerializer, AttendanceSerializer, 
    AttendanceRegularizationSerializer
)

class CheckInAPIView(generics.CreateAPIView):
    serializer_class = CheckInSerializer

class CheckOutAPIView(generics.CreateAPIView):
    serializer_class = CheckOutSerializer

class AttendanceHistoryAPIView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'date']

    def get_queryset(self):
        return Attendance.objects.all()

class MonthlySummaryAPIView(APIView):
    def get(self, request, employee_id):
        current_month = timezone.now().month
        records = Attendance.objects.filter(employee_id=employee_id, date__month=current_month)
        
        summary = records.aggregate(
            total_days=Count('id'),
            late_days=Sum('is_late', filter=Q(is_late=True)),
            total_ot=Sum('overtime_hours'),
            geofence_breaches=Count('id', filter=Q(is_valid_geofence=False))
        )
        
        return Response({
            "employee_id": employee_id,
            "month": current_month,
            "metrics": {
                "total_present_days": summary['total_days'] or 0,
                "late_arrivals_count": summary['late_days'] or 0,
                "accumulated_overtime_hours": float(summary['total_ot'] or 0.00),
                "geofence_breaches": summary['geofence_breaches'] or 0
            }
        }, status=status.HTTP_200_OK)

class RegularizationRequestAPIView(generics.ListCreateAPIView):
    queryset = AttendanceRegularization.objects.all()
    serializer_class = AttendanceRegularizationSerializer

class RegularizationApproveAPIView(APIView):
    def post(self, request, pk):
        try:
            req = AttendanceRegularization.objects.get(pk=pk)
        except AttendanceRegularization.DoesNotExist:
            return Response({"error": "Workflow record missing."}, status=status.HTTP_404_NOT_FOUND)
            
        if req.status != 'Pending':
            return Response({"error": "Workflow already processed."}, status=status.HTTP_400_BAD_REQUEST)
            
        attendance = req.attendance
        if req.corrected_check_in:
            attendance.check_in = req.corrected_check_in
            attendance.is_late = False
        if req.corrected_check_out:
            attendance.check_out = req.corrected_check_out
            
        attendance.save()
        
        req.status = 'Approved'
        req.approved_by_username = request.user.username if request.user.is_authenticated else "HR_Admin"
        req.save()
        
        return Response({"message": "Regularization workflow processed successfully."}, status=status.HTTP_200_OK)