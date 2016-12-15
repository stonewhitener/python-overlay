class BaseMessage:
    pass


class RequestMessage(BaseMessage):
    def __init__(self, id, method, args):
        super().__init__()
        self.__id = id
        self.__method = method
        self.__args = args

    @property
    def id(self):
        return self.__id

    @property
    def method(self):
        return self.__method

    @property
    def args(self):
        return self.__args


class ResponseMessage(BaseMessage):
    def __init__(self, id, result):
        super().__init__()
        self.__id = id
        self.__result = result

    @property
    def id(self):
        return self.__id

    @property
    def result(self):
        return self.__result


class NotificationMessage(BaseMessage):
    def __init__(self, method, args):
        self.__method = method
        self.__args = args

    @property
    def method(self):
        return self.__method

    @property
    def args(self):
        return self.__args