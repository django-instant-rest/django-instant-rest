# Django Instant Rest

The fastest production-ready REST tool for Python + Django! It allows you to quickly build RESTful APIs based on [Django Models](https://docs.djangoproject.com/en/3.1/topics/db/models/). Although not as configurable as [Django Rest Framework](https://www.django-rest-framework.org/) Django Instant Rest provides a fully featured API with enterprise-grade filtering and pagination in only a handful of lines. 

If you're new to django-instant-rest, we recommend you check out our [starter template](https://github.com/django-instant-rest/starter-template)


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