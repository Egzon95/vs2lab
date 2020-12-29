import logging
import random
import time

from constMutex import ENTER, RELEASE, ALLOW, ALIVE_R, ALIVE_A, DEATH_REPORT
from datetime import datetime, timedelta

TIME_WORRY = 5
TIME_DEATH = 7

class Process:
    """
    Implements access management to a critical section (CS) via fully
    distributed mutual exclusion (MUTEX).

    Processes broadcast messages (ENTER, ALLOW, RELEASE) timestamped with
    logical (lamport) clocks. All messages are stored in local queues sorted by
    logical clock time.

    A process broadcasts an ENTER request if it wants to enter the CS. A process
    that doesn't want to ENTER replies with an ALLOW broadcast. A process that
    wants to ENTER and receives another ENTER request replies with an ALLOW
    broadcast (which is then later in time than its own ENTER request).

    A process enters the CS if a) its ENTER message is first in the queue (it is
    the oldest pending message) AND b) all other processes have sent messages
    that are younger (either ENTER or ALLOW). RELEASE requests purge
    corresponding ENTER requests from the top of the local queues.

    Message Format:

    <Message>: (Timestamp, Process_ID, <Request_Type>)

    <Request Type>: ENTER | ALLOW  | RELEASE

    """

    def __init__(self, chan):
        self.channel = chan  # Create ref to actual channel
        self.process_id = self.channel.join('proc')  # Find out who you are
        self.all_processes: list = []  # All procs in the proc group
        self.other_processes: list = []  # Needed to multicast to others
        self.queue = []  # The request queue list
        self.clock = 0  # The current logical clock
        self.logger = logging.getLogger("vs2lab.lab5.mutex.process.Process")

        #alive management
        self.other_processes_contact: list = [datetime.min, datetime.min, datetime.min] #List that stores the Time of last contact
        self.other_processes_alive: list = [True, True, True]

    def __mapid(self, id='-1'):
        # resolve channel member address to a human friendly identifier
        if id == '-1':
            id = self.process_id
        return 'Proc_' + chr(65 + self.all_processes.index(id))

    def __cleanup_queue(self):
        if len(self.queue) > 0:
            #self.queue.sort(key = lambda tup: tup[0])
            self.queue.sort()
            # There should never be old ALLOW messages at the head of the queue
            while self.queue[0][2] == ALLOW:
                del (self.queue[0])
                if len(self.queue) == 0:
                    break

    def __request_to_enter(self):
        self.clock = self.clock + 1  # Increment clock value
        request_msg = (self.clock, self.process_id, ENTER)
        self.queue.append(request_msg)  # Append request to queue
        self.__cleanup_queue()  # Sort the queue
        self.channel.send_to(self.other_processes, request_msg)  # Send request
        print("[{}] ENTER request sent".format(self.process_id))

    def __allow_to_enter(self, requester):
        self.clock = self.clock + 1  # Increment clock value
        msg = (self.clock, self.process_id, ALLOW)
        self.channel.send_to([requester], msg)  # Permit other
        print("[{}] ALLOW sent to {}".format(self.process_id , requester))

    def __release(self):
        # need to be first in queue to issue a release
        assert self.queue[0][1] == self.process_id, 'State error: inconsistent local RELEASE'

        # construct new queue from later ENTER requests (removing all ALLOWS)
        tmp = [r for r in self.queue[1:] if r[2] == ENTER]
        self.queue = tmp  # and copy to new queue
        self.clock = self.clock + 1  # Increment clock value
        msg = (self.clock, self.process_id, RELEASE)
        # Multicast release notification
        self.channel.send_to(self.other_processes, msg)
        print("[{}] RELEASE sent".format(self.process_id))

    def __allowed_to_enter(self):
        # See who has sent a message (the set will hold at most one element per sender)
        processes_with_later_message = set([req[1] for req in self.queue[1:]])
        # Access granted if this process is first in queue and all others have answered (logically) later
        other_processes_alive_count = 0
        for i in self.other_processes_alive:
            if i:
                other_processes_alive_count = other_processes_alive_count + 1
        first_in_queue = self.queue[0][1] == self.process_id
        all_have_answered = other_processes_alive_count == len(processes_with_later_message)
        if first_in_queue:
            print("[{}] {}/{} -- {}/{}".format(self.process_id, len(processes_with_later_message), other_processes_alive_count, processes_with_later_message, self.other_processes))
        #print("[{}] allowed first: {} - {}/{} first Item:{}".format(self.process_id, first_in_queue, processes_with_later_message, self.other_processes, self.queue[0]))
        return first_in_queue and all_have_answered

    def __receive(self):
         # Pick up any message
        _receive = self.channel.receive_from(self.other_processes, 2)
        if _receive:
            msg = _receive[1]

            self.clock = max(self.clock, msg[0])  # Adjust clock value...
            self.clock = self.clock + 1  # ...and increment

            #Alive Management
            sender = msg[1]
            sender_i = self.other_processes.index(sender)
            #print("[{}] ALIVE MANAGEMENT {}-i:{}".format(self.process_id, sender, sender_i))
            #self.__print_other_processes()
            self.other_processes_contact[sender_i] = datetime.now()
            self.other_processes_alive[sender_i] = True

            self.logger.debug("{} received {} from {}.".format(
                self.__mapid(),
                "ENTER" if msg[2] == ENTER
                else "ALLOW" if msg[2] == ALLOW
                else "RELEASE", self.__mapid(msg[1])))

            if msg[2] == ENTER:
                self.queue.append(msg)  # Append an ENTER request
                # and unconditionally allow (don't want to access CS oneself)
                self.__allow_to_enter(msg[1])
            elif msg[2] == ALLOW:
                self.queue.append(msg)  # Append an ALLOW
            elif msg[2] == RELEASE:
                # assure release requester indeed has access (his ENTER is first in queue)
                assert self.queue[0][1] == msg[1] and self.queue[0][2] == ENTER, 'State error: inconsistent remote RELEASE'
                del (self.queue[0])  # Just remove first message
            elif msg[2] == ALIVE_R:
                self.__answer_alive(msg[1])
            elif msg[2] == DEATH_REPORT:
                print("[{}] --------------DEATH_REPORT of {} received from {}".format(self.process_id, msg[3], msg[1]))
                self.__remove_otherProcess(msg[3])

            self.__cleanup_queue()  # Finally sort and cleanup the queue
        else:        
            self.logger.warning("{} ({}) timed out on RECEIVE.".format(self.__mapid(), self.process_id))


    def __check_alive(self):
        #print("[{}] Checking if everyone is alive...".format(self.process_id))
        #Calculating times
        now = datetime.now()
        worry = now - timedelta(seconds = TIME_WORRY)
        death = now - timedelta(seconds = TIME_DEATH)
        for i in range(len(self.other_processes)): #Check last contact with each other process
            if self.other_processes_contact[i] == datetime.min: continue
            contact_delta = now - self.other_processes_contact[i]
            if self.other_processes_alive[i]:
                if self.other_processes_contact[i] < death: #Check if process contact has been lost
                    print("[{: <16}] {} - declared dead ({})".format(self.process_id, self.other_processes[i], contact_delta))
                    self.__death_report(self.other_processes[i]) #Synchronising Death with the network
                    self.__remove_otherProcess(self.other_processes[i]) #Removing process from own system
                elif self.other_processes_contact[i] < worry: #Request life signal
                    print("[{: <16}] {} - worried about ({})".format(self.process_id, self.other_processes[i], contact_delta))
                    alive_msg = (self.clock, self.process_id, ALIVE_R)
                    self.channel.send_to([self.other_processes[i]], alive_msg)

    def __answer_alive(self, requester):
        print("[{}] {} asked if I am alive".format(self.process_id, requester))
        alive_msg = (self.clock, self.process_id, ALIVE_A)
        self.channel.send_to([requester], alive_msg)


    def __death_report(self, proc):
        msg = (self.clock, self.process_id, DEATH_REPORT, proc)
        # Multicast release notification
        self.channel.send_to(self.other_processes, msg)
        print("[{}] --------------DEATH_REPORT sent".format(self.process_id))

    def __remove_otherProcess(self, proc):
        id = self.other_processes.index(proc)
        if self.other_processes_alive[id]:
            self.other_processes_alive[id] = False

            print("[{}] QUEUE BEFORE: {} ".format(self.process_id, self.queue))
            # Remove Corresponding List Items
            for item in self.queue:
                if item[1] == self.other_processes[id]:
                    self.queue.remove(item)
            self.__cleanup_queue()

            print("[{}] QUEUE AFTER: {} ".format(self.process_id, self.queue))

    def init(self):
        self.channel.bind(self.process_id)

        self.all_processes = list(self.channel.subgroup('proc'))
        # sort string elements by numerical order
        self.all_processes.sort(key=lambda x: int(x))

        self.other_processes = list(self.channel.subgroup('proc'))
        self.other_processes.remove(self.process_id)

        self.logger.info("Member {} joined channel as {}."
                         .format(self.process_id, self.__mapid()))

    def run(self):
        while True:
            # Enter the critical section if there are more than one process left
            # and random is true
            if len(self.all_processes) > 1 and \
                    random.choice([True, False]):
                self.logger.debug("{} wants to ENTER CS at CLOCK {}."
                    .format(self.__mapid(), self.clock))

                self.__request_to_enter()
                while not self.__allowed_to_enter():
                    self.__receive()
                    self.__check_alive()

                # Stay in CS for some time ...
                sleep_time = random.randint(0, 2000)
                self.logger.debug("{} enters CS for {} milliseconds."
                    .format(self.__mapid(), sleep_time))
                print('<'* 20 + " CS <- {}({}) ".format(self.__mapid(), self.process_id) + '>' *20)
                time.sleep(sleep_time/1000)

                # ... then leave CS
                print(" CS -> {}".format(self.__mapid()))
                self.__release()
                continue

            # Occasionally serve requests to enter
            if random.choice([True, False]):
                self.__receive()

    def __print_other_processes(self):
        print("[{}] Other processes at {}".format(self.process_id, datetime.now()))
        print(' ' * 8 + "%-7s %s" % ("ID", "Last contact"))
        for i in range(len(self.other_processes)):
            print(' ' * 8 + "%-7s %s" % (self.other_processes[i],self.other_processes_contact[i]))