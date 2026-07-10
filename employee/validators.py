import re
import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_numeric_phone(value):
    """
    Validates that a string contains a valid, standard numeric phone sequence.
    Permits basic international/domestic standard lengths ranging between 9 to 15 digits.
    """
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    if not phone_regex.match(str(value)):
        raise ValidationError(
            _("Phone number '%(value)s' must be entered in the format: '+999999999'. Up to 15 digits allowed."),
            params={'value': value},
        )

def validate_non_negative(value):
    """
    Ensures currency/monetary value allocations like salary matrices never scale below zero.
    """
    if value < 0:
        raise ValidationError(_("Financial allocations and monetary inputs cannot be a negative value."))

def validate_document_extension(value):
    """
    Restricts file upload payloads exclusively to safe, production-accepted extensions:
    PDF, PNG, JPG, and JPEG. Protects the runtime server environment against arbitrary binary execution.
    """
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    if ext not in valid_extensions:
        raise ValidationError(
            _("Unsupported file extension '%(ext)s'. Allowed formats are: PDF, PNG, JPG, JPEG."),
            params={'ext': ext},
        )