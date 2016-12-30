import socket
import transport.tcp
from transport import BaseRequestHandler

address_family = socket.AF_INET
socket_type = socket.SOCK_DGRAM
max_packet_size = 8192


def send(data, address):
    with socket.socket(address_family, socket_type) as client_socket:
        client_socket.sendto(data, address)
        return client_socket.recv(max_packet_size)


class Server(transport.tcp.Server):

    """UDP server class."""

    allow_reuse_address = False

    socket_type = socket.SOCK_DGRAM

    max_packet_size = 8192

    def get_request(self):
        data, client_addr = self.socket.recvfrom(self.max_packet_size)
        return (data, self.socket), client_addr

    def server_activate(self):
        # No need to call listen() for UDP.
        pass

    def shutdown_request(self, request):
        # No need to shutdown anything.
        self.close_request(request)

    def close_request(self, request):
        # No need to close anything.
        pass


class RequestHandler(BaseRequestHandler):

    """Define self.rfile and self.wfile for datagram sockets."""

    def setup(self):
        from io import BytesIO
        self.packet, self.socket = self.request
        self.rfile = BytesIO(self.packet)
        self.wfile = BytesIO()

    def finish(self):
        self.socket.sendto(self.wfile.getvalue(), self.client_address)
