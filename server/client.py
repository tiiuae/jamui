import json
import random
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

            # start a new thread to receive messages from the server
            receive_thread = threading.Thread(target=self.receive_messages, args=(s,))
            receive_thread.start()

            while self.running:

                self.channel = random.choice([36, 40, 44, 48, 52, 56, 60, 64, 149, 153, 157, 161, 165])
                data = {'action': 'channel_switch', 'node_id': self.node_id, 'channel': self.channel}
                json_str = json.dumps(data)
                s.send(json_str.encode())
                print(f'sent: {json_str}')
                time.sleep(10)
                # print('sent')

                # if self.node_id == 1:
                #     data = {'action': 'broadcast', 'channel': 1}
                #     json_str = json.dumps(data)
                #     s.send(json_str.encode())
                #     print('sent')

    def receive_messages(self, s):
        while self.running:
            data = s.recv(1024).decode()
            if data:
                message = json.loads(data)
                action = message.get("action")
                if action == "broadcast":
                    print(f"Node {self.node_id} received broadcast: {message}")

    def stop(self):
        self.running = False
        self.join()


def main():
    host = "localhost"
    port = 8000

    clients = [Client(1, 40, host, port)]
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
