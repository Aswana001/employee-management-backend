from django.urls import path
from .views import ExecutiveDashboardAPIView, EmployeeReportAPIView

urlpatterns = [
    path('dashboard/', ExecutiveDashboardAPIView.as_view(), name='dashboard-metrics'),
    path('employee-report/', EmployeeReportAPIView.as_view(), name='report-employee'),
]