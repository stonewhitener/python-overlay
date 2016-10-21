import hashlib
import pickle

from messaging import BaseMessageHandler
from messaging.tcp import TCPMessageReceiver, TCPMessageSender
from routing.chord.config import *
from routing.chord.message import *


def sha1(obj):
    return int(hashlib.sha1(pickle.dumps(obj)).hexdigest(), 16)


class Local(BaseMessageHandler):
    def __init__(self, address, remote_address=None):
        self.__receiver = TCPMessageReceiver(address, self)

        self.address = self.__receiver.address
        self.id = sha1(self.address)

        # init with self
        self.successors = [(self.id, self.address) for i in range(SUCCESSORS_SIZE)]
        self.predecessor = (self.id, self.address)
        # fill the fingers with self
        self.fingers = [(self.id, self.address) for i in range(FINGERS_SIZE)]

        # join the Chord network with the specified remote
        self.join(remote_address)

    @property.getter
    def successor(self):
        return self.successors[0]

    def join(self, remote_address):
        if remote_address:
            remote = Remote(remote_address)

    def find_successor(self, id):
        successor = self
        if successor.successor.id is successor.id:
            return successor
        while id not in range(successor.id, successor.successor.id):
            successor = successor.closest_preceding_finger(id)
        return successor


    def process(self, message):
        return None


class Remote(TCPMessageSender):
    def __init__(self, address):
        super().__init__(address)

    def find_successor(self, id):
        return self.send_and_receive(RequestFindSuccessorMessage(id))



if __name__ == '__main__':
    for i in range(100):
        Local(('127.0.0.1', 0))
