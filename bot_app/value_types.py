from bot_app.BaseSetting import BaseSetting


class Range(BaseSetting):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __contains__(self, item):
        try:
            item = int(item)
        except ValueError:
            return False

        return self.a <= item and item <= self.b

    def __str__(self):
        return "[" + str(self.a) + "-" + str(self.b) + "]"

    def convert(self, value):
        return int(value)


class Boolean(BaseSetting):
    boolean_true = frozenset(['true', '1', 't', 'y', 'yes', 'on'])
    boolean_false = frozenset(['false', '0', 'f', 'n', 'no', 'off'])
    valid_values = frozenset(boolean_true | boolean_false)

    def __init__(self):
        pass

    def __contains__(self, item):
        return str(item).lower() in self.valid_values

    def __str__(self):
        return "[True, False]"

    def convert(self, value):
        if str(value).lower() in self.boolean_true:
            return True
        elif str(value).lower() in self.boolean_false:
            return False
        else:
            raise Exception("Value is not boolean: " + str(value))


class String(BaseSetting):
    def __init__(self, valid_values):
        self.valid_values = valid_values

    def __contains__(self, item):
        return item in self.valid_values

    def __str__(self):
        formatted_value = ["`" + value + "`" for value in self.valid_values]
        return "[" + (",".join(formatted_value)) + "]"
