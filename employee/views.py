from django.shortcuts import render
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status

from employee.models import (
    Department, Designation, Employee, EmployeeDocument, 
    Promotion, Transfer, Resignation, Termination, EmployeeHistory
)
from employee.serializers import (
    DepartmentSerializer, DesignationSerializer, EmployeeSerializer,
    EmployeeDocumentSerializer, PromotionSerializer, TransferSerializer,
    ResignationSerializer, TerminationSerializer, EmployeeHistorySerializer
)
from employee.filters import EmployeeFilter

# 1. DEPARTMENT ENDPOINTS

class DepartmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class DepartmentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

# 2. DESIGNATION ENDPOINTS

class DesignationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer

class DesignationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer

# 3. EMPLOYEE ENDPOINTS (Optimized & Filterable)

class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    """
    List and Create endpoint for Employees.
    Uses select_related to solve the N+1 query problem for foreign keys.
    """
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = ['first_name', 'last_name', 'email', 'employee_code']
    ordering_fields = ['first_name', 'salary', 'joining_date', 'created_at']

    def get_queryset(self):
        return Employee.objects.select_related('department', 'designation', 'reporting_manager').all()

class EmployeeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Read, Update, and Soft-Delete individual employee records.
    """
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        return Employee.objects.select_related('department', 'designation', 'reporting_manager').all()

    def perform_destroy(self, instance):
        # Trigger our custom model-level soft-delete engine instead of purging from disk
        instance.delete()


# 4. DOCUMENT MANAGEMENT ENDPOINTS#
class EmployeeDocumentListCreateAPIView(generics.ListCreateAPIView):
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer

class EmployeeDocumentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer


# 5. WORKFLOW ENDPOINTS (Promotions, Transfers)

class PromotionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer

class TransferListCreateAPIView(generics.ListCreateAPIView):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer

# 6. RESIGNATION WORKFLOW ENDPOINTS

class ResignationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Resignation.objects.all()
    serializer_class = ResignationSerializer

class ResignationApproveAPIView(generics.GenericAPIView):
    queryset = Resignation.objects.all()
    serializer_class = ResignationSerializer

    def post(self, request, *args, **kwargs):
        resignation = self.get_object()
        resignation.status = 'Approved'
        resignation.save()
        
        # Log into history
        EmployeeHistory.objects.create(
            employee=resignation.employee,
            action="RESIGNATION_APPROVED",
            old_data={"status": "Pending"},
            new_data={"status": "Approved"}
        )
        return Response({"message": "Resignation approved successfully."}, status=status.HTTP_200_OK)

class ResignationRejectAPIView(generics.GenericAPIView):
    queryset = Resignation.objects.all()
    serializer_class = ResignationSerializer

    def post(self, request, *args, **kwargs):
        resignation = self.get_object()
        resignation.status = 'Rejected'
        resignation.save()
        return Response({"message": "Resignation rejected successfully."}, status=status.HTTP_200_OK)


# 7. TERMINATION ENDPOINTS

class TerminationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Termination.objects.all()
    serializer_class = TerminationSerializer


# 8. AUDIT HISTORY LISTING ENDPOINT

class EmployeeHistoryListAPIView(generics.ListAPIView):
    serializer_class = EmployeeHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee']

    def get_queryset(self):
        return EmployeeHistory.objects.all().order_by('-timestamp')

