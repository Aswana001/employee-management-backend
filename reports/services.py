import io
import pandas as pd
from django.db.models import Count, Sum, Avg
from django.utils import timezone

from employee.models import Employee, Department


class DashboardAnalyticsService:
    @staticmethod
    def get_executive_summary():
        today = timezone.now().date()
        total_employees = Employee.objects.filter(is_active=True).count()
        departments_count = Department.objects.count()

        return {
            "headcount": {
                "total_active_employees": total_employees,
                "departments_count": departments_count
            }
        }


class ExportService:
    @staticmethod
    def generate_excel_report(queryset, fields, sheet_name="Report"):
        """Converts a Django QuerySet into a clean Excel file buffer."""
        # Convert queryset values to a list of dicts
        raw_data = list(queryset.values(*fields))
        
        # Clean double-underscore keys (e.g., department__name -> Department Name)
        cleaned_data = []
        for row in raw_data:
            cleaned_row = {}
            for key, val in row.items():
                # Replace double underscores with space and capitalize
                clean_key = key.replace('__', ' ').replace('_', ' ').title()
                cleaned_row[clean_key] = val if val is not None else ""
            cleaned_data.append(cleaned_row)

        if not cleaned_data:
            # Generate clean empty dataframe if queryset is empty
            headers = [f.replace('__', ' ').replace('_', ' ').title() for f in fields]
            df = pd.DataFrame(columns=headers)
        else:
            df = pd.DataFrame(cleaned_data)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        output.seek(0)
        return output