from django.urls import path
from . import views

urlpatterns = [
    # Core Shift Setup Rules
    path('shifts/', views.ShiftListCreateAPIView.as_view(), name='shift-list-create'),
    path('shifts/<int:pk>/', views.ShiftRetrieveUpdateDestroyAPIView.as_view(), name='shift-detail'),
    
    # Assignments Pipeline
    path('assignments/', views.AssignmentListCreateAPIView.as_view(), name='assign-list-create'),
    path('assignments/<int:pk>/', views.AssignmentRetrieveUpdateDestroyAPIView.as_view(), name='assign-detail'),
    path('assignments/active/<int:employee_id>/', views.ActiveAssignmentAPIView.as_view(), name='assign-active'),
    
    # Grid Weekly Calendars
    path('schedules/weekly/', views.WeeklyScheduleCreateAPIView.as_view(), name='weekly-create'),
    path('schedules/weekly/<int:employee_id>/', views.WeeklyScheduleDetailAPIView.as_view(), name='weekly-detail'),
    
    # Alternating Rotations Layer
    path('rotations/', views.RotatingShiftListCreateAPIView.as_view(), name='rotations-list-create'),
    
    # Trade Negotiation Marketplace Engine Actions
    path('swaps/request/', views.ShiftSwapRequestAPIView.as_view(), name='swap-request'),
    path('swaps/<int:pk>/<str:action>/', views.ShiftSwapWorkflowAPIView.as_view(), name='swap-workflow'),
    
    # Statutory Holidays Metrics Processing Nodes
    path('holidays/', views.HolidayShiftListCreateAPIView.as_view(), name='holidays-list-create'),
    
    # Calculators Telemetry Feeds
    path('overtime/rules/', views.OvertimeRuleListCreateAPIView.as_view(), name='ot-rules'),
    path('overtime/calculate/<int:employee_id>/', views.CalculateOvertimeAPIView.as_view(), name='ot-calculate'),
]