
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django_instant_rest.models import RestResource, RestClient
from tests import settings

# class Author(RestResource):
#     full_name = models.CharField(max_length=255)

# class Image(RestResource):
#     width = models.PositiveIntegerField()
#     height = models.PositiveIntegerField()
#     filename = models.CharField(max_length=1047)
#     description = models.CharField(max_length=1047)
#     caption = models.CharField(max_length=1047, null=True, blank=True)

# class Article(RestResource):
#     title = models.CharField(max_length=255)
#     teaser_text = models.CharField(max_length=1047)
#     is_published = models.BooleanField(default=False)
#     thumbnail_image = models.ForeignKey(Image, on_delete=models.CASCADE)

# class ArticleAuthorship(RestResource):
#     author = models.ForeignKey(Author, on_delete=models.CASCADE)
#     article = models.ForeignKey(Article, on_delete=models.CASCADE)

# class Topic(RestResource):
#     name = models.CharField(max_length=255)

# class ArticleTopic(RestResource):
#     article = models.ForeignKey(Article, on_delete=models.CASCADE)
#     topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


# class RichTextTitle(RestResource):
#     fractional_index = models.FloatField(default=0.0, blank=True)
#     text = models.CharField(max_length=255)
#     size = models.IntegerField(
#         validators=[MinValueValidator(1), MaxValueValidator(6)],
#         default=1,
#     )


# class RichTextBlock(RestResource):
#     """Represents a paragraph made up of multiple rich text spans"""
#     locked = models.BooleanField(default=False)

# class RichTextSpan(RestResource):
#     quote = models.BooleanField(default=False)
#     strong = models.BooleanField(default=False)
#     emphasis = models.BooleanField(default=False)
#     href = models.CharField(max_length=1047, null=True, blank=True)
#     text = models.CharField(max_length=1047)

# class ImagePosition(RestResource):
#     fractional_index = models.FloatField(default=0.0, blank=True)
#     image = models.ForeignKey(Image, on_delete=models.CASCADE)
#     article = models.ForeignKey(Article, on_delete=models.CASCADE)

# class RichTextTitlePosition(RestResource):
#     fractional_index = models.FloatField(default=0.0, blank=True)
#     rich_text_title = models.ForeignKey(Image, on_delete=models.CASCADE)
#     article = models.ForeignKey(Article, on_delete=models.CASCADE)

# class RichTextSpanPosition(RestResource):
#     """The position of a span within a rich text block"""
#     fractional_index = models.FloatField(default=0.0, blank=True)
#     rich_text_block = models.ForeignKey(RichTextBlock, on_delete=models.CASCADE)
#     rich_text_span = models.ForeignKey(RichTextSpan, on_delete=models.CASCADE)

# class RichTextBlockPosition(RestResource):
#     fractional_index = models.FloatField(default=0.0, blank=True)
#     rich_text_block = models.ForeignKey(RichTextBlock, on_delete=models.CASCADE)
#     article = models.ForeignKey(Article, on_delete=models.CASCADE)


class Author(RestResource):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

class Book(RestResource):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

class InventoryLocation(RestResource):
    street_address = models.CharField(max_length=255)
    state_or_province = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

class BookInventory(RestResource):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="inventory")
    location = models.ForeignKey(InventoryLocation, on_delete=models.CASCADE, related_name="inventory")
    quantity: models.PositiveIntegerField()

class Employee(RestResource):
    location = models.ForeignKey(InventoryLocation, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

class Customer(RestResource, RestClient):
    '''All models that inherit from `RestClient` will have a `username`
    and `password` field by default.'''

    email = models.CharField(max_length=127)
    phone = models.CharField(max_length=63)

    class Hashing:
        '''Providing a secret value for encoding and decoding passwords.
        This should never be hard-coded when running in production.'''
        secret_key = settings.SECRET_KEY

    class Serializer:
        '''Listing fields that should be hidden from API consumers'''
        hidden_fields = ['password']
