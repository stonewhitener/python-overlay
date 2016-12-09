import pickle
import socket
from io import BytesIO


class StreamRequestSender:
    max_packet_size = 8192
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM

    def send_request(self, address, request):
        with socket.socket(self.address_family, self.socket_type) as client_socket:
            with client_socket.makefile('wb') as wfile:
                pickle.dump(request, wfile)
            with client_socket.makefile('rb') as rfile:
                response = pickle.load(rfile)
                return response


class DatagramRequestSender(StreamRequestSender):
    socket_type = socket.SOCK_DGRAM

    def send_request(self, address, request):
        with socket.socket(self.address_family, self.socket_type) as client_socket:
            with BytesIO() as wfile:
                pickle.dump(request, wfile)
                client_socket.sendto(wfile.getvalue(), address)
            data = client_socket.recv(self.max_packet_size)
            with BytesIO(data) as rfile:
                response = pickle.load(rfile)
                return response


class ServerProxy:
    def __init__(self, address, RequestSenderClass):
        self.__address = address
        self.__request_sender = RequestSenderClass()

    def __send(self, method, args):
        request = (method, args)
        response = self.__request_sender.send_request(self.__address, request)
        return response

    def __getattr__(self, name):
        return _Method(self.__send, name)


class _Method:
    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __getattr__(self, name):
        return _Method(self.__send, "{}.{}".format(self.__name, name))

    def __call__(self, *args):
        return self.__send(self.__name, args)


if __name__ == '__main__':
    s = ServerProxy(('127.0.0.1', 49152), DatagramRequestSender)
    print(s.pow(2, 160))
