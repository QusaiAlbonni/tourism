import datetime
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import BaseValidator

class DateLessThanToday(BaseValidator):
    message = _('Date cannot be in the past.')
    code = 'date_in_past'

    def compare(self, value, now):
        if type(value) == datetime.date:
            now = timezone.now().date()
        elif type(value) == datetime.datetime:
            now = timezone.now()
        else:
            raise ValueError()
        return value < now

    def clean(self, x):
        return x