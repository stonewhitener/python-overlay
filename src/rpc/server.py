import pickle
import sys
from socketserver import StreamRequestHandler, DatagramRequestHandler, ThreadingTCPServer, ThreadingUDPServer

from rpc.message import RequestMessage, ResponseMessage, NotificationMessage


class RPCRequestHandler:
    def handle(self):
        request = pickle.load(self.rfile)
        if type(request) is RequestMessage:
            id, method, args = request.id, request.method, request.args
            result = self.server.dispatch(method, args)
            response = ResponseMessage(id, result)
            pickle.dump(response, self.wfile)
        if type(request) is NotificationMessage:
            method, args = request.method, request.args
            self.server.dispatch(method, args)


class StreamRPCRequestHandler(RPCRequestHandler, StreamRequestHandler):
    pass


class DatagramRPCRequestHandler(RPCRequestHandler, DatagramRequestHandler):
    pass


def _prefetch_variable_names(obj, name):
    attribute = _resolve_dotted_attribute(obj, name)
    variables = []
    if hasattr(attribute, '__dict__'):
        variables = [k for k in vars(attribute).keys() if not k.startswith('_')]
    return variables


def _resolve_dotted_attribute(obj, dotted_attribute):
    if dotted_attribute == 'self':
        return obj
    attributes = dotted_attribute.split('.')
    for attribute in attributes:
        obj = getattr(obj, attribute)
    return obj


class RPCDispatcher:
    def __init__(self, instance=None):
        self.__instance = instance

    def register_instance(self, instance):
        self.__instance = instance

    def dispatch(self, method, args):
        _method = None
        if self.__instance is not None:
            try:
                _method = _resolve_dotted_attribute(self.__instance, method)
            except AttributeError:
                pass
        if _method is not None:
            return _method(*args)
        else:
            raise Exception('method "{}" is not supported'.format(method))


class RPCServer(ThreadingTCPServer, RPCDispatcher):
    def __init__(self, server_address, instance=None):
        ThreadingTCPServer.__init__(self, server_address, StreamRPCRequestHandler)
        RPCDispatcher.__init__(self, instance)


if __name__ == '__main__':
    class ExampleService:
        def pow(self, base, exp):
            return base ** exp

    s = RPCServer(('127.0.0.1', 49152), ExampleService())
    print('Serving Pickle-RPC on localhost port 49152')
    print('It is advisable to run this example server within a secure, closed network.')
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        s.server_close()
        sys.exit(0)
