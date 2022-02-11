from base64 import b64decode, b64encode
from .errors import *

def encode_cursor(obj):
    '''
    Given a model instance, encode its id and created_at
    properties into a string, called a "cursor".
    '''
    field_strings = [str(obj.id), str(obj.created_at)]
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
    try:
        if first:
            if after is None:
                page_plus_one = queryset.all()[:first+1]
                page = page_plus_one[:first]
                return {
                    "page": page,
                    "has_next_page": len(page_plus_one) > len(page),
                    "error": None,
                }
            else:
                fields = decode_cursor(after)
                created_at = fields["created_at"]
                filtered_qs = queryset.filter(created_at__gt=created_at)
                page_plus_one = filtered_qs[:first+1]
                page = page_plus_one[:first]
                return {
                    "page": page,
                    "has_next_page": len(page_plus_one) > len(page),
                    "error": None,
                }
        elif last:
            if before is None:
                page_plus_one_index = max(0, len(queryset)-last-1)
                page_plus_one = queryset.all()[page_plus_one_index:]
                page = page_plus_one[len(page_plus_one)-last:]
                return {
                    "page": page,
                    "has_next_page": len(page_plus_one) > len(page),
                    "error": None,
                }
            else:
                fields = decode_cursor(before)
                created_at = fields["created_at"]
                filtered_qs = queryset.filter(created_at__lt=created_at)
                page = filtered_qs[max(0, len(filtered_qs)-last):]
                return {
                    "page": page,
                    "has_next_page": len(filtered_qs)-last >= 0,
                    "error": None,
                }
        else:
            return {
                "page": None,
                "has_next_page": False,
                "error": PAGINATION_MISSING_FIRST_OR_LAST,
            }
    except:
        return {
            "page": None,
            "has_next_page": False,
            "error": UNEXPECTEDLY_FAILED_TO_PAGINATE,
        }
