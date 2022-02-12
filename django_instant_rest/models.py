from .pagination import paginate, encode_cursor
from .casing import camel_keys, snake_keys
from .errors import *
from argon2 import PasswordHasher
from django.db import models
import datetime
import uuid
import jwt


class BaseModel(models.Model):
    '''A generic model with commonly used methods'''

    class Meta:
        abstract = True

    class Serializer:
        hidden_fields = []

    def to_dict(self):
        '''Convert model instances to dictionaries'''
        result = {}
        for field in self._meta.fields:

            # Skipping hidden fields
            if field.name in self.Serializer.hidden_fields:
                continue

            value = getattr(self, field.name)

            # Handling UUID fields
            if type(value) == uuid.UUID:
                value = str(value)

            # Handling datetime fields
            if type(value) == datetime.datetime:
                value = value.isoformat()

            # Handling relational fields 
            if hasattr(value, "id"):
                value = value.id
            
            result[field.name] = value

        return result


class RestResource(BaseModel):
    '''Represents a data type that is exposed by a REST API'''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        indexes = [ models.Index(fields=['created_at']) ]

    class Pagination:
        default_page_size = 50

    @classmethod
    def get_many(cls, first=None, last=None, after=None, before=None, filters={}, order_by=[], fields=None, pseudo_fields=None):
        """Get a paginated list of model instance dicts, or errors"""
        try:
            # Applying filtering and ordering
            queryset = cls.objects.filter(**filters)
            queryset = queryset.order_by(*order_by)

            # Selecting desired fields
            cursor_fields = ['id','created_at']
            queryset = queryset.values() if not fields else queryset.values(*fields, *cursor_fields)

            # Applying pagination
            if not first and not last:
                first = cls.Pagination.default_page_size

            pagination = paginate(queryset, first, last, after, before)
            if pagination['error']:
                return { "payload": None, "errors": [pagination['error']] }

            # Getting cursor information
            nodes = list(pagination['page'])
            first_cursor = None if not len(nodes) else encode_cursor(nodes[0])
            last_cursor = None if not len(nodes) else encode_cursor(nodes[-1])

            # Adding pseudo-fields
            if pseudo_fields and 'cursor' in pseudo_fields:
                for node in nodes:
                    node['cursor'] = encode_cursor(node)

            # Removing unwanted cursor ingredient fields
            if fields and not 'id' in fields:
                for node in nodes:
                    node.pop('id', None)

            if fields and not 'created_at' in fields:
                for node in nodes:
                    node.pop('created_at', None)

            return {
                'payload': {
                    'first_cursor': first_cursor,
                    'last_cursor': last_cursor,
                    'has_next_page': pagination['has_next_page'],
                    'has_prev_page': pagination['has_prev_page'],
                    'nodes': nodes,
                },
                'errors': [],
            }

        except Exception as e:
            return {
                "payload": None,
                "errors": [UNEXPECTEDLY_FAILED_TO_GET_MANY],
            }

class RestClient(BaseModel):
    '''Represents a human or program that is a consumer of a REST API'''
    username = models.CharField(max_length=32, unique=True, blank=False)
    password = models.CharField(max_length=512, blank=False)

    class Meta:
        abstract = True
    
    class Hashing:
        secret_key = ''

    def save(self, *args, **kwargs):
        '''Saving the model instance, but first hashing the
        plaintext password stored in its `password` field'''
        self.password = PasswordHasher().hash(self.password)
        super(RestClient, self).save(*args, **kwargs)

    def verify_password(self, password):
        '''Determine whether a given hashed password belongs
        to this model instance'''
        return PasswordHasher().verify(self.password, password)

    def authenticate(self, password):
        '''Generate a JWT if the provided password is correct,
        and None if it was incorrect'''
        if self.verify_password(password):
            payload = self.to_dict()
            return jwt.encode(payload, self.Hashing.secret_key, algorithm='HS256')
        else:
            return None
