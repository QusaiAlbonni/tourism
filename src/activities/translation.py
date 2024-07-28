from modeltranslation.translator import register, TranslationOptions, translator
from .models import Listing, Tour, Activity, Ticket

@register(Activity)
class ActivityTranslationOptions(TranslationOptions):
    fields = ()

@register(Listing)
class ListingTranslationOptions(TranslationOptions):
    fields = ()
    

    
@register(Tour)
class TourTranslationOptions(TranslationOptions):
    fields = ()
    
    
    
@register(Ticket)
class TicketTranslationOptions(TranslationOptions):
    fields = ('name', 'description')