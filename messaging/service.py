import pickle
try:
    import threading
except ImportError:
    import dummy_threading as threading

from messaging.server import ThreadingTCPServer
from messaging.client import TCPClient


class BaseMessage:
    pass


class BaseMessageHandler:
    def process(self, message):
        pass


class MessageSender:
    def __init__(self):
        self.__sender = TCPClient()

    def send(self, address, message):
        self.__sender.send(address, pickle.dumps(message))

    def send_and_receive(self, address, message):
        return pickle.loads(self.__sender.send_and_receive(address, pickle.dumps(message)))


class MessageReceiver:
    def __init__(self, address, message_handler):
        self.__receiver = ThreadingTCPServer(address, message_handler)
        self.address = self.__receiver.server_address
        receiver_thread = threading.Thread(target=self.__receiver.serve_forever)
        receiver_thread.daemon = True
        receiver_thread.start()

    def __del__(self):
        self.__receiver.shutdown()
        self.__receiver.server_close()
