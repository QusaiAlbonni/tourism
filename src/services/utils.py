from django.db.models import QuerySet
from django.utils.timezone import now
from .models import Service

def get_reviews_prompt(queryset: QuerySet, language, service: Service):
    queryset
    body = get_reviews_string(queryset)
    question = "Please summarize the reviews for the above service.\n"
    verbosity = "medium"
    description = service.description
    starting_remarks = f"""
    
        this is data for a certain service like a hotel or a tourism activity
        the data is a bunch of reviews for said Service,
        the ratings are from 1 to 5,
        here is a description for the service
        Description:
        {description}
        
        """
    
    temperature = 0.5
    
    return {
        'body': body,
        'question': question,
        'language': language,
        'temperature': temperature,
        'starting_remarks': starting_remarks,
        'verbosity': verbosity
    }
    
def get_reviews_string(queryset: QuerySet):

    start_of_month = now().replace(day=1)

    reviews = queryset.filter(created__gte=start_of_month).order_by('-created')[:100]
    
    reviews_string = ""
    
    for review in reviews:
        reviews_string += f"id: {review.pk}\n"
        reviews_string += f"Review: {review.comment}\n"
        reviews_string += f"Rating: {review.rating}\n\n"
    
    return reviews_string