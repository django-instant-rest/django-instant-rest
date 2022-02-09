
from django.test import TestCase
from django.test.client import RequestFactory
from django_instant_rest import patterns
from .models import *
import json

class ResourceModelTests(TestCase):
    @classmethod
    def setUpTestData(self):
        self.factory = RequestFactory()

        self.author_view = patterns.resource('authors', Author)
        self.book_view = patterns.resource('books', Book)
        self.customer_view = patterns.client('customers', Customer)

        self.author = Author.objects.create(first_name="Stephen", last_name="King")

    def test_can_get_resource(self):
        request = self.factory.get('/authors')
        response = self.author_view.callback(request)
        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        self.assertEqual(len(body['data']), 1)

        author = body['data'][0]
        self.assertEqual(author['first_name'], 'Stephen')
        self.assertEqual(author['last_name'], 'King')
