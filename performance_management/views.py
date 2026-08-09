from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import AppraisalCycle, Goal, KPI, Appraisal, Rating
from .serializers import (
    AppraisalCycleSerializer, GoalSerializer, KPISerializer,
    AppraisalSerializer, RatingSerializer,
    SelfReviewSerializer, ManagerReviewSerializer
)


class AppraisalCycleListCreateAPIView(generics.ListCreateAPIView):
    queryset = AppraisalCycle.objects.all()
    serializer_class = AppraisalCycleSerializer
    permission_classes = [AllowAny]


class GoalListCreateAPIView(generics.ListCreateAPIView):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [AllowAny]


class KPIListCreateAPIView(generics.ListCreateAPIView):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [AllowAny]


class AppraisalListCreateAPIView(generics.ListCreateAPIView):
    queryset = Appraisal.objects.all()
    serializer_class = AppraisalSerializer
    permission_classes = [AllowAny]


class SelfReviewAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            appraisal = Appraisal.objects.get(pk=pk)
        except Appraisal.DoesNotExist:
            return Response({"error": "Appraisal not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SelfReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        score = serializer.validated_data['score']
        feedback = serializer.validated_data['feedback']
        kpi_id = serializer.validated_data.get('kpi_id', None)

        # 1. Save entry to Rating model
        Rating.objects.create(
            appraisal=appraisal,
            kpi_id=kpi_id,
            rating_type='SELF',
            score=score,
            comments=feedback
        )

        # 2. Update status and self feedback on Appraisal model
        appraisal.self_feedback = feedback
        appraisal.status = 'SUBMITTED_SELF'
        appraisal.save()

        return Response({
            "message": "Self review submitted successfully.",
            "appraisal_id": appraisal.id,
            "status": appraisal.status,
            "self_feedback": appraisal.self_feedback
        }, status=status.HTTP_200_OK)


class ManagerReviewAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            appraisal = Appraisal.objects.get(pk=pk)
        except Appraisal.DoesNotExist:
            return Response({"error": "Appraisal not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ManagerReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        score = float(serializer.validated_data['score'])
        feedback = serializer.validated_data['feedback']
        kpi_id = serializer.validated_data.get('kpi_id', None)

        # 1. Save entry to Rating model
        Rating.objects.create(
            appraisal=appraisal,
            kpi_id=kpi_id,
            rating_type='MANAGER',
            score=score,
            comments=feedback
        )

        # 2. Assign performance band based on score
        if score >= 4.5:
            band = 'EXCEEDS'
        elif score >= 3.5:
            band = 'MEETS'
        else:
            band = 'NEEDS_IMPROVEMENT'

        # 3. Update status, final score and manager feedback on Appraisal model
        appraisal.manager_feedback = feedback
        appraisal.final_score = score
        appraisal.performance_band = band
        appraisal.status = 'COMPLETED'
        appraisal.save()

        return Response({
            "message": "Manager review submitted successfully.",
            "final_score": score,
            "performance_band": band,
            "status": appraisal.status
        }, status=status.HTTP_200_OK)