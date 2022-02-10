
from bookstore.models import *
from django_instant_rest import patterns

urlpatterns = [
    patterns.resource('authors', Author),
    patterns.resource('books', Book),
    patterns.client('customers', Customer),
]