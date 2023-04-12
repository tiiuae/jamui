import json
import socket
import threading
import time


class Client(threading.Thread):
    def __init__(self, node_id, channel, host, port):
        threading.Thread.__init__(self)
        self.node_id = node_id
        self.channel = channel
        self.host = host
        self.port = port
        self.running = True

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))

            while self.running:
                time.sleep(1)
                data = {'action': 'channel_switch', 'node_id': self.node_id, 'channel': self.channel}
                json_str = json.dumps(data)
                s.send(json_str.encode())
                print('sent')

    def stop(self):
        self.running = False
        self.join()


def main():
    host = "localhost"
    port = 8000

    clients = [Client(1, 36, host, port), Client(2, 36, host, port), Client(3, 36, host, port)]
    # clients = [Client(1, 36, host, port)]
    for client in clients:
        client.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Attempting to stop the clients.")
        for client in clients:
            client.stop()
        print("Clients successfully stopped.")


if __name__ == '__main__':
    main()
