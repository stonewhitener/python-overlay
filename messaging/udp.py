import pickle
import socket
try:
    import threading
except ImportError:
    import dummy_threading as threading

from messaging import ThreadingMixIn, BaseMessagingServer, BaseMessageReceiver, BaseMessagingClient, BaseMessageSender


class UDPMessagingServer(BaseMessagingServer):

    """UDP messaging server class."""

    address_family = socket.AF_INET
    socket_type = socket.SOCK_DGRAM
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
        pass

    def server_close(self):
        self.socket.close()

    def fileno(self):
        return self.socket.fileno()

    def get_request(self):
        data, client_address = self.socket.recvfrom(self.max_packet_size)
        return (data, self.socket), client_address

    def finish_request(self, request, client_address):
        reply = self.process(pickle.loads(request[0]))
        if reply is not None:
            request[1].sendto(pickle.dumps(reply), client_address)

    def shutdown_request(self, request):
        self.close_request(request)

    def close_request(self, request):
        pass


class ThreadingUDPMessagingServer(ThreadingMixIn, UDPMessagingServer):

    """Threading UDP messaging server class."""

    pass


class UDPMessageReceiver(BaseMessageReceiver):

    """UDP message receiver class."""

    def __init__(self, address, process):
        self.__receiver = ThreadingUDPMessagingServer(address, process)
        self.address = self.__receiver.address
        receiver_thread = threading.Thread(target=self.__receiver.serve_forever)
        receiver_thread.daemon = True
        receiver_thread.start()

    def __del__(self):
        self.__receiver.shutdown()
        self.__receiver.server_close()


class UDPMessagingClient(BaseMessagingClient):

    """TCP messaging client class."""

    max_packet_size = 8192
    address_family = socket.AF_INET
    socket_type = socket.SOCK_DGRAM

    def send(self, address, request):
        with socket.socket(self.address_family, self.socket_type) as client_socket:
            client_socket.sendto(pickle.dumps(request), address)

    def send_and_receive(self, address, request):
        with socket.socket(self.address_family, self.socket_type) as client_socket:
            client_socket.sendto(pickle.dumps(request), address)
            reply, address = client_socket.recvfrom(self.max_packet_size)
            return pickle.loads(reply)


class UDPMessageSender(BaseMessageSender):

    """UDP message sender class."""

    __sender = UDPMessagingClient()

    def __init__(self, address):
        super().__init__(address)

    def send(self, request):
        self.__sender.send(self.address, request)

    def send_and_receive(self, request):
        return self.__sender.send_and_receive(self.address, request)
