# Django Instant Rest

The fastest production-ready REST tool for Python + Django! It allows you to quickly build RESTful APIs based on [Django Models](https://docs.djangoproject.com/en/3.1/topics/db/models/). Although not as configurable as [Django Rest Framework](https://www.django-rest-framework.org/) Django Instant Rest provides a fully featured API with enterprise-grade filtering and pagination in only a handful of lines. 


# Create Fully-Featured REST APIs Instantly
Simply define [Django Models](https://docs.djangoproject.com/en/3.1/topics/db/models/) for the data types you'd like to expose, and assign them a URL route:

```python
# models.py
from django_instant_rest.models import RestResource

class Author(RestResource):
    first_name = models.CharField(max_length=255, unique=True)
    last_name = models.CharField(max_length=255, null=False)

class Book(RestResource):
    title = models.CharField(max_length=255)
    synopsis = models.CharField(max_length= 1023)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

```

```python
# urls.py
from myapp.models import *
from django_instant_rest import patterns

urlpatterns = [
    patterns.resource('authors', Author),
    patterns.resource('books', Book),
]

```

# Enterprise Grade Filtering and Pagination
Out of the box, your REST API will have modern [cursor pagination system](https://dev.to/jackmarchant/offset-and-cursor-pagination-explained-b89), and complete access to [Django's powerful filtering system](https://docs.djangoproject.com/en/3.2/topics/db/queries/#retrieving-specific-objects-with-filters).

```json
// GET /authors?first_name__startswith=J&created_at__gte=2021-02-08

{
  "first_cursor": "MXwyMDIxLTAyLTA5IDIwOjI2OjU3LjkyODAwMCswMDowMA==",
  "last_cursor": "MXwyMDIxLTAyLTA5IDIwOjI2OjU3LjkyODAwMCswMDowMA==",
  "has_next_page": false,
  "data": [
    {
      "id": 1,
      "created_at": "2021-02-09T20:26:57.928000+00:00",
      "updated_at": "2021-02-09T20:26:57.928000+00:00",
      "first_name": "JK",
      "last_name": "Rowling"
    }
  ]
}
```


# Error Handling
All endpoints created with Django Instant Rest have a robust system of error handling.

When REST requests don't succeed, the JSON object in the response body will have a truthy `errors` property.

```json
{
    "errors": [
        {
            "field": "last_name",
            "message": "this field cannot be blank."
        },
        {
            "field": "first_name",
            "message": "author with this first name already exists."
        }
    ]
}
```

Each `error` object in the `errors` array will have a mandatory `message` property, and an optional `field` property, which associates the error with a field on the resource in question.

# Getting Started
If you're new to django-instant-rest, we recommend cloning and running the [starter template](https://github.com/django-instant-rest/starter-template)
