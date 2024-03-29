from .pagination import paginate, encode_cursor
from .casing import camel_keys, snake_keys
from .errors import *
from django.db import models
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import OperationalError
import datetime
import argon2
import uuid
import jwt


REGION = 'MODEL_STORAGE'

def default_get_many_args(kwargs = {}):
    input = kwargs
    input['filters'] = input.get('filters', {})
    input['order_by'] = input.get('order_by', [])
    input['pseudo_fields'] = input.get('pseudo_fields', [])
    input['fields'] = input.get('fields', [])
    return input


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

            field_name = field.name

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

                if not field_name.endswith('_id'):
                    field_name += '_id'

            
            result[field_name] = value

        return result


    @classmethod
    def _unpack_validation_error(cls, e):
        errors = []
        for field_name, messages in e:
            for message in messages:
                errors.append({
                    "message": message,
                    "unique_name": f"INVALID_FIELD:{field_name}",
                    "is_internal": False,
                })

        return errors


class RestResource(BaseModel):
    '''Represents a data type that is exposed by a REST API'''
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        indexes = [ models.Index(fields=['created_at']) ]

    class Pagination:
        default_page_size = 50
    
    class Hooks:
        before_anything = []
        before_create_one = []
        before_delete_one = []
        before_get_many = []
        before_get_one = []
        before_update_one = []

        after_anything = []
        after_create_one = []
        after_delete_one = []
        after_get_many = []
        after_get_one = []
        after_update_one = []


    @classmethod
    def with_hooks(cls, fn, fn_name):
        def wrapper(**input):
            try:
                output = None

                # Applying pre-operation hooks
                after_hooks = getattr(cls.Hooks, f"after_{fn_name}")
                before_hooks = getattr(cls.Hooks, f"before_{fn_name}")

                for hook_fn in cls.Hooks.before_anything + before_hooks:
                    input, errors = hook_fn(**input)

                    if errors:
                        output = { "payload": None, "errors": errors }
                        break

                # Performing the actual data fetching
                output = output if output else fn(**input)

                # Applying post-operation hooks
                for hook_fn in cls.Hooks.after_anything + after_hooks:
                    output = hook_fn(**output)

                return output 

            except Exception as e:
                error = FAILED_UNEXPECTEDLY('applying hooks', region = REGION, exception = e)
                return { "payload": None, "errors": [error] }
        
        return wrapper


    @classmethod
    def delete_one(cls, **input):
        '''Tries to delete a an existing model instance'''

        def inner_fn(**input):
            id = input.get('id', None)

            try:
                # Removing non-field input
                input.pop('auth_claims', None)

                model_instance = cls.objects.get(id=id)
                model_instance.delete()
                payload = model_instance.to_dict()
                return { "payload" : payload, "errors": [] }

            except cls.DoesNotExist:
                return { "payload": None, "errors": [OBJECT_WITH_ID_DOES_NOT_EXIST(id)] }

            except Exception as e:
                error = FAILED_UNEXPECTEDLY('deleting an object', region = REGION, exception = e)
                return { "payload": None, "errors": [error] }

        return cls.with_hooks(inner_fn, 'delete_one')(**input)


    @classmethod
    def update_one(cls, **input):
        '''Attempts to update an existing model instance'''
        
        def inner_fn(**input):
            try:
                # Removing non-field input
                input.pop('auth_claims', None)

                model_instance = cls.objects.get(id=input.get('id', None))
                for key in input:
                    field = getattr(cls, key)

                    if field.field.is_relation is True and input[key] != None:
                        related_model = field.field.related_model
                        input[key] = related_model.objects.get(id = input[key])

                    setattr(model_instance, key, input[key])

                # Validating and storing data
                model_instance.full_clean()
                model_instance.save()

                payload = model_instance.to_dict()
                return { "payload": payload, "errors": [] }

            except ValidationError as e:
                errors = cls._unpack_validation_error(e)
                return { "payload": None, "errors": errors }

            # Exposing AttributeErrors, because they're end-user friendly
            except AttributeError as inst:
                error = { "message": str(inst) }
                return { "payload": None, "errors": [error] }
        
            # Handling attempts to edit non-existent objects
            except cls.DoesNotExist:
                id = input.get('id', None)
                return { "payload": None, "errors": [OBJECT_WITH_ID_DOES_NOT_EXIST(id)] }

            except Exception as e:
                    error = FAILED_UNEXPECTEDLY('updating an object', region = REGION, exception = e)
                    return { "payload": None, "errors": [error] }
        
        return cls.with_hooks(inner_fn, 'update_one')(**input)



    @classmethod
    def create_one(cls, **input):
        '''Tries to store a new model instance'''

        def inner_fn(**input):
            try:
                # Removing non-field input
                input.pop('auth_claims', None)

                for key in input:
                    field = getattr(cls, key)

                    if field.field.is_relation is True and input[key] != None:
                        related_model = field.field.related_model
                        input[key] = related_model.objects.get(id = input[key])

                # Validating and storing data
                model_instance = cls(**input)
                model_instance.full_clean()
                model_instance.save()

                payload = model_instance.to_dict()
                return { "payload": payload, "errors": [] }

            except ValidationError as e:
                errors = cls._unpack_validation_error(e)
                return { "payload": None, "errors": errors }

            except Exception as e:
                error = FAILED_UNEXPECTEDLY('storing new object', region = REGION, exception = e)
                return { "payload": None, "errors": [error] }
        
        return cls.with_hooks(inner_fn, 'create_one')(**input)


    @classmethod
    def get_one(cls, **input):
        """Retrieve a single model instance as a dictionary"""

        def inner_fn(**input):
            try:
                # Removing non-field input
                input.pop('auth_claims', None)

                id = input.get('id', None)
                model_instance = cls.objects.get(id=id)
                return { 'payload': model_instance.to_dict(), 'errors': [] }

            except cls.DoesNotExist:
                return { "payload": None, "errors": [OBJECT_WITH_ID_DOES_NOT_EXIST(id)] }

            except Exception as e:
                error = FAILED_UNEXPECTEDLY('retrieving an object', region = REGION, exception = e)
                return { "payload": None, "errors": [error] }
        
        return cls.with_hooks(inner_fn, 'get_one')(**input)


    @classmethod
    def get_many(cls, **input):
        """Retrieve a paginated list of model instance dictionaries"""

        def inner_fn(**input):
            try:
                # Removing non-field input
                input.pop('auth_claims', None)

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

                # Removing hidden fields, because pagination.
                # Normally, this would happen in `cls.to_dict()`,
                # but pagination returns objects already as dicts.
                for node in nodes:
                    for field_name in cls.Serializer.hidden_fields:
                        node.pop(field_name)

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
        
            except OperationalError as e:
                return { 'payload': None, "errors": [DATABASE_INTEGRITY_VIOLATED] }

            except Exception as e:
                if 'base64' in str(e):
                    if before:
                        return { 'payload': None, "errors": [INVALID_BEFORE_PARAMETER] }
                    if after:
                        return { 'payload': None, "errors": [INVALID_AFTER_PARAMETER] }

                error = FAILED_UNEXPECTEDLY('retrieving a list of objects', region = REGION, exception = e)
                return { "payload": None, "errors": [error] }

        return cls.with_hooks(inner_fn, 'get_many')(**input)


            

class RestClient(BaseModel):
    '''Represents a human or program that is a consumer of a REST API'''

    class Meta:
        abstract = True

    # TODO document the following:
    # Overriding this class means that every property needs to be provided!
    # username_field must be unique and not blank.
    # password_field must be not blank.
    class Auth:
        secret_key = ''
        username_field = 'username'
        password_field = 'password'

    def save(self, *args, **input):
        '''Saving the model instance, but first hashing the
        plaintext password stored in its `password` field'''
        self.password = argon2.PasswordHasher().hash(self.password)
        super(RestClient, self).save(*args, **input)

    def verify_password(self, password):
        '''Determine whether a given hashed password belongs
        to this model instance'''
        try:
            actual_password = getattr(self, self.Auth.password_field)
            argon2.PasswordHasher().verify(actual_password, password)
            return { "payload": True, "errors": [] }
        except argon2.exceptions.VerifyMismatchError:
            return { "payload": False, "errors": [] }
        except Exception as e:
            error = FAILED_UNEXPECTEDLY('verifying password', region = 'AUTHENTICATION', exception = e)
            return { "payload": None, "errors": [error] }

    def authenticate(self, password):
        '''Generate a JWT if the provided password is correct,
        and None if it was incorrect'''
        try:
            verification = self.verify_password(password)
            is_correct = verification.get("payload", None)
            errors = verification.get("errors", [])

            if len(errors):
                return { "payload": None, "errors": errors }

            if is_correct:
                model_name = self.__class__.__name__
                claims = { f"{model_name}": self.to_dict() }
                token = jwt.encode(claims, self.Auth.secret_key, algorithm='HS256')
                return { "payload": token, "errors": [] }
            else:
                return { "payload": None, "errors": [INCORRECT_AUTH_CREDENTIALS] }
        except Exception as e:
                error = FAILED_UNEXPECTEDLY(action = 'encoding auth token', region = 'AUTHENTICATION', exception = e)
                return { "payload": None, "errors": [error] }


