import pickle
import xmlrpc.client, xmlrpc.server
from typing import Generic, TypeVar
from socketserver import *


class RPCRequestHandlingMixIn:
    def handle(self):
        request = pickle.load(self.rfile)
        response = self.server.dispatch(request)
        pickle.dump(response, self.wfile)


class StreamRPCRequestHandler(RPCRequestHandlingMixIn, StreamRequestHandler):
    pass


class DatagramRPCRequestHandler(RPCRequestHandlingMixIn, DatagramRequestHandler):
    pass


class RPCDispatcher:
    def __init__(self, instance):
        self.__instance = instance

    @staticmethod
    def resolve_dotted_attribute(obj, dotted_attribute):
        attributes = dotted_attribute.split('.')
        for attribute in attributes:
            if attribute.startwith('_'):
                raise AttributeError('attempt to access private attribute "{}"'.format(attribute))
            else:
                obj = getattr(obj, attribute)
        return obj

    def dispatch(self, method, args):
        _method = None
        if self.__instance is not None:
            try:
                _method = self.resolve_dotted_attribute(self.__instance, method)
            except AttributeError:
                pass
        if _method is not None:
            return _method(*args)
        else:
            raise Exception('method "%s" is not supported'.format(method))


S = TypeVar('S', ThreadingTCPServer, ThreadingUDPServer)
H = TypeVar('H', StreamRequestHandler, DatagramRPCRequestHandler)


class BaseRPCServer(Generic[S, H], RPCDispatcher):
    def __init__(self, server_address, service):
        S.__init__(self, server_address, H)
        RPCDispatcher.__init__(self, service)
