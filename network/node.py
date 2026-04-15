# network/node.py

import socket
import json

class Node:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()

        print(f"[DSAN NODE] Listening on {self.port}")

        while True:
            conn, addr = server.accept()
            data = conn.recv(4096)

            try:
                msg = json.loads(data.decode())
                print(f"[RECEIVED] {msg}")
            except:
                print("[ERROR] Invalid message")

            conn.close()
