import pickle
import socket





class ClientTransport:
    max_packet_size = 8192
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM

    def send_request(self, address, request):
        with socket.socket(self.address_family, self.socket_type) as client_socket:
            client_socket.connect(address)
            with client_socket.makefile('wb') as wfile:
                pickle.dump(request, wfile)
            with client_socket.makefile('rb') as rfile:
                response = pickle.load(rfile)
        return response
