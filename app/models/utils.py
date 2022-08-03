from sqlalchemy.types import TypeDecorator, VARCHAR
import json


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

def all_nyse_symbols(location: str = "nyse-symbols-07-27-2022.txt"):
    try:
        with open(location) as file:
            symbols = []
            for line in file:
                symbols.append(line.rstrip())
        return symbols
    except:
        print(f'Error opening \"{location}\"')