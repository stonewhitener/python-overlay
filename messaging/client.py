import socket


class TCPClient:
    address_family = socket.AF_INET

    socket_type = socket.SOCK_STREAM

    max_packet_size = 8192

    def __init__(self):
        pass

    def send(self, address, data):
        with socket.socket(self.address_family, self.socket_type) as client_socket:
            client_socket.connect(address)
            client_socket.sendall(data)

    def send_and_receive(self, address, data):
        with socket.socket(self.address_family, self.socket_type) as client_socket:
            client_socket.connect(address)
            client_socket.sendall(data)
            response = client_socket.recv(self.max_packet_size)
            return response


class UDPClient(TCPClient):
    socket_type = socket.SOCK_DGRAM
