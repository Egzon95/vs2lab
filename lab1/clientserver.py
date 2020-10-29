import socket
import constCS

import random
import string

class Protocol:
    HEADER = 64
    GET_MESSAGE = "GET"
    GETALL_MESSAGE = "GETALL"
    DISCONNECT_MESSAGE = "!DISCONNECT"

    FORMAT = 'ascii'

class Server:


    d = {"James": 235007, "Luke": 571708, "Holy": 839655, "Maria": 229351, "Noah": 123456, "Egzon": 666666, "Yannik": 180546, "Julian": 555555}

    i = 1
    while i <= 500:
        n = ''.join(random.choice(string.ascii_lowercase) for i in range(12))
        d[n] = i
        i += 1



    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((constCS.HOST, constCS.PORT))
        self.s.settimeout(3)

        print("Hello, I am the Server")


    def serve(self):
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
            msg_type = connection.recv(Protocol.HEADER).decode(Protocol.FORMAT)
            if msg_type: #check if the message has any content. When you connect a blank message is sent, so this prevents erors
                #remove trailing whitespace
                msg_type = msg_type.replace(" ","") # eliminating appendet spaces
                if msg_type == Protocol.GET_MESSAGE:
                    self.handle_get(connection)
                elif msg_type == Protocol.GETALL_MESSAGE:
                    self.handle_getall(connection)
                elif msg_type == Protocol.DISCONNECT_MESSAGE:
                    self.handle_disconnect(connection)
                    connected = False
                else:
                    print("Default -- something went wrong, received Type: " + msg_type + "END")
                    connected = False
        connection.close()
        print("[CLOSED] Connection has been closed")

    def handle_get(self, connection):
        print("    [GET] GET handler started")
        msg_length = connection.recv(Protocol.HEADER).decode(Protocol.FORMAT)
        msg_length = int(msg_length)
        print("        [MESSAGE_LENGTH] " + str(msg_length))
        msg = connection.recv(msg_length).decode(Protocol.FORMAT)
        print("        [MESSAGE] " + msg)

        #Answer
        if msg in Server.d:
            answer = str(Server.d [msg])
        else:
            answer = "No Result"

        send_answer = answer.encode(Protocol.FORMAT)
        answer_length = len(send_answer)
        send_length = str(answer_length).encode(Protocol.FORMAT)
        send_length += b' ' * (Protocol.HEADER - len(send_length)) #Abbending bytes to match HEADER size

        #Sending#sending length
        connection.send(send_length)
        print("    [ANSWER_LENGTH] Sending the length: " + send_length.decode(Protocol.FORMAT).replace(" ",""))
        #sending name
        connection.send(send_answer)
        print("    [ANSWER] Sending the Answer: " + send_answer.decode(Protocol.FORMAT))


    def handle_getall(self, connection):
        print("    [GETALL] GETALL handler started")

        #Answer
        send_answer = str(Server.d).encode(Protocol.FORMAT)
        answer_length = len(send_answer)
        send_length = str(answer_length).encode(Protocol.FORMAT)
        send_length += b' ' * (Protocol.HEADER - len(send_length)) #Abbending bytes to match HEADER size

        #Sending#sending length
        connection.send(send_length)
        print("    [ANSWER_LENGTH] Sending the length: " + send_length.decode(Protocol.FORMAT).replace(" ",""))
        #sending name
        connection.send(send_answer)
        print("    [ANSWER] Sending the Answer: " + send_answer.decode(Protocol.FORMAT))



    def handle_disconnect(self, connection):
        print("    [DISCONNECT] DISCONNECT handler started")
        print ("I'm done!")

class Client:

    def __init__(self):
        print("Hello, I am the Client")


    def connect(self):
        print("[CONNECTING]")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((constCS.HOST, constCS.PORT))  # connect to server (block until accepted)
        print("[CONNECTED] to: " + str(constCS.HOST) + "Port: " + str(constCS.PORT))
        return True


    def get(self, name = "No Result"):
        print("\n[GET] starting GET request with: " + name)
        # Letting the Server know, that this is a GET request
        send_get = Protocol.GET_MESSAGE.encode(Protocol.FORMAT)
        send_get += b' ' * (Protocol.HEADER - len(send_get)) #Abbending bytes to match HEADER size
        print("    [TYPE] Sending server the GET_MESSAGE: " + send_get.decode(Protocol.FORMAT).replace(" ",""))
        self.s.send(send_get)

        # calculating length
        send_name = name.encode(Protocol.FORMAT)
        name_length = len(send_name)
        send_length = str(name_length).encode(Protocol.FORMAT)
        send_length += b' ' * (Protocol.HEADER - len(send_length)) #Abbending bytes to match HEADER size

        #sending length
        self.s.send(send_length)
        print("    [LENGTH] Sending server the length: " + send_length.decode(Protocol.FORMAT).replace(" ",""))
        #sending name
        self.s.send(send_name)
        print("    [NAME] Sending server the name: " + send_name.decode(Protocol.FORMAT))

        #Answer
        waiting = True
        while waiting:
            msg_length = self.s.recv(Protocol.HEADER).decode(Protocol.FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                print("    [ANSWER_LENGTH] " + str(msg_length))
                msg = self.s.recv(msg_length).decode(Protocol.FORMAT)
                print("    [Answer] " + msg)
                waiting = False
                return msg


    def getall(self):
        print("\n[GETALL] starting GETALL ")

        # Letting the Server know, that this is a GETALL request
        send_getall = Protocol.GETALL_MESSAGE.encode(Protocol.FORMAT)
        send_getall += b' ' * (Protocol.HEADER - len(send_getall)) #Abbending bytes to match HEADER size
        print("    [TYPE] Sending server the GETALL_MESSAGE: " + send_getall.decode(Protocol.FORMAT).replace(" ",""))
        self.s.send(send_getall)

        #Answer
        waiting = True
        while waiting:
            msg_length = self.s.recv(Protocol.HEADER).decode(Protocol.FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                print("    [ANSWER_LENGTH] " + str(msg_length))
                msg = self.s.recv(msg_length).decode(Protocol.FORMAT)
                print("    [Answer] " + msg)
                waiting = False
                return msg


    def disconnect(self):
        print("\n[DISCONNECT] starting DISCONNECT ")
        # Letting the Server know, that this is a Disconnect message
        send_disconnect = Protocol.DISCONNECT_MESSAGE.encode(Protocol.FORMAT)
        send_disconnect += b' ' * (Protocol.HEADER - len(send_disconnect)) #Abbending bytes to match HEADER size
        print("    [TYPE] Sending server the DISCONNECT_MESSAGE: " + send_disconnect.decode(Protocol.FORMAT).replace(" ",""))
        self.s.send(send_disconnect)
        return True