import random


N_NODE = 1000


# create nodes
n = [Node(transport='UDP', routing='Chord') for _ in range(N_NODE)]

# create a new network
n[0].create()

# join the network with an existing node
for i in range(1, N_NODE):
    n[i].join(n[random.randrange(i)])

# queries
for i in range(10000):
    n[random.randrange(N_NODE)].get('')
