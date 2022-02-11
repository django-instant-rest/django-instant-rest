
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

    def test_get_requests_return_200(self):
        response = self.client.get('/authors')
        self.assertEqual(response.status_code, 200)

    def test_get_requests_return_model_instances(self):
        response = self.client.get('/authors')
        body = deserialize(response.content)
        self.assertEqual(len(body['data']), 3)

    def test_get_by_id_requests_return_model_instance_fields(self):
        response = self.client.get('/authors/2')
        self.assertEqual(response.status_code, 200)

        body = deserialize(response.content)
        author = body['data']

        self.assertIsNotNone(author['id'])
        self.assertEqual(author['first_name'], 'Agatha')
        self.assertEqual(author['last_name'], 'Christie')
        self.assertIsInstance(author['created_at'], str)
        self.assertIsInstance(author['updated_at'], str)

    # In the future, this should use better error (status codes and enum).
    # body['data'] should also be None
    def test_get_by_id_requests_return_errors_when_id_doesnt_exist(self):
        response = self.client.get('/authors/4')
        self.assertEqual(response.status_code, 200)

        body = deserialize(response.content)
        self.assertEqual(len(body['errors']), 1)

    def test_get_requests_return_model_instance_fields(self):
        response = self.client.get('/authors')
        self.assertEqual(response.status_code, 200)

        body = deserialize(response.content)
        author = body['data'][0]

        self.assertIsNotNone(author['id'])
        self.assertEqual(author['first_name'], 'Stephen')
        self.assertEqual(author['last_name'], 'King')
        self.assertIsInstance(author['created_at'], str)
        self.assertIsInstance(author['updated_at'], str)

    def test_get_requests_return_pagination_data(self):
        response = self.client.get('/authors')
        body = deserialize(response.content)
        self.assertIsInstance(body['first_cursor'], str)
        self.assertIsInstance(body['last_cursor'], str)
        self.assertIsInstance(body['has_next_page'], bool)

    def test_get_requests_respect_filter_params(self):
        response = self.client.get('/authors?first_name__startswith=A')
        body = deserialize(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body['data']), 2)

    def test_get_requests_respect_forward_pagination(self):
        response = self.client.get('/authors?first=1')
        body = deserialize(response.content)

        self.assertEqual(len(body['data']), 1)
        self.assertEqual(response.status_code, 200)

        author = body['data'][0]
        self.assertEqual(author['first_name'], 'Stephen')

        cursor = body['first_cursor']

        response = self.client.get('/authors?first=3&after=' + cursor)
        body = deserialize(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body['data']), 2)

        author = body['data'][0]
        self.assertEqual(author['first_name'], 'Agatha')

        author = body['data'][1]
        self.assertEqual(author['first_name'], 'Akira')

    def test_get_requests_respect_backward_pagination(self):
        response = self.client.get('/authors?last=1')
        body = deserialize(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body['data']), 1)

        author = body['data'][0]
        self.assertEqual(author['first_name'], 'Akira')

        cursor = body['first_cursor']

        response = self.client.get('/authors?last=3&before=' + cursor)
        body = deserialize(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body['data']), 2)

        author = body['data'][0]
        self.assertEqual(author['first_name'], 'Stephen')

        author = body['data'][1]
        self.assertEqual(author['first_name'], 'Agatha')

    def test_get_requests_respect_relational_filters(self):
        response = self.client.get('/books?author__first_name=Stephen')
        body = deserialize(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body['data']), 1)

    def test_post_requests_create_new_instances(self):
        response = self.client.post(
            '/authors',
            content_type = "application/json",
            data = { "first_name": "Tom", "last_name": "Clancy" },
        )

        self.assertEqual(response.status_code, 200)
        body = deserialize(response.content)
        author = body['data']

        self.assertIsNotNone(author['id'])
        self.assertEqual(author['first_name'], 'Tom')
        self.assertEqual(author['last_name'], 'Clancy')
        self.assertIsInstance(author['created_at'], str)
        self.assertIsInstance(author['updated_at'], str)

        actual_author = Author.objects.get(id=author['id'])
        self.assertEqual(actual_author.id, author['id'])
        self.assertEqual(actual_author.first_name, author['first_name'])
        self.assertEqual(actual_author.last_name, author['last_name'])

    def test_put_requests_update_existing_instances(self):
        response = self.client.put(
            '/books/1',
            content_type = "application/json",
            data = { "title": "IT" },
        )

        self.assertEqual(response.status_code, 200)
        body = deserialize(response.content)
        book = body['data']

        self.assertIsNotNone(book['id'])
        self.assertEqual(book['title'], 'IT')
        self.assertIsInstance(book['created_at'], str)
        self.assertIsInstance(book['updated_at'], str)

        actual_book = Book.objects.get(id=book['id'])
        self.assertEqual(actual_book.id, book['id'])
        self.assertEqual(actual_book.title, book['title'])

    # Should have non-200 status code and None for data in the future
    def test_put_requests_return_errors_when_id_doesnt_exist(self):
        response = self.client.put(
            '/books/4',
            content_type = "application/json",
            data = { "title": "IT" },
        )

        self.assertEqual(response.status_code, 200)
        body = deserialize(response.content)
        self.assertEqual(len(body['errors']), 1)

