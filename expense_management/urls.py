from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.ExpenseCategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('claims/', views.ExpenseClaimListCreateAPIView.as_view(), name='claim-list-create'),
    path('claims/<int:pk>/approve-manager/', views.ApproveManagerAPIView.as_view(), name='claim-approve-manager'),
    path('claims/<int:pk>/approve-finance/', views.ApproveFinanceAPIView.as_view(), name='claim-approve-finance'),
    path('claims/<int:pk>/reject/', views.RejectExpenseAPIView.as_view(), name='claim-reject'),
    path('reports/summary/', views.ExpenseReportSummaryAPIView.as_view(), name='expense-report-summary'),
]