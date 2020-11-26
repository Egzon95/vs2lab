import pickle
import sys
import time

import zmq

import constPipe

reducerCount = 2
me = str(sys.argv[1])

#Pull Socket for receiving
address1 = "tcp://" + constPipe.SRC1 + ":" + constPipe.PORT1  # line src

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  # create a pull socket

pull_socket.connect(address1)  # connect to task source 1

#Push Sockets for distributing
#Choose push Adress
if me == "1":
    address2 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER10  # reducer0
    address3 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER11  # reducer1
    print("ME1 " + address2)
elif me == "2":
    address2 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER20  # reducer0
    address3 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER21  # reducer1
    print("ME2 " + address2)
else:
    address2 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER30  # reducer0
    address3 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER31  # reducer1

#Creating sockets
push0 = context.socket(zmq.PUSH)
push0.bind(address2)
push1 = context.socket(zmq.PUSH)
push1.bind(address3)

#Waiting
time.sleep(1) 

print("{} started".format(me))

#Receiving Lines
while True:
    line = pickle.loads(pull_socket.recv())  # receive work from a source
    print("\n{} received line: \"{}\"".format(me, line[:-1]))
    print("Splitting the words: ")
    #Splitting lines
    words = line.split()
    #Distributing Words
    for word in words:
        category = len(word) % reducerCount #Calculating category for the word
        if category == 0:
            push0.send(pickle.dumps(word))
        else:
            push1.send(pickle.dumps(word))
        print("{} sent to Reducer{}".format(word, category))