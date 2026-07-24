from django.urls import path
from . import views

urlpatterns = [
    # Salary Structure Setup
    path('structures/', views.SalaryStructureListCreateAPIView.as_view(), name='salary-structures'),
    path('structures/<int:employee_id>/', views.SalaryStructureDetailAPIView.as_view(), name='salary-structure-detail'),

    # One-off Components (Bonuses/Incentives)
    path('components/', views.PayrollComponentListCreateAPIView.as_view(), name='payroll-components'),

    # Batch Engine
    path('generate/', views.GeneratePayrollAPIView.as_view(), name='payroll-generate'),
    path('batches/<int:pk>/lock/', views.LockPayrollBatchAPIView.as_view(), name='payroll-lock'),

    # Employee Payslips & Reports
    path('payslip/<int:employee_id>/<int:month>/<int:year>/', views.EmployeePayslipAPIView.as_view(), name='employee-payslip'),
    path('reports/summary/', views.PayrollSummaryReportAPIView.as_view(), name='payroll-summary-report'),

    # Full & Final Settlement
    path('settlement/', views.FinalSettlementAPIView.as_view(), name='final-settlement'),
]