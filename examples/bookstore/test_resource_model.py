
from django.test import TestCase
from .models import *

class ResourceModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(first_name="Stephen", last_name="King")

    def test2(self):
        self.assertEqual(1, 1)