
from bookstore.models import *
from django_instant_rest import patterns, casing
from ariadne import gql, QueryType, MutationType, make_executable_schema
from ariadne_django.views import GraphQLView
from django.urls import path

def lower(string):
    return string[0].lower() + string[1:]

def gql_primitive(field):
    field_type = type(field)
    if field_type == models.BigAutoField:
        return 'ID'
    elif field_type == models.ForeignKey:
        return field.related_model.__name__
    elif field_type == models.DateTimeField:
        return 'DateTime'
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
        self.name = set.rel.related_name if set.rel.related_name else set.rel.name
        self.typename = backwards_rel_type(set)


class GraphQLQueryType():
    def __init__(self, name = "", args = {}, output = ""):
        self.name = name
        self.args = args
        self.output = output

    def stringify(self):
        args = ", ".join([f"{k}: {v}" for k,v in self.args.items()])
        return f"{self.name}({args}): {self.output}"



class GraphQLModel():
    def __init__(self, model):
        self.name = model.__name__
        self.fields = [GraphQLField(f) for f in model._meta.fields]

        def is_rel(property_name):
            set = getattr(model, property_name, None)
            if not set:
                return False
            return bool(getattr(set, 'rel', None))

        backwards_rel_attrs = list(filter(lambda p: is_rel(p), dir(model)))
        backwards_rel_sets = [getattr(model, attr) for attr in backwards_rel_attrs]
        self.fields += [GraphQLBackwardsRel(set) for set in backwards_rel_sets]


    def stringify_type_def(self):
        gql_fields = [f"{f.name}: {f.typename}" for f in self.fields]
        newline = "\n    "

        return (f"type {self.name} {{\n" 
            f"    {newline.join(gql_fields)}\n"
            "}\n"
        )


    def query_types(self):
        return [
            GraphQLQueryType(
                name = lower(casing.camel(self.name)),
                args = { 'id': 'ID' },
                output = self.name,
            )
        ]




def type_defs(gql_models):
    type_def = "\n".join([ m.stringify_type_def() for m in gql_models ]) + "\n"
    indented_nl = "\n    "

    # Queries types
    query_types = []
    for m in gql_models:
        query_types += [qt.stringify() for qt in m.query_types()]

    type_def += ("type Query {\n" 
        f"    {indented_nl.join(query_types)}\n"
        "}\n"
    )

    return type_def


included_models = [Book, BookInventory, Author, StoreLocation, Employee]
gql_models = list(map(lambda m: GraphQLModel(m), included_models))
print(type_defs(gql_models))


# type_defs = gql("""
#     type Query {
#         books: [Book!]!
#     }

#     type Mutation {
#         createBook: Book!
#     }

#     type Book {
#         title: String!
#     }
# """)

# def list_books(*_):
#     return [{ "title": book.title } for book in Book.objects.all()]

# def create_book(*_, title):
#     book = Book.objects.create(titie=title)
#     return {"title": book.title}

# query = QueryType()
# query.set_field("books", list_books)

# mutation = MutationType()
# mutation.set_field("createBook", create_book)

# schema = make_executable_schema(type_defs, query, mutation)


urlpatterns = [
    # path("graphql/", GraphQLView.as_view(schema=schema)),
    patterns.resource('authors', Author),
    patterns.resource('books', Book),
    patterns.client('customers', Customer),
]