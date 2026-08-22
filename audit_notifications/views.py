from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification, AuditLog
from .serializers import NotificationSerializer, AuditLogSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users to view and interact with their notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Enforce multi-tenant privacy: users only see their notifications
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Marks a single notification as read."""
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
        return Response({'status': 'Notification marked as read'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """Bulk updates all unread notifications for the user."""
        updated_count = self.get_queryset().filter(is_read=False).update(
            is_read=True, 
            read_at=timezone.now()
        )
        return Response(
            {'status': f'Marked {updated_count} notifications as read'}, 
            status=status.HTTP_200_OK
        )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for security admins to review activity logs 
    and compliance summaries.
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'], url_path='compliance-report')
    def compliance_report(self, request):
        """Aggregates audit metrics for compliance reporting."""
        total_logs = AuditLog.objects.count()
        actions_by_type = {
            choice[0]: AuditLog.objects.filter(action=choice[0]).count()
            for choice in AuditLog.ACTION_CHOICES
        }

        return Response({
            'total_audit_records': total_logs,
            'breakdown_by_action': actions_by_type,
            'generated_at': timezone.now()
        }, status=status.HTTP_200_OK)