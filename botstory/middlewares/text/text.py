from ... import matchers


class Text:
    @matchers.matcher()
    class Any:
        """
        filter any raw text
        """
        type = 'text.any'

        def __init__(self):
            pass

        def validate(self, message):
            return message.get('text', {}).get('raw', None)

        def serialize(self):
            return None

        def deserialize(self, state):
            pass

    @matchers.matcher()
    class Match:
        type = 'text.match'

        def __init__(self, test_string):
            self.test_string = test_string

        def validate(self, message):
            return self.test_string == (message.get('text', {}).get('raw', None))

        def serialize(self):
            return self.test_string

        def deserialize(self, state):
            self.test_string = state
