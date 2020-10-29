import socket

import constCS
class Client:
    HEADER = 64
    GET_MESSAGE = "GET"
    GETALL_MESSAGE = "GETALL"
    DISCONNECT_MESSAGE = "!DISCONNECT"

    FORMAT = 'ascii'

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((constCS.HOST, constCS.PORT))  # connect to server (block until accepted)

        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.connect((constCS.HOST, constCS.PORT))
        #s elf.logger.info("Client connected to socket " + str(self.sock))

    def get(self, name = "No Result"):
        print("\n[GET] starting GET request with: " + name)
        # Letting the Server know, that this is a GET request
        send_get = GET_MESSAGE.encode(FORMAT)
        send_get += b' ' * (HEADER - len(send_get)) #Abbending bytes to match HEADER size
        print("    [TYPE] Sending server the GET_MESSAGE: " + send_get.decode(FORMAT).replace(" ",""))
        self.s.send(send_get)

        # calculating length
        send_name = name.encode(FORMAT)
        name_length = len(send_name)
        send_length = str(name_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length)) #Abbending bytes to match HEADER size

        #sending length
        self.s.send(send_length)
        print("    [LENGTH] Sending server the length: " + send_length.decode(FORMAT).replace(" ",""))
        #sending name
        self.s.send(send_name)
        print("    [NAME] Sending server the name: " + send_name.decode(FORMAT))

        #Answer
        waiting = True
        while waiting:
            msg_length = self.s.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                print("    [ANSWER_LENGTH] " + str(msg_length))
                msg = self.s.recv(msg_length).decode(FORMAT)
                print("    [Answer] " + msg)
                waiting = False


    def getall(self):
        print("\n[GETALL] starting GETALL ")

        # Letting the Server know, that this is a GETALL request
        send_getall = GETALL_MESSAGE.encode(FORMAT)
        send_getall += b' ' * (HEADER - len(send_getall)) #Abbending bytes to match HEADER size
        print("    [TYPE] Sending server the GETALL_MESSAGE: " + send_getall.decode(FORMAT).replace(" ",""))
        self.s.send(send_getall)

        #Answer
        waiting = True
        while waiting:
            msg_length = self.s.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                print("    [ANSWER_LENGTH] " + str(msg_length))
                msg = self.s.recv(msg_length).decode(FORMAT)
                print("    [Answer] " + msg)
                waiting = False


    def disconnect(self):
        print("\n[DISCONNECT] starting DISCONNECT ")
        # Letting the Server know, that this is a Disconnect message
        send_disconnect = DISCONNECT_MESSAGE.encode(FORMAT)
        send_disconnect += b' ' * (HEADER - len(send_disconnect)) #Abbending bytes to match HEADER size
        print("    [TYPE] Sending server the DISCONNECT_MESSAGE: " + send_disconnect.decode(FORMAT).replace(" ",""))
        self.s.send(send_disconnect)