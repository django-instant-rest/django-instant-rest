
from django.db import models
from django_instant_rest.models import RestResource, RestClient
from tests import settings


class Author(RestResource):
    '''All models that inherit from `RestResource` will have a `created_at`
    and `updated_at` field by default.'''

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

class Book(RestResource):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

class StoreLocation(RestResource):
    street_address = models.CharField(max_length=255)
    state_or_province = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

class BookInventory(RestResource):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    location = models.ForeignKey(StoreLocation, on_delete=models.CASCADE)
    quantity: models.PositiveIntegerField()

class Employee(RestResource):
    location = models.ForeignKey(StoreLocation, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

class Customer(RestResource, RestClient):
    '''All models that inherit from `RestClient` will have a `username`
    and `password` field by default.'''

    email = models.CharField(max_length=127)
    phone = models.CharField(max_length=63)

    class Hashing:
        '''Providing a secret value for encoding and decoding passwords.
        This should never be hard-coded when running in production.'''
        secret_key = settings.SECRET_KEY

    class Serializer:
        '''Listing fields that should be hidden from API consumers'''
        hidden_fields = ['password']
