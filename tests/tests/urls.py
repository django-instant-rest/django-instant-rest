
import bookstore.models as resources
from inspect import getmembers, isclass
from django_instant_rest import patterns, casing
from django_instant_rest.models import RestResource
from ariadne import gql, QueryType, MutationType, ObjectType, make_executable_schema
from ariadne_django.views import GraphQLView
from django.urls import path
from django.db import models

int_fields = [
    models.IntegerField,
    models.SmallIntegerField,
    models.BigIntegerField,
    models.PositiveIntegerField,
    models.PositiveSmallIntegerField,
    models.PositiveBigIntegerField,
]

float_fields = [
    models.FloatField,
    models.DecimalField,
]

string_fields = [
    models.CharField,
    models.TextField,
    models.UUIDField,
]

def lower(string):
    return string[0].lower() + string[1:]

def gql_primitive(field, is_insertion = False):
    field_type = type(field)
    if field_type == models.BigAutoField:
        return 'ID'
    elif field_type in int_fields:
        return 'Int'
    elif field_type in float_fields:
        return 'Float'
    elif field_type in string_fields:
        return 'String'
    elif field_type == models.ForeignKey:
        return 'ID' if is_insertion else f"Single{field.related_model.__name__}Result"
    elif field_type == models.DateTimeField:
        return 'DateTime'

    return 'String'

def backwards_rel_type(set):
    typename = set.rel.related_model.__name__
    return typename if not set.rel.multiple else f"[{typename}]"


class GraphQLField():
    def __init__(self, field, is_insertion = False):
        self.name = field.name
        self.typename = gql_primitive(field, is_insertion)
        self.field = field

    def as_insertion(self):
        return GraphQLField(self.field, True)
    

class GraphQLInputField():
    def __init__(self, name, typename):
        self.name = name
        self.typename = typename
    

def get_many_args(typename):
    return {
        'filters': f'{typename}SearchFilters',
        'first': 'Int',
        'last': 'Int',
        'after': 'Cursor',
        'before': 'Cursor',
    }

class GraphQLBackwardsRel():
    def __init__(self, set):
        self.name = set.rel.related_name if set.rel.related_name else set.rel.name
        self.name = f"{self.name}List" if set.rel.multiple else self.name

        typename = set.rel.related_model.__name__
        self.typename = f"{typename}SearchResults" if set.rel.multiple else f"Single{typename}Result"

        self.args = { 'input': f"{typename}SearchCriteria" } if set.rel.multiple else {}
        self.set = set

    def stringify(self):
        args = ", ".join([f"{k}: {v}" for k,v in self.args.items()])
        return f"{self.name}({args}): {self.typename}"


class GraphQLQueryType():
    def __init__(self, name = "", args = {}, output = ""):
        self.name = name
        self.args = args
        self.output = output

    def stringify(self):
        args = ", ".join([f"{k}: {v}" for k,v in self.args.items()])
        return f"{self.name}({args}): {self.output}"


class GraphQLInputType():
    def __init__(self, name = "", fields = []):
        self.name = name
        self.fields = fields


    def stringify(self):
        gql_fields = [f"{f.name}: {f.typename}" for f in self.fields]
        newline = "\n    "

        return (f"input {self.name} {{\n" 
            f"    {newline.join(gql_fields)}\n"
            "}\n"
        )


class GraphQLModel():
    def __init__(self, model):
        self.name = model.__name__
        self.fields = [GraphQLField(f) for f in model._meta.fields]
        self.model = model

        def is_rel(property_name):
            set = getattr(model, property_name, None)
            if not set:
                return False
            return bool(getattr(set, 'rel', None))

        backwards_rel_attrs = list(filter(lambda p: is_rel(p), dir(model)))
        backwards_rel_sets = [getattr(model, attr) for attr in backwards_rel_attrs]
        self.rels = [GraphQLBackwardsRel(set) for set in backwards_rel_sets]


    def field_level_resolvers(self):
        obj_type = ObjectType(self.name)

        # TODO allow filtering and pagination on backwards relations
        for rel in self.rels:
            backward_field_name = rel.set.rel.field.name

            def resolver(obj, info, filters = {}):
                required_filters = { backward_field_name: obj.get('id') }
                filters = { **filters, **required_filters, }
                result = rel.set.rel.related_model.get_many(filters=filters)
                return result

            obj_type.set_field(rel.name, resolver)


        # Defining resolvers to populate owned relational fields
        for field in self.fields:

            if type(field.field) == models.ForeignKey:
                relation = getattr(self.model, field.name)

                def resolver(obj, info):
                    field_name  = field.name if field.name.endswith('id') else field.name + '_id'
                    id = obj.get(field_name, None)
                    result = relation.field.related_model.get_one(id = id)
                    return result

                obj_type.set_field(field.name, resolver)

        return obj_type


    def stringify_type_def(self):
        gql_fields = [f"{f.name}: {f.typename}" for f in self.fields]

        gql_rel_fields = [f.stringify() for f in self.rels]

        newline = "\n    "

        return (f"type {self.name} {{\n" 
            f"    {newline.join(gql_fields)}\n"
            f"    {newline.join(gql_rel_fields)}\n"
            "}\n"
        )


    def query_types(self):
        return [
            # Get One
            GraphQLQueryType(
                name = lower(casing.camel(self.name)),
                args = { 'id': 'ID' },
                output = f"Single{self.name}Result"
            ),
            # Get Many
            GraphQLQueryType(
                name = f"{lower(casing.camel(self.name))}List",
                args = { 'input': f'{self.name}SearchCriteria' },
                output = f"{self.name}SearchResults"
            )
        ]

    def mutation_types(self):
        return [
            # Create One
            GraphQLQueryType(
                name = "create" + casing.camel(self.name),
                args = { 'input': self.input_type().name },
                output = f"Single{self.name}Result"
            )
        ]


    def input_type(self):
        name = f"{self.name}Insertion"

        fields = []

        for f in self.fields:
            if f.name not in ['id', 'created_at', 'updated_at']:
                fields.append(f.as_insertion())

        return GraphQLInputType(name=name, fields=fields)


    def search_type(self):
        name = f"{self.name}SearchFilters"

        fields = []

        for f in self.fields:
            field_type = type(f.field)

            int_fields = [
                models.IntegerField,
                models.SmallIntegerField,
                models.BigIntegerField,
                models.PositiveIntegerField,
                models.PositiveSmallIntegerField,
                models.PositiveBigIntegerField,
            ]

            float_fields = [
                models.FloatField,
                models.DecimalField,
            ]

            string_fields = [
                models.CharField,
                models.TextField,
                models.UUIDField,
            ]

            if field_type == models.BigAutoField:
                fields.append(GraphQLInputField(f.name, 'ID'))
                fields.append(GraphQLInputField(f'{f.name}__in', '[ID]'))

            elif field_type == models.BooleanField:
                fields.append(GraphQLInputField(f.name, 'Boolean'))

            elif field_type == models.DateTimeField:
                fields.append(GraphQLInputField(f.name, 'DateTime'))
                fields.append(GraphQLInputField(f'{f.name}__gt', 'DateTime'))
                fields.append(GraphQLInputField(f'{f.name}__lt', 'DateTime'))
                fields.append(GraphQLInputField(f'{f.name}__gte', 'DateTime'))
                fields.append(GraphQLInputField(f'{f.name}__lte', 'DateTime'))
                fields.append(GraphQLInputField(f'{f.name}__in', '[DateTime]'))

            elif field_type in string_fields:
                fields.append(GraphQLInputField(f'{f.name}', 'String'))
                fields.append(GraphQLInputField(f'{f.name}__startswith', 'String'))
                fields.append(GraphQLInputField(f'{f.name}__endswith', 'String'))
                fields.append(GraphQLInputField(f'{f.name}__contains', 'String'))
                fields.append(GraphQLInputField(f'{f.name}__in', '[String]'))

            elif field_type in int_fields:
                fields.append(GraphQLInputField(f.name, 'Int'))
                fields.append(GraphQLInputField(f'{f.name}__gt', 'Int'))
                fields.append(GraphQLInputField(f'{f.name}__lt', 'Int'))
                fields.append(GraphQLInputField(f'{f.name}__gte', 'Int'))
                fields.append(GraphQLInputField(f'{f.name}__lte', 'Int'))
                fields.append(GraphQLInputField(f'{f.name}__in', '[Int]'))

            elif field_type in float_fields:
                fields.append(GraphQLInputField(f.name, 'Float'))
                fields.append(GraphQLInputField(f'{f.name}__gt', 'Float'))
                fields.append(GraphQLInputField(f'{f.name}__lt', 'Float'))
                fields.append(GraphQLInputField(f'{f.name}__gte', 'Float'))
                fields.append(GraphQLInputField(f'{f.name}__lte', 'Float'))
                fields.append(GraphQLInputField(f'{f.name}__in', '[Float]'))

        return GraphQLInputType(name=name, fields=fields)


    def query_resolvers(self):
        def get_one(obj, info, id = None):
            result = self.model.get_one(id=id)
            return result

        get_one_field = lower(casing.camel(self.name))

        # def get_many(obj, info, filters={}, first=None, last=None, after=None, before=None):
        def get_many(obj, info, input = {}):

            # TODO get selected fields. Will require drilling into field nodes
            # for n in info.field_nodes:
            #     payload = [s for s in n.selection_set.selections if s.name.value == 'payload'][0]
            #     nodes = [s for s in payload.selection_set.selections if s.name.value == 'nodes'][0]
            #     fields = [s.name.value for s in nodes.selection_set.selections]

            return self.model.get_many(**input)

            # return self.model.get_many(
            #     filters=filters,
            #     first=first,
            #     last=last,
            #     after=after,
            #     before=before
            # )

        get_many_field = f"{lower(casing.camel(self.name))}List"

        return {
            get_one_field: get_one,
            get_many_field: get_many,
        }

    def mutation_resolvers(self):
        def create_one(obj, info, input):
            return self.model.create_one(**input)

        create_one_field = "create" + casing.camel(self.name)

        return {
            create_one_field: create_one,
        }


def make_type_defs(gql_models):
    # adding base types
    type_def = (
        "scalar DateTime\n\n"
        "scalar Cursor\n\n"
        "type Error {\n"
        "    unique_name: String\n"
        "    message: String\n"
        "    is_internal: Boolean\n"
        "    _exception: String\n"
        "    _region: String\n"
        "}\n\n"
    )

    # Model Types
    type_def += "\n".join([ m.stringify_type_def() for m in gql_models ]) + "\n"
    indented_nl = "\n    "

    # Input Types
    type_def += "\n".join([ m.input_type().stringify() for m in gql_models ]) + "\n"
    type_def += "\n".join([ m.search_type().stringify() for m in gql_models ]) + "\n"

    # Queries types
    query_types = []
    for m in gql_models:
        query_types += [qt.stringify() for qt in m.query_types()]

    
    for m in gql_models:

        # Payload Types
        type_def += (
            f"type Single{m.name}Result {{\n"
            f"    payload: {m.name}\n"
            f"    errors: [Error]\n"
            "}\n\n"
        )

        type_def += (
            f"type {m.name}SearchResults {{\n"
            f"    payload: Paginated{m.name}List \n"
            f"    errors: [Error]\n"
            "}\n\n"
        )
        
        type_def += (
            f"type Paginated{m.name}List{{\n"
            f"    first_cursor: String\n"
            f"    last_cursor: String\n"
            f"    has_prev_page: Boolean\n"
            f"    has_next_page: Boolean\n"
            f"    nodes: [{m.name}]\n"
            "}\n\n"
        )

        type_def += (
            f"input {m.name}SearchCriteria {{\n"
            f"    filters: {m.name}SearchFilters \n"
            f"    first: Int\n"
            f"    last: Int\n"
            f"    before: Cursor\n"
            f"    after: Cursor\n"
            "}\n\n"
        )

    type_def += ("type Query {\n" 
        f"    {indented_nl.join(query_types)}\n"
        "}\n"
    )

    # Mutation types
    mutation_types = []
    for m in gql_models:
        mutation_types += [qt.stringify() for qt in m.mutation_types()]

    type_def += ("type Mutation {\n" 
        f"    {indented_nl.join(mutation_types)}\n"
        "}\n"
    )

    return type_def


included_models = [r for name, r in getmembers(resources) if isclass(r) and issubclass(r, RestResource) and r != RestResource]
gql_models = list(map(lambda m: GraphQLModel(m), included_models))
type_defs = make_type_defs(gql_models)
type_def_string = gql(type_defs)


query = QueryType()
mutation = MutationType()
other_resolvers = []

for m in gql_models:
    for field_name, resolver in m.query_resolvers().items():
        query.set_field(field_name, resolver)

    for field_name, resolver in m.mutation_resolvers().items():
        mutation.set_field(field_name, resolver)

    other_resolvers.append(m.field_level_resolvers())


schema = make_executable_schema(type_defs, query, mutation, other_resolvers)


urlpatterns = [
    path("graphql/", GraphQLView.as_view(schema=schema)),
    patterns.resource('authors', resources.Author),
    patterns.resource('books', resources.Book),
    patterns.client('customers', resources.Customer),
]