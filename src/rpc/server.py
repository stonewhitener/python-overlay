import pickle
import sys
from socketserver import StreamRequestHandler, DatagramRequestHandler, ThreadingTCPServer, ThreadingUDPServer


class RPCRequestHandler:
    def handle(self):
        print('requested from ' + str(self.client_address))
        method, args = pickle.load(self.rfile)
        response = self.server.dispatch(method, args)
        pickle.dump(response, self.wfile)


class StreamRPCRequestHandler(RPCRequestHandler, StreamRequestHandler):
    pass


class DatagramRPCRequestHandler(RPCRequestHandler, DatagramRequestHandler):
    pass


class RPCDispatcher:
    def __init__(self, instance=None):
        self.__instance = instance

    def register_instance(self, instance):
        self.__instance = instance

    def dispatch(self, method, args):
        _method = None
        if self.__instance is not None:
            try:
                _method = self._resolve_dotted_attribute(self.__instance, method)
            except AttributeError:
                pass
        if _method is not None:
            return _method(*args)
        else:
            raise Exception('method "{}" is not supported'.format(method))

    @staticmethod
    def _resolve_dotted_attribute(obj, dotted_attribute):
        attributes = dotted_attribute.split('.')
        for attribute in attributes:
            if attribute.startswith('_'):
                raise AttributeError('attempt to access private attribute "{}"'.format(attribute))
            else:
                obj = getattr(obj, attribute)
        return obj


class RPCServer(ThreadingUDPServer, RPCDispatcher):
    def __init__(self, server_address, RPCRequestHandlerClass, instance=None):
        ThreadingUDPServer.__init__(self, server_address, RPCRequestHandlerClass)
        RPCDispatcher.__init__(self, instance)


if __name__ == '__main__':
    class ExampleService:
        def pow(self, base, exp):
            return base ** exp


    s = RPCServer(('127.0.0.1', 49152), DatagramRPCRequestHandler, ExampleService())
    print('Serving Pickle-RPC on localhost port 49152')
    print('It is advisable to run this example server within a secure, closed network.')
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        s.server_close()
        sys.exit(0)
