import json
import logging
import signal
import socket
import sqlite3
import sys
import threading
import time
from typing import List, Tuple, Dict, Any

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

            nodes = [(1, 36)]
            for node in nodes:
                c.execute("INSERT INTO node_channels (node_id, channel) VALUES (?, ?)", node)
            conn.commit()

            c.execute('DROP TABLE IF EXISTS channel_quality')
            c.execute("""
            CREATE TABLE IF NOT EXISTS channel_quality (
                channel INTEGER PRIMARY KEY,
                quality REAL
            )
            """)
            conn.commit()

    def run(self) -> None:
        """
        Periodically fetches and displays data from the SQLite database.
        """
        display_channels_thread = threading.Thread(target=self.display_node_channels)
        display_quality_thread = threading.Thread(target=self.display_channel_quality)

        display_channels_thread.start()
        display_quality_thread.start()

        display_channels_thread.join()
        display_quality_thread.join()

    def display_channel_quality(self) -> None:
        """
        Periodically fetches and displays data from the channel_quality table.
        """
        prev_results = None
        while self.running:
            time.sleep(self.interval)
            try:
                with sqlite3.connect('demo.db') as conn:
                    c = conn.cursor()
                    c.execute("SELECT * FROM channel_quality")
                    results = c.fetchall()
                    if prev_results is None or results != prev_results:
                        logging.info("Channel Quality:")
                        for row in results:
                            logging.info(f"Channel: {row[0]}, Quality: {row[1]}")
                        prev_results = results
            except Exception as e:
                logging.error("Database connection error", exc_info=True)
                self.running = False
                break

    def display_node_channels(self) -> None:
        """
        Periodically fetches and displays data from the node_channels table.
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
                        logging.info("Node Channels:")
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
    def __init__(self, socket: socket.socket, address: Tuple[str, int], clients: List["Client"]):
        """
        Initializes the Client object.

        :param socket: The connected socket for the client.
        :param address: The address of the client.
        :param clients: A list of all connected clients.
        """
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.running = True
        self.conn = sqlite3.connect('demo.db', check_same_thread=False)
        self.c = self.conn.cursor()
        self.clients = clients
        self.start()

    def run(self) -> None:
        """
        Handles incoming messages from the client and updates the SQLite database.
        """
        while self.running:
            try:
                message = self.socket.recv(1024).decode()
                if not message:
                    break

                json_object = json.loads(message)
                action = json_object.get("action")
                if action == "broadcast":
                    self.broadcast(json_object)
                elif action == "channel_switch":
                    self.update_node_channel(json_object["node_id"], json_object["channel"])
                elif action == "new_estimation":
                    self.store_channel_quality(json_object["channel_quality"], json_object["channels"])
            except ConnectionResetError:
                logging.warning("Connection forcibly closed by the remote host")
                break
            except ValueError:
                logging.warning("Message is not a JSON", exc_info=True)
                break

    def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Sends a message to all connected clients except for the sender.

        :param message: The message to broadcast.
        """
        for client in self.clients[:]:  # create a copy of the list for safe iteration
            if client != self:
                try:
                    client.socket.sendall(json.dumps(message).encode())
                except BrokenPipeError:
                    print("Broken pipe error, client disconnected:", client.address)
                    self.clients.remove(client)

    def update_node_channel(self, node_id: int, channel: int) -> None:
        """
        Updates the node_channels table with the given node_id and channel values.

        :param node_id: The node ID to update in the table.
        :param channel: The channel value to set for the node.
        """
        self.c.execute("""
        REPLACE INTO node_channels (node_id, channel)
        VALUES (?, ?)
        """, (node_id, channel))
        self.conn.commit()

    def store_channel_quality(self, channel_quality: List[float], channels: List[int]) -> None:
        """
        Stores the channel quality data in the channel_quality table.

        :param channel_quality: A list of channel quality values.
        :param channels: A list of channel indices corresponding to the quality values.
        """
        for channel, quality in zip(channels, channel_quality):
            self.c.execute("""
            REPLACE INTO channel_quality (channel, quality)
            VALUES (?, ?)
            """, (channel, quality))
        self.conn.commit()

    def stop(self) -> None:
        """
        Stops the Client thread and closes the socket and database connections.
        """
        self.running = False
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
        logging.info("server started and listening")

        while True:
            c_socket, c_address = serversocket.accept()
            client = Client(c_socket, c_address, self.clients)
            print('New connection', client)
            self.clients.append(client)

    def signal_handler(self, sig: signal.Signals, frame) -> None:
        """
        Handles a signal interrupt (SIGINT) and stops the server gracefully.

        :param sig: The signal received by the handler.
        :param frame: The current execution frame.
        """
        print("Attempting to close threads.")
        for client in self.clients:
            print("joining", client.address)
            client.stop()
        print("threads successfully closed")
        sys.exit(0)


def main():
    dd = DatasetManager()
    dd.start()

    # host, port = "40.40.40.5", 8000
    host, port = "localhost", 8000
    server = Server(host, port)
    server.start()


if __name__ == "__main__":
    main()
