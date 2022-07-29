from base64 import b64decode, b64encode
from binascii import Error as Base64Error
from copy import copy
from .errors import *

def encode_cursor(obj):
    '''
    Given a model instance, encode its id and created_at
    properties into a string, called a "cursor".
    '''
    id = obj['id'] if isinstance(obj, dict) else obj.id
    created_at = obj['created_at'] if isinstance(obj, dict) else obj.created_at
    field_strings = [ str(id), str(created_at) ]
    payload = '|'.join(field_strings)
    payload_bytes = payload.encode('utf8')
    cursor_bytes = b64encode(payload_bytes)
    cursor = cursor_bytes.decode('utf8')
    return cursor


def decode_cursor(cursor):
    '''
    Given a cursor string, return the `id` and `created_at`
    that it encodes.
    '''
    cursor_bytes = cursor.encode('utf8')
    payload_bytes = b64decode(cursor_bytes)
    payload = payload_bytes.decode('utf8')
    field_strings = payload.split('|')
    return {
        "id": field_strings[0],
        "created_at": field_strings[1],
    }

def paginate(queryset, first, last, after=None, before=None):
    if (not first and not last) or (first and last) or (after and before) or (first and before) or (last and after):
        return {
            "queryset": None,
            "has_next_page": False,
            "error": PAGINATION_DIRECTION_UNCLEAR,
        }

    try:
        if first:
            quantity = first
            if after is None:
                page_plus_one = queryset.all()[:first+1]
                page = page_plus_one[:first]
                return {
                    "queryset": page,
                    "has_prev_page": False,
                    "has_next_page": len(page_plus_one) > quantity,
                    "error": None,
                }
            else:
                fields = decode_cursor(after)
                page_plus_1 = queryset.filter(created_at__gt=fields['created_at']).all()[:quantity + 1]
                has_next_page = len(page_plus_1) > quantity
                has_prev_page = bool(len(queryset.filter(created_at__lt=fields['created_at'])))
                return {
                    "queryset": page_plus_1[:quantity],
                    "has_next_page": has_next_page,
                    "has_prev_page": has_prev_page,
                    "error": None,
                }
        elif last:
            quantity = last
            if before is None:
                index_before_first_page_element = max(0, len(queryset) - last - 1)
                page_plus_1 = queryset.all()[index_before_first_page_element:]
                page = page_plus_1[1:]
                return {
                    "queryset": page,
                    "has_next_page": False,
                    "has_prev_page": len(page_plus_1) > len(page),
                    "error": None,
                }
            else:
                fields = decode_cursor(before)
                created_at = fields["created_at"]
                all_before_cursor = queryset.filter(created_at__lt=created_at)
                index_before_first_page_element = max(0, len(all_before_cursor) - quantity - 1)
                page_plus_1 = all_before_cursor[index_before_first_page_element:]
                has_prev_page = len(page_plus_1) > quantity
                has_next_page = bool(queryset.filter(created_at__gt=created_at).first())
                return {
                    "queryset": page_plus_1 if not has_prev_page else page_plus_1[1:],
                    "has_next_page": has_next_page,
                    "has_prev_page": has_prev_page,
                    "error": None,
                }

        raise Exception('Unreachable!')

    except Base64Error as e:
        return {
            "queryset": None,
            "has_next_page": False,
            "error": PAGINATION_CURSOR_INVALID,
        }
    except Exception as e:
        raise e
        return {
            "queryset": None,
            "has_next_page": False,
            "error": PAGINATION_FAILED_UNEXPECTEDLY,
        }
