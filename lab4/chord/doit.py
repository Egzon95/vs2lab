"""
Chord Application
- defines a DummyChordClient implementation
- sets up a ring of chord_node instances
- Starts up a DummyChordClient
- nodes and client run in separate processes
- multiprocessing should work on unix and windows
"""

import logging
import sys
import multiprocessing as mp

import chordnode as chord_node
import constChord
from context import lab_channel, lab_logging

import random
import math

lab_logging.setup(stream_level=logging.INFO)


class DummyChordClient:
    """A dummy client template with the channel boilerplate"""

    def __init__(self, channel):
        self.channel = channel
        self.node_id = channel.join('client')

    def enter(self):
        self.channel.bind(self.node_id)

    def run(self):
        print("Implement me pls...")
        self.channel.bind(self.node_id)
        destination = [random.choice(list(self.channel.channel.smembers('node'))).decode()]
        key = random.randint(0,60)
        smallestMatch = 100
        liste = list(map(int,{i.decode() for i in list(self.channel.channel.smembers('node'))}))
        print("IST KEY:", key)
        for num in liste:
            if num >= key:
                if num <= smallestMatch:
                    smallestMatch = num
                    print("JETZT IST SmallestMatch:", smallestMatch)
                print("vorherige Knoten war kleiner")
            print("key eh größer als knoten",num)
        print("Sending Request to:", destination, " for Key:", smallestMatch)
        self.channel.send_to(destination,(constChord.LOOKUP_REQ,smallestMatch))
        while True:
            message = self.channel.receive_from(destination)
            sender: str = message[0]  # Identify the sender
            request = message[1]  # And the actual request
            if request[0] == constChord.LOOKUP_REP:
                print("#########################################")
                print("Node ", request[1], " is responsible for ", key)
                self.channel.send_to({i.decode() for i in list(self.channel.channel.smembers('node'))}, constChord.STOP)
                break
        self.channel.send_to(  # a final multicast
            {i.decode() for i in list(self.channel.channel.smembers('node'))},
            constChord.STOP)


def create_and_run(num_bits, node_class, enter_bar, run_bar):
    """
    Create and run a node (server or client role)
    :param num_bits: address range of the channel
    :param node_class: class of node
    :param enter_bar: barrier syncing channel population
    :param run_bar: barrier syncing node creation
    """
    chan = lab_channel.Channel(n_bits=num_bits)
    node = node_class(chan)
    enter_bar.wait()  # wait for all nodes to join the channel
    node.enter()  # do what is needed to enter the ring
    run_bar.wait()  # wait for all nodes to finish entering
    node.run()  # start operating the node


if __name__ == "__main__":  # if script is started from command line
    m = 6  # Number of bits for linear names
    n = 8  # Number of nodes in the chord ring

    # Check for command line parameters m, n.
    if len(sys.argv) > 2:
        m = int(sys.argv[1])
        n = int(sys.argv[2])

    # Flush communication channel
    chan = lab_channel.Channel()
    chan.channel.flushall()

    # we need to spawn processes for support of windows
    mp.set_start_method('spawn')

    # create barriers to synchronize bootstrapping
    bar1 = mp.Barrier(n+1)  # Wait for channel population to complete
    bar2 = mp.Barrier(n+1)  # Wait for ring construction to complete

    # start n chord nodes in separate processes
    children = []
    for i in range(n):
        nodeproc = mp.Process(
            target=create_and_run,
            name="ChordNode-" + str(i),
            args=(m, chord_node.ChordNode, bar1, bar2))
        children.append(nodeproc)
        nodeproc.start()

    # spawn client proc and wait for it to finish
    clientproc = mp.Process(
        target=create_and_run,
        name="ChordClient",
        args=(m, DummyChordClient, bar1, bar2))
    clientproc.start()
    clientproc.join()

    # wait for node processes to finish
    for nodeproc in children:
        nodeproc.join()