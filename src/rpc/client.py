import pickle
import socket
from io import BytesIO

from rpc.message import RequestMessage, ResponseMessage
from transport import tcp


class ServerProxy:
    def __init__(self, address, transport=tcp, timeout=None, **kwargs):
        self.address = address
        self.__transport = transport
        self.__timeout = timeout
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __send_request(self, method, args):
        request = pickle.dumps(RequestMessage(0, method, args))
        response = pickle.loads(self.__transport.send(request, self.address))
        if type(response) is ResponseMessage:
            return response.result

    def __getattr__(self, name):
        return _Method(self.__send_request, name)


class _Method:
    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __getattr__(self, name):
        return _Method(self.__send, '{}.{}'.format(self.__name, name))

    def __call__(self, *args):
        return self.__send(self.__name, args)


if __name__ == '__main__':
    s = ServerProxy(address=('127.0.0.1', 49152), id=123456789)
    print(s.address, s.id)
    print(s.pow(2, 160))
