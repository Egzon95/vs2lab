import pickle
import random
import sys
import time

import zmq

import constPipe

src = constPipe.SRC1 # check line src host
prt = constPipe.PORT1 # check line src port

context = zmq.Context()
push_socket = context.socket(zmq.PUSH)  # create a push socket

address = "tcp://" + src + ":" + prt  # how and where to connect
push_socket.bind(address)  # bind socket to address

#Loading file
file = open('text.txt', 'r')
lines = file.readlines()
print("Lines splitted")


time.sleep(1)# wait to allow all Mappers to connect


count = 1
for line in lines:  # distribute the Lines
    print("Line{}: {}".format(count, line.strip()))
    push_socket.send(pickle.dumps(line))  #send workload to Mapper
    count = count + 1
