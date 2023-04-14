import json
import os
import re
import socket
import subprocess
import threading
import time


class CommsClient(threading.Thread):
    def __init__(self, node_id, channel, host, port):
        threading.Thread.__init__(self)
        self.node_id = node_id
        self.channel = channel
        self.host = host
        self.port = port
        self.running = True
        self.switching = False

    def run(self):
        previous_channel = self.channel
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))

            # start a new thread to receive messages from the server
            receive_thread = threading.Thread(target=self.receive_messages, args=(s,))
            receive_thread.start()

            # while self.running:
            #     # ACK channel switch
            #     # TODO: if current channel is different than previous channel
            #     time.sleep(0.1)
            #     data = {'action': 'channel_switch', 'node_id': self.node_id, 'channel': self.channel}
            #     json_str = json.dumps(data)
            #     s.send(json_str.encode())
            #     # TODO: update previous_channel as current channel previous_channel = current channel

    def receive_messages(self, s):
        while self.running:
            data = s.recv(1024).decode()
            if data:
                message = json.loads(data)
                action = message.get("action")
                if action == "broadcast":
                    print(f"Node {self.node_id} received broadcast: {message}")
                    new_channel = message['channel']
                    if not self.switching:
                        self.switching = True
                        self.switch(new_channel)

    def stop(self):
        self.running = False
        self.join()

    def switch(self, freq: int):
        print(f"\nChanging channels... moving to {freq} MHz\n")

        # Put wlp1s0 down
        subprocess.call('ifconfig wlp1s0 0', shell=True)
        subprocess.call('ifconfig wlp1s0 down', shell=True)

        # Kill wpa_supplicant
        print('Killing wpa_supp')
        subprocess.call('killall wpa_supplicant', shell=True)
        time.sleep(10)

        # Ensure clean termination of wpa_supplicant
        filename = '/var/run/wpa_supplicant/wlp1s0'
        if os.path.exists(filename):
            os.remove(filename)
            print(f"{filename} deleted")

        # Change mesh.conf to set FREQ to the value from json file
        with open('/var/run/wpa_supplicant-11s.conf', 'r') as f:
            conf = f.read()
        conf = re.sub(r'frequency=\d+', f'frequency={freq}', conf)
        conf = re.sub(r'country=\d+', f'country=US', conf)
        with open('/var/run/wpa_supplicant-11s.conf', 'w') as f:
            f.write(conf)

        # Restart wpa_supplicant
        print('Restarting wpa_supp')
        subprocess.call(f'wpa_supplicant -Dnl80211 -iwlp1s0 -c /var/run/wpa_supplicant-11s.conf -B', shell=True)
        time.sleep(3)

        # Display changed frequency
        time.sleep(3)
        subprocess.call('iw dev', shell=True)
        self.switching = False


def main():
    host = "40.40.40.5"
    port = 8000
    node_id = 1
    channel = 36

    client = CommsClient(node_id, channel, host, port)
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
