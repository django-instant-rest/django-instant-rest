
import re

# "snake_case" -> "snakeCase" 
def camel(snake_str):
    return "".join(w.capitalize() if i else w for i, w in enumerate(snake_str.split("_")))

# "camelCase" -> "camel_case" 
def snake(camel_str):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

def camel_keys(dictionary):
    return { camel(key): value for (key, value) in dictionary.items() }

def snake_keys(dictionary):
    return { snake(key): value for (key, value) in dictionary.items() }

