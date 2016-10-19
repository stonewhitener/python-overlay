from messaging.service import MessageReceiver, MessageSender, BaseMessageHandler, BaseMessage


class RequestMessage(BaseMessage):
    def __init__(self, text):
        self.text = text


class ReplyMessage(BaseMessage):
    def __init__(self, text):
        self.text = text


class Local(BaseMessageHandler):
    def __init__(self, address):
        self.__receiver = MessageReceiver(address, self)
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
        self.__sender = MessageSender()
        self.address = address

    def reply(self, message):
        rep = self.__sender.send_and_receive(self.address, message)
        assert isinstance(rep, RequestMessage)
        return rep.text


if __name__ == '__main__':
    n1 = Local(('127.0.0.1', 0))
    n2 = Local(('127.0.0.1', 0))

    print('node created: ' + str(n1.address))
    print('node created: ' + str(n2.address))

    n1.request(n2.address)
    n1.request(n2.address)
    n1.request(n2.address)
    n1.request(n2.address)
    n1.request(n2.address)

    n2.request(n1.address)
    n2.request(n1.address)
    n2.request(n1.address)
    n2.request(n1.address)
    n2.request(n1.address)
