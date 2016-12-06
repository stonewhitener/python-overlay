import hashlib
import pickle

from routing.chord.crange import crange
from routing.chord.config import *


def sha1(obj):
    return int(hashlib.sha1(pickle.dumps(obj)).hexdigest(), 16)


class Chord:
    def __init__(self, address):
        self.address = address
        self.id = sha1(self.address)

        self.successor = None
        self.finger = []
        self.predecessor = None

    def create(self):
        self.successor = (self.id, self.address)
        self.predecessor = None

    def join(self, address):
        n = object(address)
        self.successor = n.find_successor(self.id)
        self.predecessor = None

    def find_successor(self, id):
        if id in range(self.id, self.successor[0]):
            return self.successor
        else:
            n = object(self._closest_preceding_node(id)[1])
            return n.find_successor(id)

    def _closest_preceding_node(self, id):
        for i in range(start=N_FINGER - 1, stop=-1, step=-1):
            if self.finger[i] in crange(self.id, id):
                return self.finger[i]
        return self.id, self.address
