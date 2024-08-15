from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money
from decimal import Decimal

class CurrencyConversionMixin:
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request:
            converted_price=instance.price
            target_currency = request.headers.get('Currency')
            if target_currency and 'price' in representation and 'price_currency' in representation:
 
                from_currency = instance.price_currency
                amount = instance.price.amount
                converted_price = convert_money(Money(amount, from_currency), target_currency)
                representation['price'] = converted_price.amount
                representation['price_currency'] = target_currency
            print(0)
            if hasattr(instance, 'activity'):
                print(1)
                discount = getattr(instance.activity, 'discount', 0)
                print(discount)
            elif hasattr(instance, 'property_id'):
                print(2)
                discount = getattr(instance.property_id, 'discount', 0)
                print(discount)
            else:
                print(3)
                discount = 0
            converted_price.amount = converted_price.amount * (1 - discount / Decimal(100))
            representation['price_after_discount'] = converted_price.amount
        
        return representation
