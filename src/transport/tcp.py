import socket

from transport.transport import BaseServer


address_family = socket.AF_INET
socket_type = socket.SOCK_STREAM
max_packet_size = 8192


def send(data: bytes, address) -> bytes:
    with socket.socket(address_family, socket_type) as client_socket:
        client_socket.connect(address)
        client_socket.sendall(data)
        return client_socket.recv(max_packet_size)


class Server(BaseServer):
    request_queue_size = 5
    allow_reuse_address = False

    def __init__(self, address, RequestHandlerClass, bind_and_activate=True):
        super().__init__(address, RequestHandlerClass)
        self.__socket = socket.socket(address_family, socket_type)
        if bind_and_activate:
            try:
                self.bind()
                self.activate()
            except:
                self.close()

    def bind(self):
        if self.allow_reuse_address:
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(self.__address)
        self.__address = self.__socket.getsockname()

    def activate(self):
        self.__socket.listen(self.request_queue_size)

    def close(self):
        self.__socket.close()

    def fileno(self):
        return self.__socket.fileno()

    def _get_request(self):
        client_socket, client_address = self.__socket.accept()
        data = client_socket.recv(max_packet_size)
        return (data, client_socket), client_address

    def _close_request(self, request):
        try:
            request.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        request[1].close()


if __name__ == '__main__':
    s = Server()