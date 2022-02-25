
CREATE_ONE_FAILED_UNEXPECTEDLY = {
    'unique_name': 'CREATE_ONE_FAILED_UNEXPECTEDLY ',
    'message': 'Failed unexpectedly while trying to store a new object',
    'is_internal': True,
}

GET_MANY_FAILED_UNEXPECTEDLY = {
    'unique_name': 'GET_MANY_FAILED_UNEXPECTEDLY ',
    'message': 'Failed unexpectedly while trying to retrieve a list of objects',
    'is_internal': True,
}

PAGINATION_FAILED_UNEXPECTEDLY = {
    'unique_name': 'PAGINATION_FAILED_UNEXPECTEDLY ',
    'message': 'Failed unexpectedly while trying to paginate a list of objects',
    'is_internal': True,
}

PAGINATION_DIRECTION_UNCLEAR = {
    'unique_name': 'PAGINATION_DIRECTION_UNCLEAR',
    'message': 'Received too many or not enough pagination parameters.',
    'is_internal': False,
}

PAGINATION_CURSOR_INVALID = {
    'unique_name': 'PAGINATION_CURSOR_INVALID ',
    'message': 'Expected `first` or `last` to be a base-64 encoded string.',
    'is_internal': False,
}
