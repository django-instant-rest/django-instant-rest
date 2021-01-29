
from . import views
from django.urls import re_path


# Create a urlpattern element that allows CRUD
# operations for a given model. 
def resource(name, model, middleware = None):
    route = rf"^{name}/(?P<id>\d+)$|^{name}$"

    if not middleware:
        return re_path(route, views.resource(model))

    # Using a django-style middleware callable
    # if it was provided as a function parameter.
    # https://docs.djangoproject.com/en/3.1/topics/http/middleware/

    def handler(request, id = None):
        def get_response(request, id = id):
            return views.resource(model)(request, id)

        middleware_callable = middleware(get_response)
        response = middleware_callable(request, id = id)
        return response


    return re_path(route, handler)

