from django.urls import path
from employee import views

urlpatterns = [
    # Departments
    path('departments/', views.DepartmentListCreateAPIView.as_view(), name='department-list'),
    path('departments/<int:pk>/', views.DepartmentRetrieveUpdateDestroyAPIView.as_view(), name='department-detail'), # Fixed syntax here!
    
    # Designations
    path('designations/', views.DesignationListCreateAPIView.as_view(), name='designation-list'),
    path('designations/<int:pk>/', views.DesignationRetrieveUpdateDestroyAPIView.as_view(), name='designation-detail'),
    
    # Employees
    path('employees/', views.EmployeeListCreateAPIView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', views.EmployeeRetrieveUpdateDestroyAPIView.as_view(), name='employee-detail'),
    
    # Documents
    path('documents/', views.EmployeeDocumentListCreateAPIView.as_view(), name='document-list'),
    path('documents/<int:pk>/', views.EmployeeDocumentRetrieveUpdateDestroyAPIView.as_view(), name='document-detail'),
    
    # Workflows
    path('promotions/', views.PromotionListCreateAPIView.as_view(), name='promotion-list'),
    path('transfers/', views.TransferListCreateAPIView.as_view(), name='transfer-list'),
    path('terminations/', views.TerminationListCreateAPIView.as_view(), name='termination-list'),
    
    # Resignations
    path('resignations/', views.ResignationListCreateAPIView.as_view(), name='resignation-list'),
    path('resignations/<int:pk>/approve/', views.ResignationApproveAPIView.as_view(), name='resignation-approve'),
    path('resignations/<int:pk>/reject/', views.ResignationRejectAPIView.as_view(), name='resignation-reject'),
    
    # History
    path('history/', views.EmployeeHistoryListAPIView.as_view(), name='employee-history'),
]