import socket
import transport.tcp

max_packet_size = 8192
address_family = socket.AF_INET
socket_type = socket.SOCK_DGRAM


def send(data: bytes, address):
    with socket.socket(address_family, socket_type) as client_socket:
        client_socket.sendto(data, address)
        return client_socket.recv(max_packet_size)


class Server(transport.tcp.Server):
    socket_type = socket.SOCK_DGRAM

    def activate(self):
        pass

    def _get_request(self):
        data, client_address = self.__socket.recvfrom(max_packet_size)
        return (data, self.__socket), client_address

    def _close_request(self, request):
        pass
