
from django.test import TestCase
from .models import Author, Book, Customer
from json import dumps


class TestModelMethods(TestCase):
    @classmethod
    def setUpTestData(cls):
        stephen = Author.objects.create(first_name="Stephen", last_name="King")
        agatha = Author.objects.create(first_name="Agatha", last_name="Christie")
        akira = Author.objects.create(first_name="Akira", last_name="Toriyama")

        the_shining = Book.objects.create(title="The Shining", author=stephen)
        the_secret_adversary = Book.objects.create(title="The Secret Adversary", author=agatha)
        dragon_ball = Book.objects.create(title="Dragon Ball", author=akira)

    def test_get_many_can_apply_filters(self):
        result = Author.get_many(filters = { "first_name__startswith": "A" })
        self.assertEqual(len(result['payload']['nodes']), 2)
        self.assertEqual(len(result['errors']), 0)

    def test_get_many_can_apply_order_by(self):
        result = Author.get_many(order_by = ["first_name"])
        self.assertEqual(result['payload']['nodes'][0]['first_name'], "Agatha")
        self.assertEqual(len(result['errors']), 0)

    def test_get_many_can_apply_forward_pagination(self):
        result = Author.get_many(first = 2)
        self.assertEqual(result['payload']['has_next_page'], True)
        self.assertEqual(len(result['payload']['nodes']), 2)
        self.assertEqual(len(result['errors']), 0)

        last_cursor = result['payload']['last_cursor']
        self.assertIsInstance(last_cursor, str)

        result = Author.get_many(first = 2, after = last_cursor)
        self.assertEqual(result['payload']['has_next_page'], False)
        self.assertEqual(len(result['payload']['nodes']), 1)
        self.assertEqual(len(result['errors']), 0)


    def test_get_many_can_apply_backward_pagination(self):
        result = Author.get_many(last = 2)
        self.assertEqual(result['payload']['has_next_page'], False)
        self.assertEqual(result['payload']['has_prev_page'], True)
        self.assertEqual(len(result['payload']['nodes']), 2)
        self.assertEqual(len(result['errors']), 0)

        first_cursor = result['payload']['first_cursor']
        self.assertIsInstance(first_cursor, str)

        result = Author.get_many(last = 2, before = first_cursor)
        self.assertEqual(result['payload']['has_next_page'], True)
        self.assertEqual(result['payload']['has_prev_page'], False)
        self.assertEqual(len(result['payload']['nodes']), 1)
        self.assertEqual(len(result['errors']), 0)

    def test_get_many_can_apply_chosen_fields(self):
        result = Author.get_many(first = 2, fields=['first_name'])
        self.assertEqual(len(result['payload']['nodes']), 2)

        for node in result['payload']['nodes']:
            self.assertEqual(len(node), 1)

    def test_get_many_can_apply_cursor_pseudo_field(self):
        result = Author.get_many(first = 2, pseudo_fields=['cursor'])
        self.assertEqual(len(result['payload']['nodes']), 2)

        for node in result['payload']['nodes']:
            self.assertIsInstance(node['cursor'], str)
            self.assertEqual(len(node), 6)

