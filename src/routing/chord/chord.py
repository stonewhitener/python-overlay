import hashlib
import pickle

import sys
import threading
import time

from routing.chord.crange import crange
from routing.chord.config import *
from rpc.client import ServerProxy, DatagramRequestSender
from rpc.server import RPCServer


def sha1(obj):
    return int(hashlib.sha1(pickle.dumps(obj)).hexdigest(), 16)


class Chord:
    def __init__(self, address):
        self.address = address
        self.id = sha1(self.address)

        self.successor = None
        self.finger = [None] * N_FINGER
        self.predecessor = None

    def create(self):
        self.successor = (self.id, self.address)
        self.finger = [(self.id, self.address)] * N_FINGER
        self.predecessor = None

    def join(self, bootstrap):
        n = ServerProxy(bootstrap, DatagramRequestSender)
        self.successor = n.find_successor(self.id)
        self.predecessor = None
        print(self.successor)

    def find_successor(self, id):
        if id in crange(self.id, self.successor[0], ID_SPACE_SIZE):
            return self.successor
        else:
            n = ServerProxy(self._closest_preceding_node(id)[1], DatagramRequestSender)
            return n.find_successor(id)

    def _closest_preceding_node(self, id):
        for i in range(N_FINGER - 1, -1, -1):
            if self.finger[i][0] in crange(self.id, id, ID_SPACE_SIZE):
                return self.finger[i]
        return self.id, self.address


if __name__ == '__main__':
    class Node:
        def __init__(self, address):
            self.__server = RPCServer(address)
            self.__address = self.__server.server_address
            self.__protocol = Chord(self.__server.server_address)
            self.__server.register_instance(self.__protocol)

            print('Serving RPC on localhost port {}'.format(self.__server.server_address))
            print('It is advisable to run this example server within a secure, closed network.')

            self.__server_thread = threading.Thread(target=self.__server.serve_forever)
            self.__server_thread.daemon = True
            self.__server_thread.start()

        @property
        def address(self):
            return self.__address

        def create(self):
            self.__protocol.create()

        def join(self, bootstrap):
            self.__protocol.join(bootstrap)


    n0 = Node(('127.0.0.1', 0))
    n1 = Node(('127.0.0.1', 0))

    n0.create()
    n1.join(n0.address)

    time.sleep(2)
