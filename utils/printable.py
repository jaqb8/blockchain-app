from abc import ABC


class Printable(ABC):
    def __repr__(self):
        return str(self.__dict__)
