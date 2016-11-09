import random

from messaging import BaseMessage
# from messaging.tcp import TCPMessageReceiver as MessageReceiver
# from messaging.tcp import TCPMessageSender as MessageSender
from messaging.udp import UDPMessageReceiver as MessageReceiver
from messaging.udp import UDPMessageSender as MessageSender


class RequestMessage(BaseMessage):
    def __init__(self, text):
        self.text = text


class ReplyMessage(BaseMessage):
    def __init__(self, text):
        self.text = text


class Local:
    def __init__(self, address):
        self.__receiver = MessageReceiver(address, self.process)
        self.address = self.__receiver.address

    def greet(self, address):
        remote = Remote(address)
        request = RequestMessage('Nice to meet you! I am ' + str(self.address))
        reply = remote.reply(request)
        print(reply.text)

    def process(self, request):
        reply = None

        if isinstance(request, RequestMessage):
            print(request.text)
            reply = ReplyMessage('Nice to meet you too! I am ' + str(self.address))

        return reply


class Remote:
    def __init__(self, address):
        self.__sender = MessageSender(address)
        self.address = self.__sender.address

    def reply(self, request):
        return self.__sender.send_and_receive(request)


def main():
    node = []

    for i in range(1000):
        n = Local(('127.0.0.1', 0))
        print("node #{} created at {}".format(i, n.address))
        node.append(n)

    for i in range(100):
        src = random.randrange(1000)
        dst = random.randrange(1000)
        node[src].greet(node[dst].address)


if __name__ == '__main__':
    main()
