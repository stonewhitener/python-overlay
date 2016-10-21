import socket
try:
    import threading
except ImportError:
    import dummy_threading as threading

from messaging import ThreadingMixIn, BaseMessageReceiver
from messaging.tcp import TCPMessagingServer, TCPMessagingClient, TCPMessageSender


class UDPMessagingServer(TCPMessagingServer):

    """UDP messaging server class."""

    allow_reuse_address = False
    socket_type = socket.SOCK_DGRAM

    def get_request(self):
        data, client_address = self.socket.recvfrom(self.max_packet_size)
        return (data, self.socket), client_address

    def server_activate(self):
        pass

    def shutdown_request(self, request):
        self.close_request(request)

    def close_request(self, request):
        pass


class ThreadingUDPMessagingServer(ThreadingMixIn, UDPMessagingServer):

    """Threading UDP messaging server class."""

    pass


class UDPMessageReceiver(BaseMessageReceiver):

    """UDP message receiver class."""

    def __init__(self, address, handler):
        self.__receiver = ThreadingUDPMessagingServer(address, handler)
        self.address = self.__receiver.address
        receiver_thread = threading.Thread(target=self.__receiver.serve_forever)
        receiver_thread.daemon = True
        receiver_thread.start()

    def __del__(self):
        self.__receiver.shutdown()
        self.__receiver.server_close()


class UDPMessagingClient(TCPMessagingClient):

    """UDP messaging client class."""

    socket_type = socket.SOCK_DGRAM


class UDPMessageSender(TCPMessageSender):

    """UDP message sender class."""

    __sender = UDPMessagingClient()
