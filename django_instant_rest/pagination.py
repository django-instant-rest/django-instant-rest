from base64 import b64decode, b64encode

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
    if first:
        if after is None:
            extended_page = queryset.all()[:first+1]
            page = extended_page[:first]
            return {
                "page": page,
                "has_next_page": len(extended_page) > len(page)
            }
        else:
            fields = decode_cursor(after)
            id = fields["id"]
            created_at = fields["created_at"]
            filtered_qs = queryset.filter(id__gt=id, created_at__gt=created_at)
            extended_page = filtered_qs[:first+1]
            page = extended_page[:first]
            return {
                "page": page,
                "has_next_page": len(extended_page) > len(page)
            }
    elif last:
        if before is None:
            extended_page_index = max(0, len(queryset)-last-1)
            extended_page = queryset.all()[extended_page_index:]
            page = extended_page[len(extended_page)-last:]
            return {
                "page": page,
                "has_next_page": len(extended_page) > len(page)
            }
        else:
            fields = decode_cursor(before)
            id = fields["id"]
            created_at = fields["created_at"]
            filtered_qs = queryset.filter(id__lt=id, created_at__lt=created_at)
            page = filtered_qs[max(0, len(filtered_qs)-last):]
            return {
                "page": page,
                "has_next_page": len(filtered_qs)-last >= 0
            }
    else:
        return queryset



