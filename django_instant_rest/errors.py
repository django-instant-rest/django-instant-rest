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


def FAILED_UNEXPECTEDLY(prefix = '', action = 'perform an unspecified task'):
    def handler(region = 'unknown', exception = None):
        print(f'Unexpected failure in region "{region}": {exception}')

        return {
            'unique_name': f"{prefix}FAILED_UNEXPECTEDLY",
            'message': 'Failed unexpectedly while attempting to {action}.',
            'is_internal': True,
        }
    return handler


GET_MANY_FAILED_UNEXPECTEDLY = FAILED_UNEXPECTEDLY('GET_MANY_', 'retrieve a list of object')
GET_ONE_FAILED_UNEXPECTEDLY = FAILED_UNEXPECTEDLY('GET_ONE_', 'retrieve a single object')
CREATE_ONE_FAILED_UNEXPECTEDLY = FAILED_UNEXPECTEDLY('CREATE_ONE_', 'store a new object')
UPDATE_ONE_FAILED_UNEXPECTEDLY = FAILED_UNEXPECTEDLY('UPDATE_ONE_', 'update an existing object')
DELETE_ONE_FAILED_UNEXPECTEDLY = FAILED_UNEXPECTEDLY('DELETE_ONE_', 'delete an existing object')


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
