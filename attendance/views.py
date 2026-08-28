from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Attendance, AttendanceRegularization
from .serializers import (
    CheckInSerializer, CheckOutSerializer, AttendanceSerializer, 
    AttendanceRegularizationSerializer
)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone

from .models import Attendance
from employee.models import Employee


class CheckInAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # 1. Safely extract employee ID from request body
        employee_id = request.data.get('employee') or request.data.get('employee_id')

        if not employee_id:
            return Response(
                {"error": "Field 'employee' or 'employee_id' is required in JSON payload."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Safely verify employee exists in Database
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {"error": f"Employee with ID {employee_id} does not exist in database."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        today = timezone.now().date()
        now = timezone.now()

        # 3. Get or Create attendance record cleanly
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'check_in': now,
                'is_valid_geofence': request.data.get('is_valid_geofence', True)
            }
        )

        if not created and attendance.check_in:
            return Response(
                {"message": "Employee already checked in today.", "check_in": attendance.check_in},
                status=status.HTTP_200_OK
            )

        attendance.check_in = now
        attendance.save()

        return Response({
            "id": attendance.id,
            "employee": employee.id,
            "date": str(attendance.date),
            "check_in": attendance.check_in.isoformat(),
            "status": getattr(attendance, 'status', 'PRESENT')
        }, status=status.HTTP_201_CREATED)


class CheckOutAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CheckOutSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AttendanceHistoryAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'date']

    def get_queryset(self):
        return Attendance.objects.all()


class MonthlySummaryAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, employee_id):
        current_month = timezone.now().month
        records = Attendance.objects.filter(employee_id=employee_id, date__month=current_month)
        
        # Use Count with filter for boolean fields to ensure DB compatibility across SQLite/PostgreSQL
        summary = records.aggregate(
            total_days=Count('id'),
            late_days=Count('id', filter=Q(is_late=True)),
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
    permission_classes = [AllowAny]
    queryset = AttendanceRegularization.objects.all()
    serializer_class = AttendanceRegularizationSerializer


class RegularizationApproveAPIView(APIView):
    permission_classes = [AllowAny]

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
        # Fallback string for when request.user is AnonymousUser
        user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
        req.approved_by_username = user.username if user else "HR_Admin"
        req.save()
        
        return Response({"message": "Regularization workflow processed successfully."}, status=status.HTTP_200_OK)