import selectors
import socket
import socketserver
import threading
from io import BytesIO


class BaseServer:
    def __init__(self, address):
        self.address = address
        self.__is_shutdown = threading.Event()
        self.__shutdown_request = False

    def serve_forever(self, poll_interval=0.5):
        self.__is_shutdown.clear()
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(self, selectors.EVENT_READ)
                while not self.__shutdown_request:
                    ready = selector.select(poll_interval)
                    if ready:
                        self._handle_request_noblock()
                    selector.service_actions()
        finally:
            self.__shutdown_request = False
            self.__is_shutdown.set()

    def _handle_request_noblock(self):
        request, client_address = self._get_request()
        if self._verify_request(request, client_address):
            try:
                self._process_request(request, client_address)
            except:
                self._handle_error(request, client_address)
                self._shutdown_request(request)
        else:
            self._shutdown_request(request)

    def _get_request(self):
        pass

    def _verify_request(self, request, client_address):
        """Verify the request.

        Return True if we should proceed with this request.

        """
        return True

    def _process_request(self, request, client_address):
        self._finish_request(request, client_address)
        self._shutdown_request(request)

    def _finish_request(self, request, client_address):
        pass

    def _shutdown_request(self, request):
        self._close_request(request)

    def _close_request(self, request):
        pass

    def _handle_error(self, request, client_address):
        print('-' * 40)
        print('Exception happened during processing of request from', end=' ')
        print(client_address)
        import traceback
        traceback.print_exc()  # XXX But this goes to stderr!
        print('-' * 40)

    def _handle_timeout(self):
        pass

    def shutdown(self):
        self.__shutdown_request = True
        self.__is_shutdown.wait()

    def close(self):
        pass


class TCPServer(BaseServer):
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    allow_reuse_address = False

    def __init__(self, address, bind_and_activate=True):
        super().__init__(address)
        self.socket = socket.socket(self.address_family, self.socket_type)

        if bind_and_activate:
            try:
                self.bind()
                self.listen()
            except:
                self.close()

    def bind(self):
        if self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.address)
        self.address = self.socket.getsockname()

    def listen(self):
        self.socket.listen(self.request_queue_size)

    def close(self):
        self.socket.close()

    def fileno(self):
        return self.socket.fileno()

    def _get_request(self):
        return self.socket.accept()

    def _shutdown_request(self, request):
        try:
            request.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        self._close_request(request)

    def _close_request(self, request):
        request.close()


class UDPServer(TCPServer):
    socket_type = socket.SOCK_DGRAM
    max_packet_size = 8192

    def listen(self):
        pass

    def _get_request(self):
        data, client_address = self.socket.recvfrom(self.max_packet_size)
        return BytesIO(data), client_address

    def _shutdown_request(self, request):
        self._close_request(request)

    def _close_request(self, request):
        pass
