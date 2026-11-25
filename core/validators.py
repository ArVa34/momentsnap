from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

MAX_IMAGE_SIZE_MB = 5


def validate_image_size(file):
    """Reject uploaded files larger than MAX_IMAGE_SIZE_MB."""
    limit = MAX_IMAGE_SIZE_MB * 1024 * 1024
    if file.size > limit:
        raise ValidationError(
            _("Image is too large. The maximum size is %(size)s MB."),
            params={"size": MAX_IMAGE_SIZE_MB},
        )