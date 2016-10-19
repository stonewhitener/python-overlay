import pickle
import selectors
import socket
try:
    import threading
except ImportError:
    import dummy_threading as threading
from time import monotonic as time


if hasattr(selectors, 'PollSelector'):
    _ServerSelector = selectors.PollSelector
else:
    _ServerSelector = selectors.SelectSelector


class BaseMessage:

    """Base class for massages."""

    pass


class BaseMessageHandler:

    """Base class for message handlers."""

    def process(self, message):
        pass


class BaseMessagingServer:
    max_packet_size = 8192
    timeout = None

    def __init__(self, address, handler):
        self.address = address
        self.handler = handler
        self.__is_shut_down = threading.Event()
        self.__shutdown_request = False

    def server_activate(self):
        pass

    def serve_forever(self, poll_interval=0.5):
        self.__is_shut_down.clear()
        try:
            with _ServerSelector() as selector:
                selector.register(self, selectors.EVENT_READ)

                while not self.__shutdown_request:
                    ready = selector.select(poll_interval)
                    if ready:
                        self._handle_request_noblock()

                    self.service_actions()
        finally:
            self.__shutdown_request = False
            self.__is_shut_down.set()

    def shutdown(self):
        self.__shutdown_request = True
        self.__is_shut_down.wait()

    def service_actions(self):
        pass

    def handle_request(self):
        timeout = self.socket.gettimeout()
        if timeout is None:
            timeout = self.timeout
        elif self.timeout is not None:
            timeout = min(timeout, self.timeout)
        if timeout is not None:
            deadline = time() + timeout

        with _ServerSelector() as selector:
            selector.register(self, selectors.EVENT_READ)

            while True:
                ready = selector.select(timeout)
                if ready:
                    return self._handle_request_noblock()
                else:
                    if timeout is not None:
                        timeout = deadline - time()
                        if timeout < 0:
                            return self.handle_timeout()

    def _handle_request_noblock(self):
        try:
            request, client_address = self.get_request()
        except OSError:
            return
        if self.verify_request(request, client_address):
            try:
                self.process_request(request, client_address)
            except:
                self.handle_error(request, client_address)
                self.shutdown_request(request)
        else:
            self.shutdown_request(request)

    def handle_timeout(self):
        pass

    def verify_request(self, request, client_address):
        return True

    def process_request(self, request, client_address):
        self.finish_request(request, client_address)
        self.shutdown_request(request)

    def server_close(self):
        pass

    def finish_request(self, request, client_address):
        message = self.handler.process(pickle.loads(request.recv(self.max_packet_size)))
        if message is not None:
            request.sendall(pickle.dumps(message))

    def shutdown_request(self, request):
        self.close_request(request)

    def close_request(self, request):
        pass

    def handle_error(self, request, client_address):
        print('-'*40)
        print('Exception happened during processing of request from', end=' ')
        print(client_address)
        import traceback
        traceback.print_exc() # XXX But this goes to stderr!
        print('-'*40)


class ThreadingMixIn:
    daemon_threads = False

    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
        except:
            self.handle_error(request, client_address)
            self.shutdown_request(request)

    def process_request(self, request, client_address):
        t = threading.Thread(target = self.process_request_thread,
                             args = (request, client_address))
        t.daemon = self.daemon_threads
        t.start()


class TCPMessagingServer(BaseMessagingServer):

    """TCP messaging server class."""

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    allow_reuse_address = False

    def __init__(self, address, handler, bind_and_activate=True):
        BaseMessagingServer.__init__(self, address, handler)
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
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

    def shutdown_request(self, request):
        try:
            request.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        self.close_request(request)

    def close_request(self, request):
        request.close()


class UDPMessagingServer(TCPMessagingServer):

    """UDP messaging server class."""

    allow_reuse_address = False
    socket_type = socket.SOCK_DGRAM

    def get_request(self):
        data, client_addr = self.socket.recvfrom(self.max_packet_size)
        return (data, self.socket), client_addr

    def server_activate(self):
        pass

    def shutdown_request(self, request):
        self.close_request(request)

    def close_request(self, request):
        pass


class ThreadingTCPMessagingServer(ThreadingMixIn, TCPMessagingServer):

    """Treading TCP messaging server class."""

    pass


class ThreadingUDPMessagingServer(ThreadingMixIn, UDPMessagingServer):

    """Threading UDP messaging server class."""

    pass


class BaseMessageReceiver:
    pass


class TCPMessageReceiver(BaseMessageReceiver):

    """TCP message receiver class."""

    def __init__(self, address, handler):
        self.__receiver = ThreadingTCPMessagingServer(address, handler)
        self.address = self.__receiver.address
        receiver_thread = threading.Thread(target=self.__receiver.serve_forever)
        receiver_thread.daemon = True
        receiver_thread.start()

    def __del__(self):
        self.__receiver.shutdown()
        self.__receiver.server_close()


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


class BaseMessagingClient:
    def send(self, address, message):
        pass

    def send_and_receive(self, address, message):
        pass


class TCPMessagingClient(BaseMessagingClient):

    """TCP messaging client class."""

    max_packet_size = 8192
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM

    def send(self, address, message):
        client_socket = socket.socket(self.address_family, self.socket_type)
        client_socket.connect(address)
        client_socket.sendall(pickle.dumps(message))

    def send_and_receive(self, address, message):
        client_socket = socket.socket(self.address_family, self.socket_type)
        client_socket.connect(address)
        client_socket.sendall(pickle.dumps(message))
        return pickle.loads(client_socket.recv(self.max_packet_size))


class UDPMessagingClient(TCPMessagingClient):

    """UDP messaging client class."""

    socket_type = socket.SOCK_DGRAM


class BaseMessageSender:
    def send(self, address, message):
        pass

    def send_and_receive(self, address, message):
        pass


class TCPMessageSender(BaseMessageSender):

    """TCP message sender class."""

    __sender = TCPMessagingClient()

    def send(self, address, message):
        self.__sender.send(address, pickle.dumps(message))

    def send_and_receive(self, address, message):
        return self.__sender.send_and_receive(address, message)


class UDPMessageSender(TCPMessageSender):

    """UDP message sender class."""

    __sender = UDPMessagingClient()
