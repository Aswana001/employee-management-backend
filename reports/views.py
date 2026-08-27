from django.http import HttpResponse
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .services import DashboardAnalyticsService, ExportService
from employee.models import Employee


class ExecutiveDashboardAPIView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        metrics = DashboardAnalyticsService.get_executive_summary()
        return Response(metrics, status=status.HTTP_200_OK)


class EmployeeReportAPIView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        department_id = request.query_params.get('department')
        export_format = request.query_params.get('export')

        queryset = Employee.objects.all()

        if department_id:
            queryset = queryset.filter(department_id=department_id)

        # Fields to include in report
        fields = ['id', 'first_name', 'last_name', 'department__name', 'designation__title']

        # Handle Excel Export Trigger
        if export_format == 'excel':
            try:
                excel_file = ExportService.generate_excel_report(queryset, fields, sheet_name="Employees")
                
                response = HttpResponse(
                    excel_file.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename="employee_report.xlsx"'
                return response
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return standard JSON response
        report_data = list(queryset.values(*fields))
        return Response({
            'count': len(report_data), 
            'results': report_data
        })