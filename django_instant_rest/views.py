
from .pagination import paginate, encode_cursor
from .casing import camel_keys, snake_keys

import jwt
import json
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models.fields import DateTimeField
from django.utils.timezone import make_aware
from django.db.utils import IntegrityError
from django.db import OperationalError
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
incorrect_credentials_err = { "message" : "incorrect username/password combination" }


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

# A set of query string parameter keys that should not be used for filtering
filter_key_blacklist = { "order_by", }

def read_many(model, camel = False):
    def request_handler(request):
        params = { key: request.GET.get(key) for key in request.GET }
        queryset = None

        # Parsing datestrings found in params
        for key in params:
            for field in date_fields(model):
                if key.startswith(field):
                    try:
                        params[key] = datetime.fromisoformat(params[key])
                    except:
                        message = f"Invalid date string provided for field {key}"
                        invalid_date_err = { "message": message }
                        return JsonResponse({"errors": [invalid_date_err]})

        # Collecting filter parameters
        for key in params:
            if key in filter_key_blacklist:
                continue

            try:
                queryset = model.objects.filter(**{key : params[key]})
            except:
                pass

        # Using the default queryset because no filters were provided
        if queryset is None:
            queryset = model.objects.all()

        # Applying queryset ordering if requested, allowing multiple comma
        # separated values
        try:
            if "order_by" in params:
                order_by_args = params["order_by"].split(",")
                queryset = queryset.order_by(*order_by_args)
        except:
            pass

        # Collecting pagination parameters
        before = params.get("before")
        after = params.get("after")

        if before and after:
            return JsonResponse({"errors": [extra_cursor_param_err]})

        try:
            if params.get('first'):
                first = int(params.get('first'))
            else:
                first = None
        except:
            return JsonResponse({"errors": [invalid_first_param_err]})

        try:
            if params.get('last'):
                last = int(params.get('last'))
            else:
                last = None
        except:
            return JsonResponse({"errors": [invalid_last_param_err]})

        if first and last:
            return JsonResponse({"errors": [extra_quantity_param_err]})

        # Assigning a default page size
        # if none was provided.
        if not first and not last:
            first = 50

        try:
            pagination = paginate(queryset, first, last, after, before)

        except OperationalError:
            return JsonResponse({"errors": [database_operation_err]})

        except Exception as e:
            if 'base64' in str(e):
                if before:
                    return JsonResponse({"errors": [invalid_before_param_err]})
                if after:
                    return JsonResponse({"errors": [invalid_after_param_err]})

            return JsonResponse({"errors": [unknown_pagination_err]})
            
        page = list(pagination['page'])
        has_next_page = pagination['has_next_page']
        data = list(map(lambda m: m.to_dict(), page))

        payload = {
            'first_cursor': None,
            'last_cursor': None,
            'has_next_page': False,
            'data': [],
        }

        if len(page) > 0:
            payload = {
                'first_cursor': encode_cursor(page[0]),
                'last_cursor': encode_cursor(page[-1]),
                'has_next_page': has_next_page,
                'data': data,
            }

        if (camel):
            payload = camel_keys(payload)
            payload["data"] = [ camel_keys(item) for item in payload["data"] ]

        return JsonResponse(payload)

    
    return request_handler


def read_one(model, camel=False):
    def request_handler(request, id):
        try:
            obj = model.objects.get(id=id)
        except:
            return JsonResponse({ "errors": [id_not_exists_err] })

        data = obj.to_dict()

        if (camel):
            data = camel_keys(data)

        return JsonResponse({ "data": data })

    return request_handler


def create_one(model, camel=False):
    @csrf_exempt
    def request_handler(request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            if camel:
                data = snake_keys(data)

        except:
            return JsonResponse({"errors": [invalid_json_err]})

        try:
            for key in data:
                field = getattr(model, key)

                if field.field.is_relation is True and data[key] != None:
                    related_model = field.field.related_model
                    data[key] = related_model.objects.get(id = data[key])

            # Validating and storing the data
            model_instance = model(**data)
            model_instance.full_clean()
            model_instance.save()
            
            data = model_instance.to_dict()

            if camel:
                data = camel_keys(data)

            return JsonResponse({ "data" : data })

        # Exposing Attribute errors, because they're end-user friendly
        except AttributeError as inst:
            error = { "message": str(inst) }
            return JsonResponse({ "errors": [error] })

        # Handling errors generated by database constraints
        except IntegrityError as e:
            return JsonResponse({ "errors": [database_integrity_err] })

        # Handling field validation and uniquness errors
        except ValidationError as e:
            errors = format_validation_error(e, camel=camel)
            return JsonResponse({ "errors": errors })

        # Handling all other errors generically
        except Exception as e:
            return JsonResponse({ "errors": [unknown_storage_err] })

    return request_handler


def update_one(model, camel=False):
    @csrf_exempt
    def request_handler(request, id): 
        try:
            change_data = json.loads(request.body.decode("utf-8"))
            if camel:
                change_data = snake_keys(change_data)

        except:
            return JsonResponse({"errors": [invalid_json_err]})

        try:
            model_instance = model.objects.get(id=id)
                
            for field_name in change_data:
                field = getattr(model, field_name)
                if field.field.is_relation is True and data[key] != None:
                    related_model = field.field.related_model
                    change_data[field_name] = related_model.objects.get(id = change_data[field_name])
                setattr(model_instance, field_name, change_data[field_name])

            # Validating and storing the data
            model_instance.full_clean()
            model_instance.save()
            data = model_instance.to_dict()

            if camel:
                data = camel_keys(data)

            return JsonResponse({"data" : data})

        # Exposing Attribute errors, because they're end-user friendly
        except AttributeError as inst:
            error = { "message": str(inst) }
            return JsonResponse({ "errors": [error] })
        
        except model.DoesNotExist:
            # Handling attempts to edit non-existent objects
            return JsonResponse({"errors": [id_not_exists_err]})

        # Handling field validation and uniquness errors
        except ValidationError as e:
            errors = format_validation_error(e, camel=camel)
            return JsonResponse({ "errors": errors })

        except Exception as inst:
            # Handling all other errors generically
            return JsonResponse({"errors": [invalid_data_err]})

    return request_handler


def delete_one(model):
    @csrf_exempt
    def request_handler(request, id):
        try:
            obj = model.objects.get(id=id)
            obj.delete()
            data = obj.to_dict()
            return JsonResponse({ "data" : data })
        except:
            return JsonResponse({ "errors": [id_not_exists_err] })

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
                raise
                
            return JsonResponse({ "data": { "token": token } })

        except Exception as inst:
            return JsonResponse({ 'errors': [incorrect_credentials_err] }, status=400)
    
    return handler
