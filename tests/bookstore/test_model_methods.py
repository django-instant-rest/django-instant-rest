
from django.test import TestCase
from .models import Author, Book, Customer


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
        self.assertEqual(len(result['payload']), 2)
        self.assertEqual(len(result['errors']), 0)

    def test_get_many_can_apply_order_by(self):
        result = Author.get_many(order_by = ["first_name"])
        self.assertEqual(result['payload'][0]['first_name'], "Agatha")
        self.assertEqual(len(result['errors']), 0)


