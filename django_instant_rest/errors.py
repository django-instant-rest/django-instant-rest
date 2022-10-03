OBJECT_WITH_ID_DOES_NOT_EXIST = lambda id : {
    'unique_name': 'OBJECT_WITH_ID_DOES_NOT_EXIST ',
    'message': f'Object with ID "{id}" does not exist',
    'is_internal': False,
}

DATABASE_CONSTRAINTS_VIOLATED = {
    'unique_name': 'DATABASE_CONSTRAINTS_VIOLATED',
    'message': "The data provided violates database constraints",
    'is_internal': False,
}

INVALID_BEFORE_PARAMETER = {
    'unique_name': 'INVALID_BEFORE_PARAMETER ',
    'message': "Expected parameter 'before' to be a base64 encoded string",
    'is_internal': False,
}

INVALID_AFTER_PARAMETER = {
    'unique_name': 'INVALID_AFTER_PARAMETER ',
    'message': "Expected parameter 'after' to be a base64 encoded string",
    'is_internal': False,
}

INVALID_DATE_RECIEVED = lambda field_name : {
    'unique_name': 'INVALID_DATE_RECIEVED ',
    'message': f'Received an invalid date for field "{field}"',
    'is_internal': False,
}

CREATE_ONE_FAILED_UNEXPECTEDLY = {
    'unique_name': 'CREATE_ONE_FAILED_UNEXPECTEDLY ',
    'message': 'Failed unexpectedly while trying to store a new object',
    'is_internal': True,
}

DELETE_ONE_FAILED_UNEXPECTEDLY = {
    'unique_name': 'DELETE_ONE_FAILED_UNEXPECTEDLY ',
    'message': 'Failed unexpectedly while trying to delete an object',
    'is_internal': True,
}

GET_ONE_FAILED_UNEXPECTEDLY = {
    'unique_name': 'GET_ONE_FAILED_UNEXPECTEDLY ',
    'message': 'Failed unexpectedly while trying to retrieve an object',
    'is_internal': True,
}

def GET_MANY_FAILED_UNEXPECTEDLY(region = 'unknown', exception = None):
    print(f'Unexpected failure in region "{region}": {exception}')

    return {
        'unique_name': 'GET_MANY_FAILED_UNEXPECTEDLY ',
        'message': 'Failed unexpectedly while trying to retrieve a list of objects.',
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
