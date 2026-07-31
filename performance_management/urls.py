from django.urls import path
from . import views

urlpatterns = [
    path('cycles/', views.AppraisalCycleListCreateAPIView.as_view(), name='appraisal-cycle-list-create'),
    path('goals/', views.GoalListCreateAPIView.as_view(), name='goal-list-create'),
    path('appraisals/', views.AppraisalListCreateAPIView.as_view(), name='appraisal-list-create'),
    path('appraisals/<int:pk>/self-review/', views.SelfReviewAPIView.as_view(), name='appraisal-self-review'),
    path('appraisals/<int:pk>/manager-review/', views.ManagerReviewAPIView.as_view(), name='appraisal-manager-review'),
    path('appraisals/<int:pk>/calibrate/', views.CalibrateAppraisalAPIView.as_view(), name='appraisal-calibrate'),
]