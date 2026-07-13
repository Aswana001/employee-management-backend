from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, time, timedelta
from decimal import Decimal
import math
from .models import Attendance, AttendanceRegularization, Shift

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
    class Meta:
        model = Attendance
        fields = ['employee', 'shift', 'check_in_latitude', 'check_in_longitude']

    def create(self, validated_data):
        now = timezone.now()
        current_date = now.date()
        
        distance = calculate_haversine(
            float(validated_data['check_in_latitude']), float(validated_data['check_in_longitude']),
            OFFICE_LAT, OFFICE_LON
        )
        geofence_valid = distance <= ALLOWED_RADIUS_KM
        
        shift = validated_data['shift']
        late_flag = False
        if shift:
            shift_start_dt = timezone.make_aware(datetime.combine(current_date, shift.start_time))
            if now > (shift_start_dt + timezone.timedelta(minutes=shift.grace_period_mins)):
                late_flag = True

        attendance, created = Attendance.objects.update_or_create(
            employee=validated_data['employee'],
            date=current_date,
            defaults={
                'shift': shift,
                'check_in': now,
                'check_in_latitude': validated_data['check_in_latitude'],
                'check_in_longitude': validated_data['check_in_longitude'],
                'is_late': late_flag,
                'is_valid_geofence': geofence_valid
            }
        )
        return attendance

class CheckOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['employee', 'check_out_latitude', 'check_out_longitude']

    def create(self, validated_data):
        current_date = timezone.now().date()
        try:
            attendance = Attendance.objects.get(employee=validated_data['employee'], date=current_date)
        except Attendance.DoesNotExist:
            raise serializers.ValidationError("Error: Active Check-In instance not found for today.")

        now = timezone.now()
        attendance.check_out = now
        attendance.check_out_latitude = validated_data['check_out_latitude']
        attendance.check_out_longitude = validated_data['check_out_longitude']
        
        if attendance.shift and attendance.check_in:
            shift_end_dt = timezone.make_aware(datetime.combine(current_date, attendance.shift.end_time))
            if now > shift_end_dt:
                delta = now - shift_end_dt
                attendance.overtime_hours = round(Decimal(delta.total_seconds() / 3600), 2)
        
        attendance.save()
        return attendance

class AttendanceRegularizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRegularization
        fields = '__all__'
        read_only_fields = ['status', 'approved_by_username']