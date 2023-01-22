OBJECT_WITH_ID_DOES_NOT_EXIST = lambda id : {
    'unique_name': 'OBJECT_WITH_ID_DOES_NOT_EXIST',
    'message': f'Object with ID "{id}" does not exist',
    'is_internal': False,
}

DATABASE_INTEGRITY_VIOLATED = {
    'unique_name': 'DATABASE_INTEGRITY_VIOLATED',
    'message': "Database integrity has been violated",
    'is_internal': False,
}

INVALID_BEFORE_PARAMETER = {
    'unique_name': 'INVALID_BEFORE_PARAMETER',
    'message': "Expected parameter 'before' to be a base64 encoded string",
    'is_internal': False,
}

INVALID_AFTER_PARAMETER = {
    'unique_name': 'INVALID_AFTER_PARAMETER',
    'message': "Expected parameter 'after' to be a base64 encoded string",
    'is_internal': False,
}

INVALID_DATE_RECIEVED = lambda field_name : {
    'unique_name': 'INVALID_DATE_RECIEVED',
    'message': f'Received an invalid date for field "{field}"',
    'is_internal': False,
}


def FAILED_UNEXPECTEDLY( action = 'performing an unspecified task', region = 'UNSPECIFIED', exception = None):
    return {
        'unique_name': "FAILED_UNEXPECTEDLY",
        'message': f"Failed unexpectedly while {action}.",
        'is_internal': True,
        '_exception': str(exception),
        '_region': region,
    }


PAGINATION_FAILED_UNEXPECTEDLY = {
    'unique_name': 'PAGINATION_FAILED_UNEXPECTEDLY',
    'message': 'Failed unexpectedly while trying to paginate a list of objects',
    'is_internal': True,
}

PAGINATION_DIRECTION_UNCLEAR = {
    'unique_name': 'PAGINATION_DIRECTION_UNCLEAR',
    'message': 'Received too many or not enough pagination parameters.',
    'is_internal': False,
}

PAGINATION_CURSOR_INVALID = {
    'unique_name': 'PAGINATION_CURSOR_INVALID',
    'message': 'Expected `first` or `last` to be a base-64 encoded string.',
    'is_internal': False,
}

INVALID_JSON_RECEIVED = lambda e : {
    'unique_name': 'INVALID_JSON_RECEIVED',
    'message': e.msg,
    'is_internal': False,
}

INVALID_AUTH_ATTEMPT = lambda username_field, password_field : {
    'unique_name': 'INVALID_AUTH_ATTEMPT',
    'message': f'Expected a JSON object with "{username_field}" and "{password_field}" as keys',
    'is_internal': False,
}

INVALID_AUTHORIZATION_HEADER = {
    'unique_name': 'INVALID_AUTHORIZATION_HEADER',
    'message': 'The `Authorization` header value should be in the form of: `Bearer <INSERT_AUTH_TOKEN_HERE>`',
    'is_internal': False,
}

INCORRECT_AUTH_CREDENTIALS = {
    'unique_name': 'INCORRECT_AUTH_CREDENTIALS',
    'message': 'The authentication credentials were incorrect',
    'is_internal': False,
}

INVALID_AUTH_SIGNATURE = {
    'unique_name': 'INVALID_AUTH_SIGNATURE',
    'message': 'The provided auth token does not have a valid signature.',
    'is_internal': False,
}

NON_UNIQUE_USERNAME_FIELD = lambda model: {
    'unique_name': 'NON_UNIQUE_USERNAME_FIELD',
    'message': f'The {model.name} model is not set up correctly. The field {model.Auth.username_field} must be unique.',
    'is_internal': False,
}
