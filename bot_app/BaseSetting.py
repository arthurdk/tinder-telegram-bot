from abc import ABC, abstractmethod


class BaseSetting(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def __contains__(self, item):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def translate_value(self, value):
        return value

    def is_valid_value(self, value):
        return self.__contains__(value)