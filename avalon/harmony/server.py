"""
TODO:

 - [x] python > fake harmony.
 - [x] python < fake harmony.
 - [x] python > harmony.
 - [x] python < harmony.
 - [ ] setup Harmony launching and installing.
"""

import socket
import logging
import json
import threading
import traceback
import importlib


class Server(object):

    def __init__(self, port):
        self.connection = None
        self.received = ""

        # Setup logging.
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.DEBUG)

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ("localhost", port)
        self.log.debug("Starting up on {}".format(server_address))
        self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(1)

    def process_request(self, request):
        """

        Args:
            request (dict): {
                "module": str,  # Module of method.
                "method" str,  # Name of method in module.
            }
        """
        self.log.debug("Processing request: {}".format(request))

        try:
            module = importlib.import_module(request["module"])
            method = getattr(module, request["method"])
            method()
        except Exception:
            self.log.error(traceback.format_exc())

    def receive(self):
        while True:
            # Receive the data in small chunks and retransmit it
            request = None
            while True:
                data = self.connection.recv(16)
                if data:
                    self.received += data.decode("utf-8")
                else:
                    break

                self.log.debug("Received: {}".format(self.received))

                try:
                    request = json.loads(self.received)
                    break
                except json.decoder.JSONDecodeError:
                    pass

            if request is None:
                break

            self.process_request(request)

            self.log.debug("Request: {}".format(request))
            if "reply" not in request.keys():
                request["reply"] = True
                self._send(json.dumps(request))
                self.received = ""

    def start(self):
        # Wait for a connection
        self.log.debug("Waiting for a connection.")
        self.connection, client_address = self.sock.accept()

        self.log.debug("Connection from: {}".format(client_address))

        self.receive()

    def _send(self, message):
        # Wait for a connection.
        while not self.connection:
            pass

        self.log.debug("Sending: {}".format(message))
        self.connection.sendall(message.encode("utf-8"))

    def send(self, message):
        self._send(message)

        while True:
            try:
                json.loads(self.received)
                break
            except json.decoder.JSONDecodeError:
                pass

        self.received = ""


if __name__ == "__main__":
    server = Server(8081)
    thread = threading.Thread(target=server.start)
    thread.deamon = True
    thread.start()
    """
    server.send(json.dumps({"string": "This is a long message from server."}))
    server.send(json.dumps({"integer": 1, "float": 1.2345346}))
    """
