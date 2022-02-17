
from .models import Author, Book, Customer
from django_instant_rest.errors import *
from django_instant_rest.models import RestResource
from django.test import TestCase, tag
from django.db import models

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

    def test_get_many_wont_except_unclear_pagination_params(self):
        result = Author.get_many(first = 1, last = 1)
        self.assertIsNone(result['payload'])
        self.assertEqual(result['errors'], [PAGINATION_DIRECTION_UNCLEAR])

        result = Author.get_many(first = 1, before = 'MXwy')
        self.assertIsNone(result['payload'])
        self.assertEqual(result['errors'], [PAGINATION_DIRECTION_UNCLEAR])

        result = Author.get_many(last = 1, after = 'MXwy')
        self.assertIsNone(result['payload'])
        self.assertEqual(result['errors'], [PAGINATION_DIRECTION_UNCLEAR])

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

    def test_get_many_can_apply_cursor_field(self):
        result = Book.get_many(first = 2, pseudo_fields=['cursor'])
        self.assertEqual(len(result['payload']['nodes']), 2)

        for node in result['payload']['nodes']:
            self.assertIsInstance(node['cursor'], str)
            self.assertEqual(len(node), 6)

    def test_get_many_input_can_be_modified_by_hooks(self):
        def force_first_name_equals_agatha(**input):
            input['filters']['first_name'] = 'Agatha'
            return (input, None)

        Author.Hooks.before_get_many.append(force_first_name_equals_agatha)
        result = Author.get_many(filters = { "first_name": "Stephen" })
        Author.Hooks.before_get_many.clear()

        self.assertEqual(result['payload']['nodes'][0]['first_name'], 'Agatha')
        self.assertEqual(result['payload']['nodes'][0]['last_name'], 'Christie')

    def test_get_many_can_be_access_controlled_using_hooks(self):
        auth_error = {
            "message": "Failed to authenticate",
            "unique_name": "AUTHENTICATION_FAILED",
            "is_internal": False,
        }

        def fail_without_credentials(**input):
            credentials = input.get('credentials', None)
            return (input, None) if credentials else (input, [auth_error])

        Author.Hooks.before_get_many.append(fail_without_credentials)
        result_a = Author.get_many(credentials=True)
        result_b = Author.get_many()
        Author.Hooks.before_get_many.clear()

        self.assertEqual(result_a['errors'], [])
        self.assertEqual(result_b['errors'], [auth_error])
        self.assertEqual(result_b['payload'], None)

    def test_get_many_output_can_be_modified_by_hooks(self):
        def abbreviate_last_names(**output):
            try:
                for node in output['payload']['nodes']:
                    node['last_name'] = node['last_name'][0] + '.'
                return output
            except:
                return output

        Author.Hooks.after_get_many.append(abbreviate_last_names)
        result = Author.get_many()
        Author.Hooks.after_get_many.clear()

        self.assertEqual(len(result['payload']['nodes']), 3)
        for node in result['payload']['nodes']:
            self.assertEqual(len(node['last_name']), 2)

