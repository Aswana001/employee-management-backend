from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, time, timedelta
from decimal import Decimal
import math
from .models import Attendance, AttendanceRegularization, Shift 
from employee.models import Employee


OFFICE_LAT = 8.558100  
OFFICE_LON = 76.880700  
ALLOWED_RADIUS_KM = 0.5

def calculate_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'



class CheckInSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'check_in', 'location', 'is_valid_geofence']
        extra_kwargs = {
            'date': {'required': False},
            'check_in': {'required': False}
        }

    def create(self, validated_data):
        today = timezone.now().date()
        now = timezone.now()

        # Set default date and check_in if not provided in payload
        validated_data['date'] = validated_data.get('date', today)
        validated_data['check_in'] = validated_data.get('check_in', now)

        # Prevent 500 IntegrityError on duplicate daily check-in
        attendance, created = Attendance.objects.get_or_create(
            employee=validated_data['employee'],
            date=validated_data['date'],
            defaults=validated_data
        )

        if not created:
            # Update existing record for today instead of crashing
            attendance.check_in = validated_data['check_in']
            if 'location' in validated_data:
                attendance.location = validated_data['location']
            attendance.save()

        return attendance


class CheckOutSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'check_out']
        extra_kwargs = {
            'date': {'required': False},
            'check_out': {'required': False}
        }

    def create(self, validated_data):
        today = timezone.now().date()
        now = timezone.now()
        employee = validated_data['employee']

        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
            attendance.check_out = validated_data.get('check_out', now)
            attendance.save()
            return attendance
        except Attendance.DoesNotExist:
            raise serializers.ValidationError({
                "error": "No check-in record found for this employee today."
            })
class AttendanceRegularizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRegularization
        fields = '__all__'
        read_only_fields = ['status', 'approved_by_username']