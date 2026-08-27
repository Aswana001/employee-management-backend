from .models import AuditLog

def log_audit_action(user, action, module_name, description="", request=None):
    """Safely logs audit actions even when user is unauthenticated or None."""
    
    actor = None
    if user and getattr(user, 'is_authenticated', False):
        actor = user

    ip_address = None
    user_agent = ""

    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

    return AuditLog.objects.create(
        actor=actor,
        action=action,
        module_name=module_name,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )