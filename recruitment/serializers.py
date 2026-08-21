from decimal import Decimal
from rest_framework import serializers
from .models import JobOpening, Candidate, Interview, Offer, OnboardingChecklist


class JobOpeningSerializer(serializers.ModelSerializer):
    candidate_count = serializers.IntegerField(source='candidates.count', read_only=True)

    class Meta:
        model = JobOpening
        fields = '__all__'


class InterviewSerializer(serializers.ModelSerializer):
    interviewer_name = serializers.ReadOnlyField(source='interviewer.get_full_name')

    class Meta:
        model = Interview
        fields = '__all__'


class OfferSerializer(serializers.ModelSerializer):
    candidate_name = serializers.ReadOnlyField(source='candidate.first_name')
    offered_salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.00')
    )

    class Meta:
        model = Offer
        fields = '__all__'


class OnboardingChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingChecklist
        fields = '__all__'


class CandidateSerializer(serializers.ModelSerializer):
    interviews = InterviewSerializer(many=True, read_only=True)
    offer = OfferSerializer(read_only=True)
    onboarding_tasks = OnboardingChecklistSerializer(many=True, read_only=True)

    class Meta:
        model = Candidate
        fields = '__all__'


class StageUpdateSerializer(serializers.Serializer):
    stage = serializers.ChoiceField(choices=Candidate.STAGE_CHOICES)