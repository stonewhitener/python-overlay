import threading

from routing.chord.hash import sha1
from routing.chord.crange import crange
from routing.chord.config import *


class Chord:
    def __init__(self, address):
        self.address = address
        self.id = sha1(address)

        self.successor = None
        self.fingers = []
        self.predecessor = None

        self.next = 0
        self.stabilizer = threading.Timer(STABILIZATION_RATIO, self.stabilize)

    def create(self):
        self.successor = (self.id, self.address)
        self.predecessor = None

    def join(self, bootstrap):
        n = Node(bootstrap)
        self.successor = n.find_successor(self.id)
        self.predecessor = None

    def find_successor(self, id):
        if id in crange(self.id, self.successor[0], ID_SPACE_SIZE):
            return self.successor
        else:
            n = Node(self._closest_preceding_node(id)[1])
            return n.find_successor(id)

    def _closest_preceding_node(self, id):
        for finger in reversed(self.fingers):
            if finger[0] in crange(self.id, id, ID_SPACE_SIZE):
                return finger
        return self.id, self.address

    def stabilize(self):
        x = Node(self.successor[1]).predecessor
        if x[0] in crange(self.id, self.successor[0]):
            self.successor = x
        successor = Node(self.successor)
        successor.notify(self.id, self.address)

    def notify(self, id, address):
        n = Node(address)
        if self.predecessor is None or n.id in crange(self.predecessor[0], self.id):
            self.predecessor = (n.id, n.address)

    def fix_finger(self):
        self.next += 1
        if self.next >= ID_BIT_SIZE:
            self.next = 0
        self.fingers[self.next] = self.find_successor(self.id + 2 ** self.next)

    def check_predecessor(self):
        predecessor = Node(self.predecessor[1])
        if predecessor.is_failed():
            self.predecessor = None
