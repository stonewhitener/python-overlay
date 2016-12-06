import random


N_NODE = 8


# create nodes
n = []
for _ in range(N_NODE):
    n.append(Node(transport=UDP, routing=Chord))

# create a new network
n[0].create()

# join the network with node 0
for i in range(1, N_NODE):
    n[i].join(n[random.randrange(i)])

# queries
for i in range(10000):
    n[random.randrange(N_NODE)].get('')
