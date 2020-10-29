import logging
import socket

import constCS
from context import lab_logging

class Server:

    HEADER = 64
    GET_MESSAGE = "GET"
    GETALL_MESSAGE = "GETALL"
    DISCONNECT_MESSAGE = "!DISCONNECT"

    FORMAT = 'ascii'

    d = {"James": 235007, "Luke": 571708, "Holy": 839655, "Maria": 229351}


    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((constCS.HOST, constCS.PORT))
        self.s.settimeout(3)

        self.start()

        #self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.bind((constCS.HOST, constCS.PORT))
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        #self.sock.settimeout(3)  # time out in order not to block forever
        #self._logger.info("Server bound to socket " + str(self.sock))

    print("Hello, I am the Server")

    def start(self):
        print("[STARTING] starting the Server")
        self.s.listen(1)
        while True:
            try:
                print("\n[CONNECTING] looking for connection")
                (connection, address) = self.s.accept()  # returns new socket and address of client
                self.handle_client(connection, address)
            except socket.timeout:
                print("    [TIMEOUT] trying again")
                pass #ignore timeouts

    def handle_client(self, connection, address):
        print("[CLIENT] handling client")

        connected = True
        while connected:
            msg_type = connection.recv(HEADER).decode(FORMAT)
            if msg_type: #check if the message has any content. When you connect a blank message is sent, so this prevents erors
                #remove trailing whitespace
                msg_type = msg_type.replace(" ","") # eliminating appendet spaces
                if msg_type == GET_MESSAGE:
                    self.handle_get(connection)
                elif msg_type == GETALL_MESSAGE:
                    self.handle_getall(connection)
                elif msg_type == DISCONNECT_MESSAGE:
                    self.handle_disconnect(connection)
                    connected = False
                else:
                    print("Default -- something went wrong, received Type: " + msg_type + "END")
                    connected = False
        connection.close()
        print("[CLOSED] Connection has been closed")

    def handle_get(self, connection):
        print("    [GET] GET handler started")
        msg_length = connection.recv(HEADER).decode(FORMAT)
        msg_length = int(msg_length)
        print("        [MESSAGE_LENGTH] " + str(msg_length))
        msg = connection.recv(msg_length).decode(FORMAT)
        print("        [MESSAGE] " + msg)

        #Answer
        if msg in d:
            answer = str(d [msg])
        else:
            answer = "No Result"

        send_answer = answer.encode(FORMAT)
        answer_length = len(send_answer)
        send_length = str(answer_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length)) #Abbending bytes to match HEADER size

        #Sending#sending length
        connection.send(send_length)
        print("    [ANSWER_LENGTH] Sending the length: " + send_length.decode(FORMAT).replace(" ",""))
        #sending name
        connection.send(send_answer)
        print("    [ANSWER] Sending the Answer: " + send_answer.decode(FORMAT))


    def handle_getall(self, connection):
        print("    [GETALL] GETALL handler started")

        #Answer
        send_answer = str(d).encode(FORMAT)
        answer_length = len(send_answer)
        send_length = str(answer_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length)) #Abbending bytes to match HEADER size

        #Sending#sending length
        connection.send(send_length)
        print("    [ANSWER_LENGTH] Sending the length: " + send_length.decode(FORMAT).replace(" ",""))
        #sending name
        connection.send(send_answer)
        print("    [ANSWER] Sending the Answer: " + send_answer.decode(FORMAT))



    def handle_disconnect(self, connection):
        print("    [DISCONNECT] DISCONNECT handler started")
        print ("I'm done!")