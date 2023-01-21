
from .pagination import paginate, encode_cursor
from .casing import camel_keys, snake_keys
from .errors import *

import jwt
import json
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models.fields import DateTimeField, UUIDField
from django.utils.timezone import make_aware
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

id_not_exists_err = {"message": "Requested id does not exist" }
empty_body_err = {"message" : "Request body is empty"}
no_body_err = {"message" : "Request body does not exist"}
invalid_json_err = {"message" : "Request body is not valid json"}
missing_id_err = {"message" : "Required id not provided"}
invalid_data_err = {"message" : "Invalid data type received"}
unsupported_method_err = {"message" : "Request method not supported by url"}
invalid_pagination_params_err = {"message" : "Invalid pagination parameters provided"}
unknown_pagination_params_err = {"message" : "Something went wrong while trying to perform pagination"}
invalid_first_param_err = {"message" : "Expected parameter 'first' to be a positive integer"}
invalid_last_param_err = {"message" : "Expected parameter 'last' to be a positive integer"}
extra_cursor_param_err = {"message" : "Expected either 'before' parameter or 'after', not both"}
extra_quantity_param_err = {"message" : "Expected either 'first' parameter or 'last', not both"}
invalid_before_param_err = {"message" : "Expected parameter 'before' to be a base64 encoded string"}
invalid_after_param_err = {"message" : "Expected parameter 'after' to be a base64 encoded string"}
database_integrity_err = {"message" : "The data provided violates database constraints" }
database_operation_err = {"message" : "Unable to read from the database. Migrations may not be current." }
unknown_storage_err = { "message": "Unable to store the data provided" }
incorrect_credentials_err = { "message" : "Incorrect username/password combination" }


REGION = 'REQUEST_HANDLING'
ACTION = 'interpreting HTTP requests'

def format_validation_error(e: ValidationError, camel=False):
    errors = []

    # Applying casing
    field_messages = e.message_dict
    if camel:
        field_messages = camel_keys(field_messages)

    # Re-formatting error messages
    for (field, messages) in field_messages.items():
        for message in messages:
            errors.append({ "field": field, "message": message.lower() })

    return errors



def date_fields(model):
    '''
    Return a list of strings that correspond to a model's
    fields that are instances of DateTimeField
    '''
    def is_date_field(name):
        return type(getattr(model, name).field) == DateTimeField

    field_names = [f.name for f in model._meta.fields]
    return list(filter(is_date_field, field_names))


def read_many(model, camel = False):
    def request_handler(request):
        try:
            params = { key: request.GET.get(key) for key in request.GET }
            queryset = None

            # Parsing datestrings found in params
            for key in params:
                for field in date_fields(model):
                    if key.startswith(field):
                        try:
                            params[key] = datetime.fromisoformat(params[key])
                        except:
                            return JsonResponse({ "payload": None, "errors": [INVALID_DATE_RECIEVED(key)]})

            # Collecting pagination params
            first = params.pop('first', None)
            first = int(first) if first else None

            last = params.pop('last', None)
            last = int(last) if last else None

            after = params.pop('after', None)
            before = params.pop('before', None)

            # Collecting ordering params
            order_by = params.pop('order_by', None)
            order_by = order_by.split(",") if order_by else []

            # Aggregating params
            get_many_args = {
                'first': first,
                'last': last,
                'after': after,
                'before': before,
                'order_by': order_by,
                'filters': params,
            }

            # Collecting filter parameters
            results = model.get_many(**get_many_args)
            payload = results['payload']
            errors = results['errors']

            # Applying Camel Casing
            if (camel):
                payload = camel_keys(payload)

            return JsonResponse({ 'payload': payload, 'errors': errors })

        except Exception as e:
            error = FAILED_UNEXPECTEDLY(action = ACTION, region = REGION, exception = e)
            return { "payload": None, "errors": [error] }

    return request_handler


def read_one(model, camel=False):
    def request_handler(request, id):
        try:
            id_field = model._meta.get_field('id')
            clean_id = id if type(id_field) == UUIDField else int(id)
            result = model.get_one(id=clean_id)

            if camel:
                result= camel_keys(result)

            return JsonResponse(result)

        except Exception as e:
            error = FAILED_UNEXPECTEDLY(action = ACTION, region = REGION, exception = e)
            return { "payload": None, "errors": [error] }

    return request_handler


def create_one(model, camel=False):

    @csrf_exempt
    def request_handler(request):
        try:
            fields = json.loads(request.body.decode("utf-8"))
            if camel:
                fields = snake_keys(fields)

            result = model.create_one(**fields)
            payload = result['payload']
            errors = result['errors']

            if len(errors):
                return JsonResponse({ "payload": None, "errors" : errors })

            if camel:
                payload = camel_keys(payload)

            return JsonResponse({ "payload" : payload, "errors": [] })

        except json.JSONDecodeError as e:
            return JsonResponse({ "payload": None, "errors": [INVALID_JSON_RECEIVED(e)] })

        # Exposing Attribute errors, because they're end-user friendly
        except AttributeError as inst:
            error = { "message": str(inst) }
            return JsonResponse({ "payload": None, "errors": [error] })

        # Handling errors generated by database constraints
        except IntegrityError as e:
            return JsonResponse({ "payload": None, "errors": [DATABASE_INTEGRITY_VIOLATED] })

        # Handling field validation and uniqueness errors
        except ValidationError as e:
            errors = format_validation_error(e, camel=camel)
            return JsonResponse({ "payload": None, "errors": errors })

        # Handling all other errors generically
        except Exception as e:
            error = FAILED_UNEXPECTEDLY(action = ACTION, region = REGION, exception = e)
            return JsonResponse({ "payload": None, "errors": [error] })

    return request_handler


def update_one(model, camel=False):
    @csrf_exempt
    def request_handler(request, id): 
        try:
            input = json.loads(request.body.decode("utf-8"))
            id_field = model._meta.get_field('id')
            clean_id = id if type(id_field) == UUIDField else int(id)
            input['id'] = clean_id
            if camel:
                input = snake_keys(input)
            return JsonResponse(model.update_one(**input))

        except json.JSONDecodeError as e:
            return JsonResponse({ "payload": None, "errors": [INVALID_JSON_RECEIVED(e)] })

        except Exception as e:
            error = FAILED_UNEXPECTEDLY(action = ACTION, region = REGION, exception = e)
            return JsonResponse({ "payload": None, "errors": [error] })

    return request_handler


def delete_one(model):
    @csrf_exempt
    def request_handler(request, id):
        try:
            id_field = model._meta.get_field('id')
        except Exception as e:
            return JsonResponse({ "payload": None, "errors": [id_not_exists_err] })

        try:
            clean_id = id if type(id_field) == UUIDField else int(id)
            result = model.delete_one(id=clean_id)
            return JsonResponse(result)
        except Exception as e:
            error = FAILED_UNEXPECTEDLY(action = ACTION, region = REGION, exception = e)
            return JsonResponse({ "payload": None, "errors": [error] })

    return request_handler


def resource(model, camel=False):
    @csrf_exempt
    def request_handler(request, id=None):
        # POST
        if request.method =='POST':
            return create_one(model, camel)(request)

        # GET 
        elif request.method =='GET':
            if id:
                return read_one(model, camel)(request, id)
            else:
                return read_many(model, camel)(request)

        # PUT
        elif request.method == 'PUT':
            if id:
                return update_one(model, camel)(request, id)
            else:
                return JsonResponse({"errors": [missing_id_err]})

        # DELETE
        elif request.method =='DELETE':
            if id:
                return delete_one(model)(request, id)
            else:
                return JsonResponse({"errors": [missing_id_err]})

        else:
            return JsonResponse({"errors" : [unsupported_method_err]})

    return request_handler


def authenticate(client_model):
    @csrf_exempt
    def handler(request):
        '''Allows requesters to provide username/password
        combinations in exchange for a json web token'''
        try:
            credentials = json.loads(request.body.decode("utf-8"))

        except:
            message = "expected POST request with json body"
            return JsonResponse({ 'error': message }, status=400)

        try:
            c = client_model.objects.get(username=credentials["username"])
            token = c.authenticate(credentials["password"])

            if not token:
                # TODO
                raise

            return JsonResponse({ "data": { "token": token } })

        except Exception as inst:
            return JsonResponse({ 'errors': [incorrect_credentials_err] }, status=400)

    return handler
