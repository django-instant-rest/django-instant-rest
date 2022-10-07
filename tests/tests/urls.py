
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
        return 'ID'
    elif field_type == models.ForeignKey:
        return field.related_model.__name__
    elif field_type == models.DateTimeField:
        return 'String'
    elif field_type == models.CharField:
        return 'String'

    return 'String'

def backwards_rel_type(set):
    typename = set.rel.related_model.__name__
    return typename if not set.rel.multiple else f"[{typename}]"


class GraphQLField():
    def __init__(self, field):
        self.name = field.name
        self.typename = gql_primitive(field)

class GraphQLBackwardsRel():
    def __init__(self, set):
        self.name = set.rel.name
        self.typename = backwards_rel_type(set)


class GraphQLModel():
    def __init__(self, model):
        self.name = model.__name__
        self.fields = [GraphQLField(f) for f in model._meta.fields]

        backwards_rel_attrs = list(filter(lambda p: p.endswith('set'), dir(model)))
        backwards_rel_sets = [getattr(model, attr) for attr in backwards_rel_attrs]
        self.fields += [GraphQLBackwardsRel(set) for set in backwards_rel_sets]


    def stringify(self):
        gql_fields = [f"{f.name}: {f.typename}" for f in self.fields]
        newline = "\n    "

        return (f"type {self.name} {{\n" 
            f"    {newline.join(gql_fields)}\n"
            "}\n"
        )


included_models = [Book, Author]
gql_models = map(lambda m: GraphQLModel(m), included_models)
print("\n".join([ m.stringify() for m in gql_models ]))

# print(dir(Author.book_set.rel))
# print(Author.book_set.rel.name)
# print(Author.book_set.rel.related_model.__name__)
# print(Author.book_set.rel.many_to_many)
# print(Author.book_set.rel.many_to_one)
# print(Author.book_set.rel.one_to_one)
# print(Author.book_set.rel.one_to_many)
# print(Author.book_set.rel.multiple)

# print(dir(Author))

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