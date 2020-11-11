import constRPC
import threading
import time
from context import lab_channel

ACKAPPEND = "ACKAPPEND"

class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self


class Client:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.client = self.chan.join('client')
        self.server = None

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')


    def alive(self, count, sec):
        while count > 0:
            print("[client] I'm stil alive " + str(int(count/sec)))
            time.sleep(sec)
            count = count - 1

    def stop(self):
        self.chan.leave('client')

    def append(self, data, db_list):
        assert isinstance(db_list, DBList)
        msglst = (constRPC.APPEND, data, db_list)  # message payload
        self.chan.send_to(self.server, msglst)  # send msg to server
        msgrcv = self.chan.receive_from(self.server)  # wait for response
        return msgrcv[1]  # pass it to caller

    class AsnycAppend(threading.Thread):
        def __init__(self, data, db_list, client, callback = None):
            threading.Thread.__init__(self)
            self.data = data
            self.db_list = db_list
            self.chan = client.chan
            self.server = client.server
            self.callback = callback

        def run(self):
            assert isinstance(self.db_list, DBList)
            msglst = (constRPC.APPEND, self.data, self.db_list)  # message payload
            self.chan.send_to(self.server, msglst)  # send msg to server
            print("[AsyncAppend] Request sent")
            ackrcv = self.chan.receive_from(self.server)  # wait for response
            if ackrcv[1] == ACKAPPEND:
                print("[AsyncAppend] " + ackrcv[1] + " received from " + ackrcv[0])
                msgrcv = self.chan.receive_from(self.server)  # wait for response
                print("[AsyncAppend] Result: " + str(msgrcv[1]))
                if self.callback:
                    self.callback(msgrcv[1])






class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        return db_list.append(data)

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                client = msgreq[0]  # see who is the caller
                #Sending ack ACKAPPEND
                self.chan.send_to({client}, ACKAPPEND)  # return response
                print("[Server] Request received, ACK sent")
                msgrpc = msgreq[1]  # fetch call & parameters
                if constRPC.APPEND == msgrpc[0]:  # check what is being requested
                    result = self.append(msgrpc[1], msgrpc[2])  # do local call
                    print("[Server] I'm tired from appending the message, I'll try to get some sleep")
                    time.sleep(10)  # pretend working
                    print("[Server] I just woke up")
                    self.chan.send_to({client}, result)  # return response
                    print("[Server] Answer sent\n")
                else:
                    pass  # unsupported request, simply ignore
