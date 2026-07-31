from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import AppraisalCycle, Goal, Appraisal
from .serializers import (
    AppraisalCycleSerializer, GoalSerializer, AppraisalSerializer,
    SelfReviewSerializer, ManagerReviewSerializer, CalibrationSerializer
)


class AppraisalCycleListCreateAPIView(generics.ListCreateAPIView):
    queryset = AppraisalCycle.objects.all()
    serializer_class = AppraisalCycleSerializer
    permission_classes = [AllowAny]


class GoalListCreateAPIView(generics.ListCreateAPIView):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
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
            serializer = SelfReviewSerializer(appraisal, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(status='SUBMITTED_SELF')
                return Response(
                    {"message": "Self-review submitted successfully.", "data": serializer.data},
                    status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Appraisal.DoesNotExist:
            return Response({"error": "Appraisal record not found."}, status=status.HTTP_404_NOT_FOUND)


class ManagerReviewAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            appraisal = Appraisal.objects.get(pk=pk)
            serializer = ManagerReviewSerializer(appraisal, data=request.data, partial=True)
            if serializer.is_valid():
                manager_rating = serializer.validated_data.get('manager_rating')
                
                # Automated Scoring & Performance Band Assignment Logic
                final_score = manager_rating  # Can be expanded with weighted goal calculations
                if final_score >= 4.5:
                    band = 'EXCEEDS'
                elif final_score >= 3.5:
                    band = 'MEETS'
                else:
                    band = 'NEEDS_IMPROVEMENT'

                appraisal.manager_feedback = serializer.validated_data.get('manager_feedback')
                appraisal.manager_rating = manager_rating
                appraisal.final_score = final_score
                appraisal.performance_band = band
                appraisal.status = 'COMPLETED'
                appraisal.save()

                return Response({
                    "message": "Manager review submitted and scored successfully.",
                    "final_score": final_score,
                    "performance_band": band,
                    "status": appraisal.status
                }, status=status.HTTP_200_OK)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Appraisal.DoesNotExist:
            return Response({"error": "Appraisal record not found."}, status=status.HTTP_404_NOT_FOUND)


class CalibrateAppraisalAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            appraisal = Appraisal.objects.get(pk=pk)
            serializer = CalibrationSerializer(appraisal, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(status='CALIBRATED')
                return Response({
                    "message": "Appraisal successfully calibrated by HR.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Appraisal.DoesNotExist:
            return Response({"error": "Appraisal record not found."}, status=status.HTTP_404_NOT_FOUND)