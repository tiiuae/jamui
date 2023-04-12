import json
import logging
import signal
import socket
import sqlite3
import sys
import threading
import time
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)


class DatasetManager(threading.Thread):
    def __init__(self):
        """
        Initializes the DatasetManager object and print nodes once values are updated.
        """
        threading.Thread.__init__(self)
        self.interval = 1
        self.running = True
        self.initialize_database()

    def initialize_database(self) -> None:
        """
        Initializes the SQLite database, creating the schema and inserting initial values.
        """
        with sqlite3.connect('demo.db') as conn:
            c = conn.cursor()
            c.execute('DROP TABLE IF EXISTS node_channels')
            c.execute("""
            CREATE TABLE IF NOT EXISTS node_channels (
                node_id INTEGER PRIMARY KEY,
                channel INTEGER
            )
            """)
            conn.commit()

            nodes = [(1, 40), (2, 40), (3, 40)]
            for node in nodes:
                c.execute("INSERT INTO node_channels (node_id, channel) VALUES (?, ?)", node)
            conn.commit()

    def run(self) -> None:
        """
        Periodically fetches and displays data from the SQLite database.
        """
        prev_results = None
        while self.running:
            time.sleep(self.interval)
            try:
                with sqlite3.connect('demo.db') as conn:
                    c = conn.cursor()
                    c.execute("SELECT * FROM node_channels")
                    results = c.fetchall()
                    if prev_results is None or results != prev_results:
                        for row in results:
                            logging.info(f"Node ID: {row[0]}, Channel: {row[1]}")
                        prev_results = results
            except Exception as e:
                logging.error("Database connection error", exc_info=True)
                self.running = False
                break

    def stop(self) -> None:
        """
        Stops the DatasetManager thread.
        """
        self.running = False
        self.join()


class Client(threading.Thread):
    def __init__(self, socket: socket.socket, address: Tuple[str, int]):
        """
        Initializes the Client object.

        :param socket: The connected socket for the client.
        :param address: The address of the client.
        """
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.running = True
        self.conn = sqlite3.connect('demo.db', check_same_thread=False)
        self.c = self.conn.cursor()
        self.start()

    def run(self) -> None:
        """
        Handles incoming messages from the client and updates the SQLite database.
        """
        while self.running:
            message = self.socket.recv(1024).decode()

            # Check if the message is empty => it occurs when the client disconnects
            if not message:
                break

            try:
                json_object = json.loads(message)
            except ValueError as e:
                logging.warning('Message is not a JSON', exc_info=True)
                break
            else:
                node_id = json_object['node_id']
                channel = json_object['channel']

                self.c.execute("""
                REPLACE INTO node_channels (node_id, channel) 
                VALUES (?, ?)
                """, (node_id, channel))
                self.conn.commit()

        # Close the connection when the loop ends
        self.stop()

    def stop(self) -> None:
        """
        Stops the Client thread and closes the socket and database connections.
        """
        self.running = False
        self.socket.send(b'close')
        self.socket.close()
        self.conn.close()


class Server:
    def __init__(self, host: str, port: int):
        """
        Initializes the Server object.

        :param host: The host address to bind the server to.
        :param port: The port number to bind the server to.
        """
        self.host = host
        self.port = port
        self.clients: List[Client] = []

    def start(self) -> None:
        """
        Starts the server and listens for incoming client connections.
        """
        signal.signal(signal.SIGINT, self.signal_handler)

        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((self.host, self.port))
        serversocket.listen(5)
        logging.info('server started and listening')

        while True:
            c_socket, c_address = serversocket.accept()
            self.clients.append(Client(c_socket, c_address))

    def signal_handler(self, sig: signal.Signals, frame) -> None:
        """
        Handles a signal interrupt (SIGINT) and stops the server gracefully.

        :param sig: The signal received by the handler.
        :param frame: The current execution frame.
        """
        print('Attempting to close threads.')
        for client in self.clients:
            print('joining', client.address)
            client.stop()
        print("threads successfully closed")
        sys.exit(0)


def main():
    dd = DatasetManager()
    dd.start()

    host, port = "localhost", 8000
    server = Server(host, port)
    server.start()


if __name__ == '__main__':
    main()
