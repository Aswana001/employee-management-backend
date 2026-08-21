from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import JobOpening, Candidate, Interview, Offer, OnboardingChecklist
from .serializers import (
    JobOpeningSerializer, CandidateSerializer, InterviewSerializer,
    OfferSerializer, OnboardingChecklistSerializer, StageUpdateSerializer
)


class JobOpeningViewSet(viewsets.ModelViewSet):
    queryset = JobOpening.objects.all()
    serializer_class = JobOpeningSerializer
    permission_classes = [IsAuthenticated]


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]

    # Move candidate along pipeline stage
    @action(detail=True, methods=['patch'], url_path='update-stage')
    def update_stage(self, request, pk=None):
        candidate = self.get_object()
        serializer = StageUpdateSerializer(data=request.data)
        if serializer.is_valid():
            candidate.stage = serializer.validated_data['stage']
            candidate.save()
            return Response({'status': f'Candidate moved to {candidate.stage}'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Pre-populate basic onboarding checklist upon hiring
    @action(detail=True, methods=['post'], url_path='initialize-onboarding')
    def initialize_onboarding(self, request, pk=None):
        candidate = self.get_object()
        if candidate.stage != 'HIRED':
            return Response(
                {'error': 'Can only initialize onboarding for HIRED candidates'},
                status=status.HTTP_400_BAD_REQUEST
            )

        default_tasks = [
            "Submit Identity & Academic Documents",
            "IT Equipment Setup & Credentials Provisioning",
            "Complete HR Policy Orientation",
            "Team Introduction & Mentorship Alignment"
        ]

        created_tasks = []
        for task_title in default_tasks:
            task = OnboardingChecklist.objects.create(
                candidate=candidate,
                title=task_title,
                status='PENDING',
                due_date=request.data.get('joining_date')
            )
            created_tasks.append(task.id)

        return Response({
            'message': f'Initialized {len(created_tasks)} default onboarding tasks',
            'task_ids': created_tasks
        })


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]


class OnboardingChecklistViewSet(viewsets.ModelViewSet):
    queryset = OnboardingChecklist.objects.all()
    serializer_class = OnboardingChecklistSerializer
    permission_classes = [IsAuthenticated]