import multiprocessing

from messaging import BaseMessage, BaseMessageHandler
from messaging.tcp import TCPMessageReceiver, TCPMessageSender


class RequestMessage(BaseMessage):
    def __init__(self, text):
        self.text = text


class ReplyMessage(BaseMessage):
    def __init__(self, text):
        self.text = text


class Local(BaseMessageHandler):
    def __init__(self, address):
        self.__receiver = TCPMessageReceiver(address, self)
        self.address = self.__receiver.address

    def request(self, address):
        remote = Remote(address)
        text = remote.reply(RequestMessage('Nice to meet you! from ' + str(self.address)))
        print(text)

    def process(self, message):
        reply = None

        if isinstance(message, RequestMessage):
            print(message.text)
            reply = ReplyMessage('Nice to meet you too! from' + str(self.address))

        return reply


class Remote:
    def __init__(self, address):
        self.__sender = TCPMessageSender()
        self.address = address

    def reply(self, message):
        rep = self.__sender.send_and_receive(self.address, message)
        assert isinstance(rep, ReplyMessage)
        return rep.text


def invoke_node():
    n = Local(('127.0.0.1', 0))
    print('node created: ' + str(n.address))

if __name__ == '__main__':
    jobs = []
    for i in range(5000):
        p = multiprocessing.Process(target=invoke_node)
        jobs.append(p)
        p.start()
