from messaging import BaseMessage


class RequestFindSuccessorMessage(BaseMessage):
    def __init__(self, id):
        self.id = id


class ReplyFindSuccessorMessage(BaseMessage):
    def __init__(self, id, address):
        self.id = id
        self.address = address
