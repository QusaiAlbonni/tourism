from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _

class NonRefundableError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("This item is not refundable.")
    default_code = "non_refundable_error"
    
class NonRefundableException(Exception):
    """Exception raised when an item is not refundable."""
    def __init__(self, message="This item is not refundable."):
        self.message = message
        super().__init__(self.message)
        
class CantBeCanceled(Exception):
    """Exception raised when an item is not refundable."""
    def __init__(self, message="This item cannot be canceled."):
        self.message = message
        super().__init__(self.message)
        
class CantBeCanceledError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("This item can't be canceled.")
    default_code = "non_refundable_error"