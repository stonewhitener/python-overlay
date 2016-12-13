from rpc.client import ServerProxy


class BaseRouting:
    def create(self):
        pass

    def join(self, address):
        pass

    def lookup(self, key):
        pass


class BaseNode(ServerProxy):
    def __init__(self, address):
        super().__init__(address)
        self.__address = address

    @property
    def address(self):
        return self.__address

