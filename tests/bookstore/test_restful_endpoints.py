
from json import loads as deserialize
from django_instant_rest import patterns
from django.test import TestCase, Client
from .models import Author, Book, Customer


class ResourceModelTests(TestCase):
    @classmethod
    def setUpTestData(self):
        self.client = Client()

        stephen = Author.objects.create(first_name="Stephen", last_name="King")
        agatha = Author.objects.create(first_name="Agatha", last_name="Christie")
        akira = Author.objects.create(first_name="Akira", last_name="Toriyama")

        the_shining = Book.objects.create(title="The Shining", author=stephen)
        the_secret_adversary = Book.objects.create(title="The Secret Adversary", author=agatha)
        dragon_ball = Book.objects.create(title="Dragon Ball", author=akira)

    def get_req_body(self, path):
        """Helper fn to reduce duplicate code"""
        response = self.client.get(path)
        return deserialize(response.content)
    
    def test_get_requests_return_200(self):
        response = self.client.get('/authors')
        self.assertEqual(response.status_code, 200)

    def test_get_requests_return_model_instances(self):
        body = self.get_req_body('/authors')
        self.assertEqual(len(body['data']), 3)

    def test_get_requests_return_model_instance_fields(self):
        body = self.get_req_body('/authors')
        author = body['data'][0]
        self.assertIsNotNone(author['id'])
        self.assertEqual(author['first_name'], 'Stephen')
        self.assertEqual(author['last_name'], 'King')
        self.assertIsInstance(author['created_at'], str)
        self.assertIsInstance(author['updated_at'], str)

    def test_get_requests_return_pagination_data(self):
        body = self.get_req_body('/authors')
        self.assertIsInstance(body['first_cursor'], str)
        self.assertIsInstance(body['last_cursor'], str)
        self.assertIsInstance(body['has_next_page'], bool)

    def test_get_requests_respect_filter_params(self):
        body = self.get_req_body('/authors?first_name__startswith=A')
        self.assertEqual(len(body['data']), 2)

    def test_get_requests_respect_forward_pagination(self):
        body = self.get_req_body('/authors?first=1')
        self.assertEqual(len(body['data']), 1)

        author = body['data'][0]
        self.assertEqual(author['first_name'], 'Stephen')

        cursor = body['first_cursor']

        body = self.get_req_body('/authors?first=3&after=' + cursor)
        self.assertEqual(len(body['data']), 2)

        author = body['data'][0]
        self.assertEqual(author['first_name'], 'Agatha')

        author = body['data'][1]
        self.assertEqual(author['first_name'], 'Akira')

    def test_get_requests_respect_backward_pagination(self):
        body = self.get_req_body('/authors?last=1')
        self.assertEqual(len(body['data']), 1)

        author = body['data'][0]
        self.assertEqual(author['first_name'], 'Akira')

        cursor = body['first_cursor']

        body = self.get_req_body('/authors?last=3&before=' + cursor)
        self.assertEqual(len(body['data']), 2)

        author = body['data'][0]
        self.assertEqual(author['first_name'], 'Stephen')

        author = body['data'][1]
        self.assertEqual(author['first_name'], 'Agatha')

    def test_get_requests_respect_relational_filters(self):
        body = self.get_req_body('/books?author__first_name=Stephen')
        self.assertEqual(len(body['data']), 1)
