from i18naddress import InvalidAddressError, normalize_address
from rest_framework.exceptions import ValidationError

class AddressSerializerMixin:
    def validate_i18address(self, attrs):
        address = {}
        address['country_code'] = attrs['country_code']
        address['city']         = attrs['locality']
        address['street_number']= attrs['street_number']
        try:
            address = normalize_address(address)
        except InvalidAddressError as e:
            raise ValidationError(e.errors)
        return address