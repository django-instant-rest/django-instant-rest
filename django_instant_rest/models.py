from argon2 import PasswordHasher
from django.db import models
import datetime

class RestResource(models.Model):
    '''Represents a data type that is exposed by a REST API'''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def to_dict(self):
        '''Convert model instances to dictionaries'''
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



class RestClient(models.Model):
    '''Represents a human or program that is a consumer of a REST API'''
    username = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=512)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        '''Saving the model instance, but first hashing the
        plaintext password stored in it's `password` field'''
        self.password = PasswordHasher().hash(self.password)
        super(RestClient, self).save(*args, **kwargs)

    def verify_password(self, password):
        '''Determine whether a given hashed password belongs
        to this model instance'''
        return PasswordHasher().verify(self.password, password)
