import pickle
import socket
try:
    import threading
except ImportError:
    import dummy_threading as threading

from messaging import ThreadingMixIn, BaseMessagingServer, BaseMessageReceiver, BaseMessagingClient, BaseMessageSender


class TCPMessagingServer(BaseMessagingServer):

    """TCP messaging server class."""

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    allow_reuse_address = False

    def __init__(self, address, process, bind_and_activate=True):
        BaseMessagingServer.__init__(self, address, process)
        self.socket = socket.socket(self.address_family, self.socket_type)
        if bind_and_activate:
            try:
                self.server_bind()
                self.server_activate()
            except:
                self.server_close()
                raise

    def server_bind(self):
        if self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.address)
        self.address = self.socket.getsockname()

    def server_activate(self):
        self.socket.listen(self.request_queue_size)

    def server_close(self):
        self.socket.close()

    def fileno(self):
        return self.socket.fileno()

    def get_request(self):
        return self.socket.accept()

    def finish_request(self, request, client_address):
        reply = self.process(pickle.loads(request.recv(self.max_packet_size)))
        if reply is not None:
            request.sendall(pickle.dumps(reply))

    def shutdown_request(self, request):
        try:
            request.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        self.close_request(request)

    def close_request(self, request):
        request.close()


class ThreadingTCPMessagingServer(ThreadingMixIn, TCPMessagingServer):

    """Treading TCP messaging server class."""

    pass


class TCPMessageReceiver(BaseMessageReceiver):

    """TCP message receiver class."""

    def __init__(self, address, process):
        self.__receiver = ThreadingTCPMessagingServer(address, process)
        self.address = self.__receiver.address
        receiver_thread = threading.Thread(target=self.__receiver.serve_forever)
        receiver_thread.daemon = True
        receiver_thread.start()

    def __del__(self):
        self.__receiver.shutdown()
        self.__receiver.server_close()


class TCPMessagingClient(BaseMessagingClient):

    """TCP messaging client class."""

    max_packet_size = 8192
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM

    def send(self, address, request):
        with socket.socket(self.address_family, self.socket_type) as client_socket:
            client_socket.connect(address)
            client_socket.sendall(pickle.dumps(request))

    def send_and_receive(self, address, request):
        with socket.socket(self.address_family, self.socket_type) as client_socket:
            client_socket.connect(address)
            client_socket.sendall(pickle.dumps(request))
            return pickle.loads(client_socket.recv(self.max_packet_size))


class TCPMessageSender(BaseMessageSender):

    """TCP message sender class."""

    __sender = TCPMessagingClient()

    def __init__(self, address):
        super().__init__(address)

    def send(self, request):
        self.__sender.send(self.address, request)

    def send_and_receive(self, request):
        return self.__sender.send_and_receive(self.address, request)
