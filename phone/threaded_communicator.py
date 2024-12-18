import socket
import time
from threading import Thread


class ThreadedRobotCommunicator(object):
    def __init__(self):
        self.conn = None
        self.frame = None
        self.thread = Thread(target=self.update, args=())
        self.thread.start()

    def send(self, data):
        with self.conn:
            new_data = str(data)
            print(new_data)
            self.conn.sendall(str.encode(new_data))

    def update(self):
        while True:
            print('Waiting for robot...')
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', 8765))
                s.listen()
                conn, addr = s.accept()
                self.conn = conn
                print(f'Connected to robot ({addr})')
                # with conn:
                #     print(f'Connected to robot ({addr})')
                #     while True:
                #         data = conn.recv(1024)
                #         if not data:
                #             break
                #         print(f'data: {data}')
                #         print(self.data_to_send)
                #         if data == b'go' and self.data_to_send is not None:
                #             new_data = str(self.data_to_send)
                #             print(new_data)
                #             conn.sendall(str.encode(new_data))
                #             self.data_to_send = None
            time.sleep(1)
