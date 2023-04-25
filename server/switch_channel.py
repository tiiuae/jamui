import json
import os
import re
import socket
import subprocess
import threading
import time


class CommsClient(threading.Thread):
    def __init__(self, node_id: int, freq: int, host: str, port: int) -> None:
        """
        Initialize the CommsClient object.

        :param node_id: An integer representing the node ID.
        :param freq: An integer representing the channel frequency.
        :param host: A string representing the host address.
        :param port: An integer representing the port number.
        """
        super().__init__()
        self.node_id = node_id
        self.frequency = freq
        self.host = host
        self.port = port
        self.running = threading.Event()
        self.switching = threading.Event()
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    def run(self) -> None:
        self.socket.connect((self.host, self.port))
        self.running.set()
        receive_thread = threading.Thread(target=self.receive_messages, args=(self.socket,))
        receive_thread.start()

    def receive_messages(self, socket: socket.socket) -> None:
        """
        Receive messages from the socket server.

        :param socket: A socket object representing the connection.
        """
        while self.running.is_set():
            try:
                message = socket.recv(1024).decode()
                if not message:
                    break

                json_object = json.loads(message)
                action = json_object.get("action")
                if action == "broadcast":
                    print(f"Node {self.node_id} received broadcast: {message}")
                    new_channel = json_object['channel']
                    if not self.switching.is_set():
                        self.switching.set()
                        self.switch_channel(new_channel)
                        self.switching.clear()

            except ConnectionResetError:
                print("Connection forcibly closed by the remote host")
                break
            except ValueError:
                print("Message is not a JSON")
                break

    def stop(self) -> None:
        self.running.clear()
        self.socket.close()
        self.join()

    def switch_channel(self, freq: int) -> None:
        """
        Change the channel and call the ack_channel_change method.

        :param freq: An integer representing the new frequency.
        """
        print(f"\nChanging channels... moving to {freq} MHz\n")
        subprocess.run(['ifconfig', 'wlp1s0', '0'])
        subprocess.run(['ifconfig', 'wlp1s0', 'down'])
        subprocess.run(['killall', 'wpa_supplicant'])
        time.sleep(10)

        filename = '/var/run/wpa_supplicant/wlp1s0'
        if os.path.exists(filename):
            os.remove(filename)
            print(f"{filename} deleted")

        with open('/var/run/wpa_supplicant-11s.conf', 'r') as f:
            conf = f.read()
        conf = re.sub(r'frequency=\d+', f'frequency={freq}', conf)
        conf = re.sub(r'country=\d+', f'country=US', conf)
        with open('/var/run/wpa_supplicant-11s.conf', 'w') as f:
            f.write(conf)

        subprocess.run(['wpa_supplicant', '-Dnl80211', '-iwlp1s0', '-c', '/var/run/wpa_supplicant-11s.conf', '-B'])
        time.sleep(4)
        subprocess.run(['iw', 'dev'])

        # Update current frequency
        self.frequency = freq

        # Call the ack_channel_change method after the channel has been switched
        self.ack_channel_change()


    def ack_channel_change(self) -> None:
        """
        Send an acknowledgement to the socket server with the node and channel.
        """
        data = {'action': 'channel_switch', 'node_id': self.node_id, 'channel': self.frequency}
        json_str = json.dumps(data)
        self.socket.send(json_str.encode())


def main():
    host = "fd01::1"
    port = 8080
    node_id = 1
    freq = 5180

    client = CommsClient(node_id, freq, host, port)
    client.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Attempting to stop the clients.")
        client.stop()
        print("CommsClients successfully stopped.")


if __name__ == '__main__':
    main()
