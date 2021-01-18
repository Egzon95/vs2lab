import random
import logging

# coordinator messages
from const3PC import VOTE_REQUEST, GLOBAL_COMMIT, GLOBAL_ABORT
# participant decissions
from const3PC import LOCAL_SUCCESS, LOCAL_ABORT,PREPARE_COMMIT
# participant messages
from const3PC import VOTE_COMMIT, VOTE_ABORT, NEED_DECISION,READY_COMMIT
# misc constants
from const3PC import TIMEOUT

import stablelog


class Participant:
    """
    Implements a two phase commit participant.
    - state written to stable log (but recovery is not considered)
    - in case of coordinator crash, participants mutually synchronize states
    - system blocks if all participants vote commit and coordinator crashes
    - allows for partially synchronous behavior with fail-noisy crashes
    """

    def __init__(self, chan):
        self.channel = chan
        self.participant = self.channel.join('participant')
        self.stable_log = stablelog.create_log(
            "participant-" + self.participant)
        self.logger = logging.getLogger("vs2lab.lab6.3pc.Participant")
        self.coordinator = {}
        self.all_participants = {}
        self.state = 'NEW'

    @staticmethod
    def _do_work():
        # Simulate local activities that may succeed or not
        return LOCAL_ABORT if random.random() > 2/3 else LOCAL_SUCCESS

    def _enter_state(self, state):
        self.stable_log.info(state)  # Write to recoverable persistant log file
        self.logger.info("Participant {} entered state {}."
                         .format(self.participant, state))
        self.state = state

    def init(self):
        self.channel.bind(self.participant)
        self.coordinator = self.channel.subgroup('coordinator')
        self.all_participants = self.channel.subgroup('participant')
        self._enter_state('INIT')  # Start in local INIT state.

    def run(self):
        # Wait for start of joint commit
        msg = self.channel.receive_from(self.coordinator, TIMEOUT)

        if not msg:  # Crashed coordinator - give up entirely
            # decide to locally abort (before doing anything)
            decision = LOCAL_ABORT

        else:  # Coordinator requested to vote, joint commit starts
            assert msg[1] == VOTE_REQUEST

            # Firstly, come to a local decision
            decision = self._do_work()  # proceed with local activities

            # If local decision is negative,
            # then vote for abort and quit directly
            # Fail
            if decision == LOCAL_ABORT:
                self.channel.send_to(self.coordinator, VOTE_ABORT)

            # If local decision is positive,
            # we are ready to proceed the joint commit
            else:
                assert decision == LOCAL_SUCCESS
                # Notify coordinator about local commit vote
                self._enter_state('READY')
                #send Vote Commit to coordinator
                self.channel.send_to(self.coordinator, VOTE_COMMIT)

                # Wait for coordinator to notify the final outcome
                msg = self.channel.receive_from(self.coordinator, TIMEOUT)
                if not msg:  # Crashed coordinator im wait
                    self._enter_state('ABORT')
                    return "Participant {} terminated in state {}".format(
                        self.participant, self.state)
                else:  # Coordinator came to a decision
                    decision = msg[1]

        # Change local state based on the outcome of the joint commit protocol
        # Note: If the protocol has blocked due to coordinator crash,
        # we will never reach this point
        if decision == PREPARE_COMMIT:
            self._enter_state('PRECOMMIT')
            if random.random() > 2 / 3:  # simulate a crash
                return "Participant {} terminated in state {}".format(
                    self.participant, self.state)
            self.channel.send_to(self.coordinator, READY_COMMIT)

        else:
            assert decision in [GLOBAL_ABORT, LOCAL_ABORT]
            self._enter_state('ABORT')
            return "Participant {} terminated in state {} due to {}.".format(
                self.participant, self.state, decision)

        msg = self.channel.receive_from(self.coordinator,TIMEOUT*2)

        if not msg:
            #Koordinator im Precommit
            self._enter_state('ABORT')
            return "Participant {} terminated in state {}".format(
                self.participant, self.state)

        elif msg[1] == GLOBAL_COMMIT:
            self._enter_state("COMMIT")
            return "Participant {} terminated in state {} due to {}.".format(
                self.participant, self.state, "COMMIT")

        return "Participant {} terminated in state {} due to {}.".format(
            self.participant, self.state, decision)
