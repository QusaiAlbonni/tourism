from django.contrib import admin
from .models import TicketPurchase, Payment, PointsPayment
# Register your models here.

class PurchaseAdmin(admin.ModelAdmin):
    fields = ['ticket', 'scanned', 'scan_date', 'created', 'modified']
    readonly_fields = ['uuid', 'owner', 'created', 'modified']
class PaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Payment._meta.get_fields()]
    
class PointsPaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PointsPayment._meta.get_fields()]    
    
admin.site.register(TicketPurchase, PurchaseAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PointsPayment, PointsPaymentAdmin)