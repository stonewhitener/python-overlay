import hashlib
import pickle
import random
import threading
import time

from routing.chord.config import *
from routing.chord.crange import crange
from rpc.client import ServerProxy
from rpc.server import RPCServer, DatagramRPCRequestHandler


def sha1(obj):
    return int(hashlib.sha1(pickle.dumps(obj)).hexdigest(), 16)


class Chord:
    def __init__(self, address):
        self.address = address
        self.id = sha1(self.address)

        self.successor = None
        self.finger = [None] * N_FINGER
        self.predecessor = None

        self.next = 0

        s = threading.Timer(STABILIZE_RATIO, self.stabilize)
        s.start()

    def get_address(self):
        return self.address

    def get_id(self):
        return self.id

    def get_successor(self):
        return self.successor

    def get_predecessor(self):
        return self.predecessor

    def create(self):
        self.successor = (self.id, self.address)
        self.finger = [(self.id, self.address)] * N_FINGER
        self.predecessor = None

    def join(self, bootstrap):
        n = ServerProxy(bootstrap)
        self.successor = n.find_successor(self.id)
        self.predecessor = None

    def find_successor(self, id):
        if id in crange(self.id, self.successor[0], ID_SPACE_SIZE):
            return self.successor
        else:
            n = ServerProxy(self._closest_preceding_node(id)[1])
            return n.find_successor(id)

    def _closest_preceding_node(self, id):
        for i in range(N_FINGER - 1, -1, -1):
            if self.finger[i][0] in crange(self.id, id, ID_SPACE_SIZE):
                return self.finger[i]
        return self.id, self.address

    def stabilize(self):
        x = ServerProxy(ServerProxy(self.successor[1]).get_predecessor()[1])
        if x.get_id() in crange(self.id, self.successor[0], ID_SPACE_SIZE):
            self.successor = (x.get_id(), x.get_address())
        successor = ServerProxy(self.successor[1])
        successor.notify(self.address)

    def notify(self, address):
        n = ServerProxy(address)
        if self.predecessor is None or n.get_id() in (self.predecessor[0], self.id):
            self.predecessor = (n.get_id(), n.get_address())

    def fix_finger(self):
        self.next += 1
        if self.next > ID_BIT_SIZE:
            self.next = 1
        self.finger[self.next] = self.find_successor(self.id + 2 ** (self.next - 1))

    def check_predecessor(self):
        predecessor = ServerProxy(self.predecessor[1])
        if predecessor.ping(self.id, self.address):
            self.predecessor = None

    def ping(self, id, address):
        return True

if __name__ == '__main__':
    class Node:
        def __init__(self, address):
            self.__server = RPCServer(address, DatagramRPCRequestHandler)
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

        def lookup(self, key):
            return self.__protocol.find_successor(sha1(key))


    N_NODE = 10

    n = []
    for i in range(N_NODE):
        n.append(Node(('127.0.0.1', 0)))

    # join the network with node 0
    for i in range(1, N_NODE):
        time.sleep(1.1)
        n[i].join(n[random.randrange(0, i)].address)

    time.sleep(10)

    # queries
    for i in range(10000):
        n[random.randrange(N_NODE)].lookup(random.randrange(0, 1000))
