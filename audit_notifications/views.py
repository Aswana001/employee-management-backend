from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Notification, AuditLog
from .serializers import NotificationSerializer, AuditLogSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Always return all notifications when testing without auth
        return Notification.objects.all()

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marked as read'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        updated_count = Notification.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': f'Marked {updated_count} notifications as read'}, status=status.HTTP_200_OK)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], url_path='compliance-report')
    def compliance_report(self, request):
        total_logs = AuditLog.objects.count()
        return Response({
            'total_audit_records': total_logs,
            'status': 'Audit tracking active (Authentication Bypassed)'
        })