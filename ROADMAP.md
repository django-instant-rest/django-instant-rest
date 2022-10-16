
# Roadmap
- Optimize performance of pagination metadata
- Test combinations of filtering and order_by
- Test interaction between pagination and order_by
- Consider solutions to cursor collisions
- Look at REST view functions, and use more appropriate errors for exceptions.
- Support non-integer IDs
- Maybe hide non-standard properties of the FAILED_UNEXPECTEDLY error.
- Support GraphQL
- Rename `RestResource` to `APIResource`
- Remove `RestClient` class.
- Support GraphQL Rate Limiting
- Support GraphQL Subscriptions
- Perhaps hide Django boilerplate
- Document Unsupported [Fields](https://docs.djangoproject.com/en/4.1/ref/models/fields/)
- Test that objects have consistent naming for foreign key fields for both get_one, and get_many.