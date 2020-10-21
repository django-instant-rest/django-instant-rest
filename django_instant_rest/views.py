

from . import serializers
from .pagination import paginate, encode_cursor

import json
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models.fields import DateTimeField
from django.utils.timezone import make_aware


id_not_exists_err = {"message": "Requested id does not exist" }
empty_body_err = {"message" : "Request body is empty"}
no_body_err = {"message" : "Request body does not exist"}
invalid_json_err = {"message" : "Request body is not valid json"}
missing_id_err = {"message" : "Required id not provided"}
invalid_data_err = {"message" : "Invalid data type received"}
unsupported_method_err = {"message" : "Request method not supported by url"}
invalid_paginagion_params_err = {"message" : "Invalid pagination parameters provided"}



def date_fields(model):
    '''
    Return a list of strings that correspond to a model's
    fields that are instances of DateTimeField
    '''
    def is_date_field(name):
        return type(getattr(model, name).field) == DateTimeField
    
    field_names = [f.name for f in model._meta.fields]
    return list(filter(is_date_field, field_names))



def read_many(model):
    def request_handler(request):
        params = { key: request.GET.get(key) for key in request.GET }
        queryset = None

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
            try:
                queryset = model.objects.filter(**{key : params[key]})
            except:
                pass

        if queryset is None:
            queryset = model.objects.all()

        # Collecting pagination parameters
        before = params.get("before")
        after = params.get("after")

        if params.get('first'):
            first = int(params.get('first'))
        else:
            first = None

        if params.get('last'):
            last = int(params.get('last'))
        else:
            last = None

        # Assigning a default page size
        # if none was provided.
        if not first and not last:
            first = 50

        try:
            pagination = paginate(queryset, first, last, after, before)
        except:
            return JsonResponse({"errors": [invalid_pagination_params_err]})
            
        page = list(pagination['page'])
        has_next_page = pagination['has_next_page']

        data = list(map(serializers.model_to_dict, page))

        if len(page) is 0:
            return JsonResponse({
                'first_cursor': None,
                'last_cursor': None,
                'has_next_page': False,
                'data': [],
            })

        return JsonResponse({
            'first_cursor': encode_cursor(page[0]),
            'last_cursor': encode_cursor(page[-1]),
            'has_next_page': has_next_page,
            'data': data,
        })

    
    return request_handler


def read_one(model):
    def request_handler(request, id):
        try:
            obj = model.objects.get(id=id)
        except:
            return JsonResponse({"errors": [id_not_exists_err]})
        data = serializers.model_to_dict(obj)
        return JsonResponse({"data": data})        
    return request_handler
  

def create_one(model):
    @csrf_exempt
    def request_handler(request):
        try:
            data = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({"errors": [invalid_json_err]})
        try:
            for key in data:
                field = getattr(model, key)
                if field.field.is_relation is True:
                    related_model = field.field.related_model
                    data[key] = related_model.objects.get(id = data[key])

            m = model.objects.create(**data)
            data = serializers.model_to_dict(m)
            return JsonResponse({"data" : data})
        except:
            return JsonResponse({"errors": [invalid_data_err]})
    return request_handler


def update_one(model):
    @csrf_exempt
    def request_handler(request, id): 
        try:
            change_data = json.loads(request.body.decode("utf-8"))
        except:
            return JsonResponse({"errors": [invalid_json_err]})
        try:
            obj = model.objects.get(id=id)
                
            for field_name in change_data:
                field = getattr(model, field_name)
                if field.field.is_relation is True:
                    related_model = field.field.related_model
                    change_data[field_name] = related_model.objects.get(id = change_data[field_name])
                setattr(obj, field_name, change_data[field_name])

            obj.save()
            data = serializers.model_to_dict(obj)
            return JsonResponse({"data" : data})
        except:
            return JsonResponse({"errors": [id_not_exists_err]})
    return request_handler


def delete_one(model):
    @csrf_exempt
    def request_handler(request, id):
        try:
            obj = model.objects.get(id=id)
            obj.delete()
            data = serializers.model_to_dict(obj)
            return JsonResponse({"data" : data})
        except:
            return JsonResponse({"errors": [id_not_exists_err]})
    return request_handler


def resource(model):
    @csrf_exempt
    def request_handler(request, id=None):
        if request.method =='POST':
            return create_one(model)(request)
        elif request.method =='GET':
            if id:
                return read_one(model)(request, id)
            else:
                return read_many(model)(request)
        elif request.method == 'PUT':
            if id:
                return update_one(model)(request, id)
            else:
                return JsonResponse({"errors": [missing_id_err]})
        elif request.method =='DELETE':
            if id:
                return delete_one(model)(request, id)
            else:
                return JsonResponse({"errors": [missing_id_err]})
        else:
            return JsonResponse({"errors" : [unsupported_method_err]})
    return request_handler

