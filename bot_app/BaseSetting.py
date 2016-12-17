from abc import ABC, abstractmethod


class BaseSetting(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def __contains__(self, item):
        pass

    def __str__(self):
        pass
