from django.urls import path
from . import views

urlpatterns = [
    path('check-in/', views.CheckInAPIView.as_view(), name='attendance-check-in'),
    path('check-out/', views.CheckOutAPIView.as_view(), name='attendance-check-out'),
    path('history/', views.AttendanceHistoryAPIView.as_view(), name='attendance-history'),
    path('summary/<int:employee_id>/', views.MonthlySummaryAPIView.as_view(), name='attendance-monthly-summary'),
    path('regularize/', views.RegularizationRequestAPIView.as_view(), name='regularize-list-create'),
    path('regularize/<int:pk>/approve/', views.RegularizationApproveAPIView.as_view(), name='regularize-approve'),
]