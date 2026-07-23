from django.urls import path
from . import views

urlpatterns = [
    # Types & Balances
    path('types/', views.LeaveTypeListCreateAPIView.as_view(), name='leave-types'),
    path('balance/<int:employee_id>/', views.LeaveBalanceListAPIView.as_view(), name='leave-balance'),

    # Request Workflow Engine
    path('apply/', views.ApplyLeaveAPIView.as_view(), name='leave-apply'),
    path('<int:pk>/approve/', views.ApproveLeaveAPIView.as_view(), name='leave-approve'),
    path('<int:pk>/reject/', views.RejectLeaveAPIView.as_view(), name='leave-reject'),
    path('<int:pk>/cancel/', views.CancelLeaveAPIView.as_view(), name='leave-cancel'),

    # Comp-Off & Encashment
    path('comp-off/claim/', views.CompOffClaimAPIView.as_view(), name='comp-off-claim'),
    path('comp-off/<int:pk>/approve/', views.ApproveCompOffAPIView.as_view(), name='comp-off-approve'),
    path('encash/', views.LeaveEncashmentAPIView.as_view(), name='leave-encash'),
]