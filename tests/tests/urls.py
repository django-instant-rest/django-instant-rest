
from bookstore.models import *
from django_instant_rest import patterns
from ariadne import gql, QueryType, MutationType, make_executable_schema
from ariadne_django.views import GraphQLView
from django.urls import path
from inspect import cleandoc
from textwrap import dedent


def gql_primitive(field):
    field_type = type(field)
    if field_type == models.BigAutoField:
        return 'Int'
    elif field_type == models.ForeignKey:
        return 'Int'
    elif field_type == models.DateTimeField:
        return 'String'
    elif field_type == models.CharField:
        return 'String'

    return 'String'


def model_as_gql_type_def(model):
    gql_fields = [f"{f.name}: {gql_primitive(f)}" for f in model._meta.fields]
    newline = "\n    "

    return (f"type {model.__name__} {{\n" 
        f"    {newline.join(gql_fields)}\n"
        "}\n"
    )




included_models = [Book, Author]
gql_model_types = "\n".join([model_as_gql_type_def(m) for m in included_models])
print(gql_model_types)


type_defs = gql("""
    type Query {
        books: [Book!]!
    }

    type Mutation {
        createBook: Book!
    }

    type Book {
        title: String!
    }
""")

def list_books(*_):
    return [{ "title": book.title } for book in Book.objects.all()]

def create_book(*_, title):
    book = Book.objects.create(titie=title)
    return {"title": book.title}

query = QueryType()
query.set_field("books", list_books)

mutation = MutationType()
mutation.set_field("createBook", create_book)

schema = make_executable_schema(type_defs, query, mutation)


urlpatterns = [
    path("graphql/", GraphQLView.as_view(schema=schema)),
    patterns.resource('authors', Author),
    patterns.resource('books', Book),
    patterns.client('customers', Customer),
]