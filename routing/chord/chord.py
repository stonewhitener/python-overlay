import hashlib
import pickle

from routing.chord.config import *
from routing.chord.message import *


def sha1(obj):
    return int(hashlib.sha1(pickle.dumps(obj)).hexdigest(), 16)


class Chord:
    def __init__(self, address, remote_address=None):
        self.address = address
        self.id = sha1(self.address)

        # init with self
        self.successors = [(self.id, self.address) for i in range(SUCCESSORS_SIZE)]
        self.predecessor = (self.id, self.address)
        # fill the fingers with self
        self.fingers = [(self.id, self.address) for i in range(FINGERS_SIZE)]

        # join the Chord network with the specified remote
        self.join(remote_address)

    def join(self, remote_address):
        pass

    def process(self, request):
        pass
