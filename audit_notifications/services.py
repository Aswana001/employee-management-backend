from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, AuditLog


def log_audit_action(user, action, module_name, description, request=None):
    """
    Extracts network metadata from HTTP request (if provided) and creates
    an AuditLog entry.
    """
    ip_address = None
    user_agent = None

    if request:
        # Check for client IP behind proxies/load balancers, fallback to REMOTE_ADDR
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
            
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

    return AuditLog.objects.create(
        actor=user if user and user.is_authenticated else None,
        action=action,
        module_name=module_name,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )


def send_system_notification(recipient, title, message, notification_type='INFO', send_email=False):
    """
    Creates an in-app Notification record, and conditionally dispatches 
    an SMTP email if requested.
    """
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type
    )

    if send_email and recipient.email:
        try:
            send_mail(
                subject=title,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@company.com'),
                recipient_list=[recipient.email],
                fail_silently=True,  # Prevent SMTP drops from breaking API requests
            )
        except Exception:
            pass  # Log exceptions if an external email provider fails

    return notification