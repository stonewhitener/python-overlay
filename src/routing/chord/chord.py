import hashlib
import pickle
import random
import threading
import time

from routing.chord.config import *
from routing.chord.crange import crange
from routing.routing import BaseNode
from rpc.client import ServerProxy
from rpc.server import RPCServer, DatagramRPCRequestHandler


def sha1(obj):
    return int(hashlib.sha1(pickle.dumps(obj)).hexdigest(), 16)


class Node(BaseNode):
    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)


class Chord:
    def __init__(self, address):
        self.id = sha1(address)
        self.address = address

        self.successor = None
        self.fingers = []
        self.predecessor = None

        self.next = 0
        self.stabilizer = threading.Timer(STABILIZE_RATIO, self.stabilize)

    def create(self):
        self.successor = (self.id, self.address)
        self.predecessor = None

    def join(self, bootstrap):
        n = ServerProxy(bootstrap)
        self.successor = n.find_successor(self.id)
        self.predecessor = None

    def find_successor(self, id):
        if id in crange(self.id, self.successor[0], ID_SPACE_SIZE):
            return self.successor
        else:
            n = ServerProxy(self._closest_preceding_node(id))
            return n.find_successor(id)

    def _closest_preceding_node(self, id):
        for i in range(N_FINGERS - 1, -1, -1):
            if self.fingers[i][0] in crange(self.id, id, ID_SPACE_SIZE):
                return self.fingers[i]
        return self.id, self.address

    def stabilize(self):
        x = ServerProxy(ServerProxy(self.successor[1]).get_predecessor()[1])
        if x.get_id() in crange(self.id, self.successors[0], ID_SPACE_SIZE):
            self.successor = (x.get_id(), x.get_address())
        successor = ServerProxy(self.successor[1])
        successor.notify(self.address)

    def notify(self, address):
        n = ServerProxy(address)
        if self.predecessor is None or n.get_id() in crange(self.predecessor[0], self.id, ID_SPACE_SIZE):
            self.predecessor = (n.get_id(), n.get_address())

    def fix_finger(self):
        self.next += 1
        if self.next >= ID_BIT_SIZE:
            self.next = 0
        self.fingers[self.next] = self.find_successor(self.id + 2 ** self.next)

    def check_predecessor(self):
        predecessor = ServerProxy(self.predecessor[1])
        if predecessor.ping(self.id, self.address):
            self.predecessor = None
