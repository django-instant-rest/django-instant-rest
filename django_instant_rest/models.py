from django.db import models
import datetime

class RestResource(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def to_dict(self):
        result = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)

            #handles datetime fields
            if type(value) == datetime.datetime:
                value = value.isoformat()

            #handles relational fields 
            if hasattr(value, "id"):
                value = value.id
            
            result[field.name] = value
        return result

