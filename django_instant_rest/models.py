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
    
    class Hooks:
        before_get_many = []
        after_get_many = []

    @classmethod
    def get_many(cls, **input):
        """
        Retrieve a paginated list of model instance dictionaries,
        respecting user defined hook functions that run before and
        after data is retrieved.
        """
        try:
            input = default_get_many_args(input)
            output = None

            # Applying pre-operation hooks
            for hook_fn in cls.Hooks.before_get_many:
                input, errors = hook_fn(**input)

                if errors:
                    output = { "payload": None, "errors": errors }
                    break

            # Performing the actual data fetching
            output = output if output else cls.__raw_get_many(**input)

            # Applying post-operation hooks
            for hook_fn in cls.Hooks.after_get_many:
                output = hook_fn(**output)

            return output

        except Exception as e:
            return { "payload": None, "errors": [GET_MANY_FAILED_UNEXPECTEDLY] }

    @classmethod
    def __raw_get_many(cls, **input):
        """Performs the pagination and data fetching for get_many()"""
        
        # Building a queryset using filtering and ordering params
        filters = input.get('filters', {})
        order_by = input.get('order_by', [])
        query = cls.objects.filter(**filters) if len(filters) else cls.objects.all()
        query = query.order_by(*order_by) if len(order_by) else query

        # Modifying the queryset to retrieve only desired fields,
        # and those that are necessary for pagination.
        fields = input.get('fields', [])
        cursor_fields = ['id','created_at']
        query = query.values(*fields, *cursor_fields) if len(fields) else query.values()

        # Destructuring pagination params
        first = input.get('first')
        last = input.get('last')
        before = input.get('before')
        after = input.get('after')

        # Applying pagination
        if not first and not last:
            first = cls.Pagination.default_page_size

        pagination = paginate(query, first, last, after, before)
        if pagination['error']:
            return { "payload": None, "errors": [pagination['error']] }

        # Getting cursor information
        nodes = list(pagination['queryset'])
        first_cursor = None if not len(nodes) else encode_cursor(nodes[0])
        last_cursor = None if not len(nodes) else encode_cursor(nodes[-1])

        # Adding pseudo-fields
        if 'cursor' in input.get('pseudo_fields', []):
            for node in nodes:
                node['cursor'] = encode_cursor(node)

        # Removing unwanted cursor ingredient fields
        if len(fields) and not 'id' in fields:
            for node in nodes:
                node.pop('id', None)

        if len(fields) and not 'created_at' in fields:
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

class RestClient(BaseModel):
    '''Represents a human or program that is a consumer of a REST API'''
    username = models.CharField(max_length=32, unique=True, blank=False)
    password = models.CharField(max_length=512, blank=False)

    class Meta:
        abstract = True
    
    class Hashing:
        secret_key = ''

    def save(self, *args, **input):
        '''Saving the model instance, but first hashing the
        plaintext password stored in its `password` field'''
        self.password = PasswordHasher().hash(self.password)
        super(RestClient, self).save(*args, **input)

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

def default_get_many_args(kwargs = {}):
    input = kwargs
    input['filters'] = input.get('filters', {})
    input['order_by'] = input.get('order_by', [])
    input['pseudo_fields'] = input.get('pseudo_fields', [])
    input['fields'] = input.get('fields', [])
    return input
