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