import pickle
import socket
from io import BytesIO


class ClientTransport:
    max_packet_size = 8192
    address_family = socket.AF_INET
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
