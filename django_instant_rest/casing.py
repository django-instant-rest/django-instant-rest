
import re

# "snake_case" -> "snakeCase" 
def camel(snake_str):
    return "".join(w.capitalize() if i else w for i, w in enumerate(snake_str.split("_")))

# "camelCase" -> "camel_case" 
def snake(camel_str):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()


def camel_keys(maybe_dict):
    if type(maybe_dict) == dict:
        return { camel(key): camel_keys(value) for (key, value) in maybe_dict.items() }
    if type(maybe_dict) == list:
        return [ camel_keys(item) for item  in maybe_dict ]
    else:
        return maybe_dict


def snake_keys(maybe_dict):
    if type(maybe_dict) == dict:
        return { snake(key): snake_keys(value) for (key, value) in maybe_dict.items() }
    if type(maybe_dict) == list:
        return [ snake_keys(item) for item  in maybe_dict ]
    else:
        return maybe_dict

