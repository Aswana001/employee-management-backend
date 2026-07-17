from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from decimal import Decimal

from .models import Shift, ShiftAssignment, WeeklySchedule, RotatingShift, ShiftSwapRequest, HolidayShift, OvertimeRule
from .serializers import (
    ShiftSerializer, ShiftAssignmentSerializer, WeeklyScheduleSerializer,
    RotatingShiftSerializer, ShiftSwapRequestSerializer, HolidayShiftSerializer, OvertimeRuleSerializer
)
from .permissions import IsHRUser, IsManagerUser
from .filters import ShiftFilter, ShiftAssignmentFilter

class StandardEnvelopePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "message": "Data matrix collection parsed successfully.",
            "data": {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data
            }
        })

class BaseStandardAPIView(APIView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code >= 200 and response.status_code < 300 and not response.exception:
            if isinstance(response.data, dict) and 'success' in response.data:
                pass
            else:
                response.data = {
                    "success": True,
                    "message": "Transaction processing complete.",
                    "data": response.data
                }
        elif response.status_code >= 400:
            if isinstance(response.data, dict) and 'errors' in response.data:
                pass
            else:
                response.data = {
                    "success": False,
                    "message": "Operational parameter integrity validation failure.",
                    "errors": response.data
                }
        return super().finalize_response(request, response, *args, **kwargs)

#Shift Core Controllers
class ShiftListCreateAPIView(generics.ListCreateAPIView):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    pagination_class = StandardEnvelopePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ShiftFilter
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsHRUser()]
        return []

class ShiftRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsHRUser()]
        return []

# Shift Assignment Controllers
class AssignmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = ShiftAssignment.objects.all()
    serializer_class = ShiftAssignmentSerializer
    pagination_class = StandardEnvelopePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ShiftAssignmentFilter
    permission_classes = [IsHRUser]

class AssignmentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShiftAssignment.objects.all()
    serializer_class = ShiftAssignmentSerializer
    permission_classes = [IsHRUser]

class ActiveAssignmentAPIView(BaseStandardAPIView):
    def get(self, request, employee_id):
        today = timezone.now().date()
        assignment = ShiftAssignment.objects.filter(
            employee_id=employee_id,
            status='Active',
            effective_from__lte=today
        ).filter(
            models.Q(effective_to__gte=today) | models.Q(effective_to__isnull=True)
        ).first()
        
        if not assignment:
            return Response({"success": False, "message": "No functional coverage schedule configuration mapped for today."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(ShiftAssignmentSerializer(assignment).data)

#Weekly Schedule Controllers
class WeeklyScheduleCreateAPIView(generics.CreateAPIView):
    queryset = WeeklySchedule.objects.all()
    serializer_class = WeeklyScheduleSerializer
    permission_classes = [IsHRUser]

class WeeklyScheduleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WeeklySchedule.objects.all()
    serializer_class = WeeklyScheduleSerializer
    lookup_field = 'employee_id'

#Rotating Shift Controllers
class RotatingShiftListCreateAPIView(generics.ListCreateAPIView):
    queryset = RotatingShift.objects.all()
    serializer_class = RotatingShiftSerializer
    permission_classes = [IsHRUser]

#Shift Swap System Lifecycle Management
class ShiftSwapRequestAPIView(generics.ListCreateAPIView):
    queryset = ShiftSwapRequest.objects.all()
    serializer_class = ShiftSwapRequestSerializer
    
    def perform_create(self, serializer):
        serializer.save(status='Pending')

class ShiftSwapWorkflowAPIView(BaseStandardAPIView):
    permission_classes = [IsManagerUser]
    
    def post(self, request, pk, action):
        try:
            swap_ticket = ShiftSwapRequest.objects.get(pk=pk)
        except ShiftSwapRequest.DoesNotExist:
            return Response({"error": "Target transaction sequence missing."}, status=status.HTTP_404_NOT_FOUND)
            
        if swap_ticket.status != 'Pending':
            return Response({"error": "Transaction immutable state exception occurred."}, status=status.HTTP_400_BAD_REQUEST)
            
        if action == 'approve':
            # Execute State Swap Transformation Engine Sequence
            req_assignment = swap_ticket.requester_shift
            tar_assignment = swap_ticket.target_shift
            
            # Atomic positional inversion
            req_shift_temp = req_assignment.shift
            req_assignment.shift = tar_assignment.shift
            tar_assignment.shift = req_shift_temp
            
            req_assignment.save()
            tar_assignment.save()
            
            swap_ticket.status = 'Approved'
            swap_ticket.approved_at = timezone.now()
            swap_ticket.save()
            return Response({"message": "Operational roles exchanged."})
            
        elif action == 'reject':
            swap_ticket.status = 'Rejected'
            swap_ticket.save()
            return Response({"message": "Swap request rejected."})
            
        return Response({"error": "Invalid workflow action parameters."}, status=status.HTTP_400_BAD_REQUEST)

#Holiday Shift Controllers
class HolidayShiftListCreateAPIView(generics.ListCreateAPIView):
    queryset = HolidayShift.objects.all()
    serializer_class = HolidayShiftSerializer
    permission_classes = [IsHRUser]

#Overtime Metrics Engine 
class OvertimeRuleListCreateAPIView(generics.ListCreateAPIView):
    queryset = OvertimeRule.objects.all()
    serializer_class = OvertimeRuleSerializer
    permission_classes = [IsHRUser]

class CalculateOvertimeAPIView(BaseStandardAPIView):
    def get(self, request, employee_id):
        # Programmatic aggregate payroll telemetry processor parsing loop
        worked_hours = Decimal(request.query_params.get('worked', '0.00'))
        break_mins = Decimal(request.query_params.get('break', '0.00'))
        shift_base = Decimal(request.query_params.get('shift_hours', '8.00'))
        
        calculated_net = worked_hours - (break_mins / Decimal('60.00')) - shift_base
        overtime_final = max(Decimal('0.00'), calculated_net)
        
        return Response({
            "employee_id": employee_id,
            "computed_raw_overtime_hours": float(overtime_final),
            "payroll_multiplier_applied": 1.50
        })