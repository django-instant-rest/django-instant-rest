
from django.db import models
from django_instant_rest.models import RestResource, RestClient
from tests import settings
from argon2 import PasswordHasher


def hash_password(**input):
    password = input.get('password', None)
    if type(password) != str:
        return (None, {
            'message': 'Expected "password" to be a string',
            'unique_name': 'UNEXPECTED_PASSWORD_TYPE',
            'is_internal': False,
        })

    input['password'] = PasswordHasher().hash(password)
    return (input, None)


class Admin(RestResource):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    class Hooks(RestResource.Hooks):
        before_create_one = [
            hash_password,
        ]


class Product(RestResource):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)

class ProductMeta(RestResource):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=2047)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class ProductImage(RestResource):
    filename = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class Variant(RestResource):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    price_in_cents_usd = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['slug', 'product'], ['name', 'product']]


class VariantDimension(RestResource):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class VariantDimensionValue(RestResource):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    dimension = models.ForeignKey(VariantDimension, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = [['variant', 'dimension', 'value']]


class VariantMeta(RestResource):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=2047)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

class VariantImage(RestResource):
    filename = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class StoreAdmin(RestResource, RestClient):
    '''All models that inherit from `RestClient` will have a `username`
    and `password` field by default.'''

    email = models.CharField(max_length=255)

    class Hashing:
        '''Providing a secret value for encoding and decoding passwords.
        This should never be hard-coded when running in production.'''
        secret_key = settings.SECRET_KEY

    class Serializer:
        '''Listing fields that should be hidden from API consumers'''
        hidden_fields = ['password']


class NavigationItem(RestResource):
    name = models.CharField(max_length=255)
    pathname = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
