import logging
import socket

import constCS
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab


class Server:

    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((constCS.HOST, constCS.PORT))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))


    def serve(self):
        telephoneDictionary = {"James": 235007, "Luke": 571708, "Holy": 839655, "Maria": 229351}
        self.sock.listen(1)
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                print("before connection address ")
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                print("after connection address")
                while True:  # forever
                    data = connection.recv(1024)  # receive data from client
                    print("Message received: " + data.decode('ascii'))
                    if not data:
                        print("not Data break")
                        break  # stop if client stopped
                    if data.decode('ascii') in telephoneDictionary:
                        answer = str(telephoneDictionary[data.decode('ascii')])
                    else:
                        answer = "No Result"
                    connection.send(answer.encode('ascii'))  # return sent data plus an "*"
                    print("Message sent: " + answer)
                print("after While Loop, before connection.close()")
                connection.close()  # close the connection
                print("[CLOSED] Connection closed and Message sent")
            except socket.timeout:
                print("timeout")
                pass  # ignore timeouts
        self.sock.close()
        print("[CLOSED] Socket closed")
        self._logger.info("Server down.")

class Client:
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((constCS.HOST, constCS.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def call(self, msg_in="Hello, world"):
        self.sock.send(msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('ascii')
        print(msg_out)  # print the result
        self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return msg_out

    def get(self, name = "Maria"):
        self.sock.send(name.encode('ascii'))
        data = self.sock.recv(1024)
        msg_received = data.decode('ascii')
        print("Received Message " + msg_received)
        self.sock.close()
        self.logger.info("Client down.")
        self.sock.close()
        return msg_received

    def close(self):
        self.sock.close()
        print("closed")
