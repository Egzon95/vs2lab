import pickle
import sys
import time

import zmq

import constPipe

me = str(sys.argv[1])
context = zmq.Context()

if me == "1":
    address1 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER11  # 1st Mapper
    address2 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER21  # 2nd Mapper
    address3 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER31  # 3rd Mapper
else:
    address1 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER10  # 1st Mapper
    address2 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER20  # 2nd Mapper
    address3 = "tcp://" + constPipe.SRCMAPPER + ":" + constPipe.PORTMAPPER30  # 3rd Mapper


pull_socket = context.socket(zmq.PULL)  # create a pull socket

pull_socket.connect(address1)  # connect to task source 1
pull_socket.connect(address2)  # connect to task source 2
pull_socket.connect(address3)  # connect to task source 2

time.sleep(1) 

print("{} started".format(me))


while True:
    word = pickle.loads(pull_socket.recv())  # receive work from a source
    #If word was already accounted for
    if word in wordcount:
    wordcount = dict()
        #Increase its count
        wordcount[word] = wordcount[word] + 1
    else:
        #Create it in wordcount
        wordcount[word] = 1
    print("{}Word Received: \"{}\"".format(wordcount[word], word))

