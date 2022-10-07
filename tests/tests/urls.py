
from bookstore.models import *
from django_instant_rest import patterns
from ariadne import gql, QueryType, MutationType, make_executable_schema
from ariadne_django.views import GraphQLView
from django.urls import path



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