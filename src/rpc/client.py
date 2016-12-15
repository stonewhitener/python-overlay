import pickle
import socket
from io import BytesIO

from rpc.message import RequestMessage, ResponseMessage
from transport import tcp


class ServerProxy:
    def __init__(self, address, transport=tcp, timeout=None):
        self.__address = address
        self.__transport = transport.ClientTransport()
        self.__timeout = timeout

        self.__variables = self.__prefetch_variable_names()

    def __send_request(self, method, args):
        request = pickle.dumps(RequestMessage(0, method, args))
        response = pickle.loads(self.__transport.send_request(self.__address, request))
        if type(response) is ResponseMessage:
            return response.result

    def __prefetch_variable_names(self):
        return self.__send_request('prefetch', ())

    def __getattr__(self, name):
        if name in self.__variables:
            return self.__send_request('__getattribute__', name)
        else:
            return _Method(self.__send_request, name)


class _Method:
    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __call__(self, *args):
        return self.__send(self.__name, args)


if __name__ == '__main__':
    s = ServerProxy(('127.0.0.1', 49152))
    print(s.pow(2, 160))
