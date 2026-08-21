from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobOpeningViewSet, CandidateViewSet, InterviewViewSet,
    OfferViewSet, OnboardingChecklistViewSet
)

router = DefaultRouter()
router.register('jobs', JobOpeningViewSet)
router.register('candidates', CandidateViewSet)
router.register('interviews', InterviewViewSet)
router.register('offers', OfferViewSet)
router.register('onboarding', OnboardingChecklistViewSet)

urlpatterns = [
    path('', include(router.urls)),
]