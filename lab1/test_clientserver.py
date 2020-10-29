import logging
import threading
import unittest

import clientserver
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)


class TestEchoService(unittest.TestCase):
    _server = clientserver.Server()  # create single server in class variable
    _server_thread = threading.Thread(target=_server.serve)  # define thread for running server

    @classmethod
    def setUpClass(cls):
        print ("setUp Class")
        cls._server_thread.start()  # start server loop in a thread (called only once)

    def setUp(self):
        print ("setUp")
        super().setUp()
        self.client = clientserver.Client()  # create new client for each test

    def test_srv_connect(self):
        print ("Test - connect")
        result = self.client.connect()
        self.assertEqual(result, True)

    def test_srv_get(self):  # each test_* function is a test
        print ("Test - get")
        msg = self.client.get("James")
        self.assertEqual(msg, 235007)

    def test_srv_getall(self):  # each test_* function is a test
        print ("Test - getall")
        msg = self.client.getall()
        self.assertNotEqual(msg, None)

    def test_srv_disconnect(self):
        print ("Test - disconnect")
        result = self.client.disconnect()
        self.assertEqual(result, True)

    def tearDown(self):
        print ("Teardown")
        self.client.close()  # terminate client after each test

    @classmethod
    def tearDownClass(cls):
        print ("Teardown CLass")
        cls._server._serving = False  # break out of server loop
        cls._server_thread.join()  # wait for server thread to terminate


if __name__ == '__main__':
    unittest.main()
