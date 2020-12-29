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


#Creating sockets for ditributing
addr0 = "tcp://" + constPipe.SRCREDUCER + ":" + constPipe.PORTRED0
con0 = context.socket(zmq.PUSH)
con0.connect(addr0)

addr1 = "tcp://" + constPipe.SRCREDUCER + ":" + constPipe.PORTRED1
con1 = context.socket(zmq.PUSH)
con1.connect(addr1)

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
            con0.send(pickle.dumps(word))
        else:
            con1.send(pickle.dumps(word))
        print("{} sent to Reducer{}".format(word, category))