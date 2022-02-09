
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
        self.author = Author.objects.create(first_name="Agatha", last_name="Christie")
        self.author = Author.objects.create(first_name="Akira", last_name="Toriyama")

    def test_get_requests_return_200(self):
        request = self.factory.get('/authors')
        response = self.author_view.callback(request)
        self.assertEqual(response.status_code, 200)

    def test_get_requests_return_model_instances(self):
        request = self.factory.get('/authors')
        response = self.author_view.callback(request)
        body = json.loads(response.content)
        self.assertEqual(len(body['data']), 3)

    def test_get_requests_return_model_instance_fields(self):
        request = self.factory.get('/authors')
        response = self.author_view.callback(request)
        body = json.loads(response.content)

        author = body['data'][0]
        self.assertIsNotNone(author['id'])
        self.assertEqual(author['first_name'], 'Stephen')
        self.assertEqual(author['last_name'], 'King')
        self.assertIsInstance(author['created_at'], str)
        self.assertIsInstance(author['updated_at'], str)

    def test_get_requests_return_pagination_data(self):
        request = self.factory.get('/authors')
        response = self.author_view.callback(request)

        body = json.loads(response.content)
        self.assertIsInstance(body['first_cursor'], str)
        self.assertIsInstance(body['last_cursor'], str)
        self.assertIsInstance(body['has_next_page'], bool)
