from bot_app.BaseSetting import BaseSetting


class FlexibleBoolean(BaseSetting):
    boolean_true = ['true', '1', 't', 'y', 'yes', 'on']
    boolean_false = ['false', '0', 'f', 'n', 'no', 'off']

    def __init__(self, str_value="False", is_value=True):
        if self._is_boolean(str_value):
            if str_value.lower() in self.boolean_false:
                self.value = False
            elif str_value.lower() in self.boolean_true:
                self.value = True
        else:
            raise ValueError("Not a boolean.")
        self.is_value = is_value

    def _is_boolean(self, item):
        return item.lower() in self.boolean_true or item.lower() in self.boolean_false

    def __contains__(self, item):
        return str(item.get_value())

    def __str__(self):
        if self.is_value:
            return str(self.value)
        else:
            return "[True, False]"

    def get_value(self):
        if not self.is_value:
            return str(self.value)
        else:
            return self.value

