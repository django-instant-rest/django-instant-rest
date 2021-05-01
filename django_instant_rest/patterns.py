
from . import views
from django.urls import re_path


# Create a urlpattern element that allows CRUD
# operations for a given model. 
def resource(name, model, middleware = None, camel=False):
    route = rf"^{name}/(?P<id>.*)$|^{name}$"

    if not middleware:
        return re_path(route, views.resource(model, camel))

    # Using a django-style middleware callable
    # if it was provided as a function parameter.
    # https://docs.djangoproject.com/en/3.1/topics/http/middleware/

    def handler(request, id = None):
        def get_response(request, id = id):
            final_handler = views.resource(model, camel=camel)
            return final_handler(request, id)

        middleware_callable = middleware(get_response)
        response = middleware_callable(request, id = id)
        return response


    return re_path(route, handler)


# Create a request handler that allows REST clients to authenticate.
# In the future, it may be associated with additional actions.
def client(name, client_model, middleware=None):
    route = rf"^{name}/authenticate$"

    if not middleware:
        return re_path(route, views.authenticate(client_model))

    # Using a django-style middleware callable
    # if it was provided as a function parameter.
    # https://docs.djangoproject.com/en/3.1/topics/http/middleware/

    def handler(request):
        def get_response(request):
            return views.authenticate(client_model)(request)

        middleware_callable = middleware(get_response)
        response = middleware_callable(request)
        return response

    return re_path(route, handler)
