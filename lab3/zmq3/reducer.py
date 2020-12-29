import pickle
import sys
import time

import zmq

import constPipe

me = str(sys.argv[1])
context = zmq.Context()

if me == "1":
    address = "tcp://" + constPipe.SRCREDUCER + ":" + constPipe.PORTRED1
else:
    address = "tcp://" + constPipe.SRCREDUCER + ":" + constPipe.PORTRED0

bind_socket = context.socket(zmq.PULL)# create a pull socket
bind_socket.bind(address)

time.sleep(1) 

print("{} started".format(me))

wordcount = dict()

while True:
    word = pickle.loads(bind_socket.recv())  # receive work from a source
    #If word was already accounted for
    if word in wordcount:
        #Increase its count
        wordcount[word] = wordcount[word] + 1
    else:
        #Create it in wordcount
        wordcount[word] = 1
    print("{}. Time received: \"{}\"".format(wordcount[word], word))