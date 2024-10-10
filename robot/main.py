#!/usr/bin/env python3

import socket
from ev3dev2.led import Leds

leds = Leds()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('localhost', 8765))
    print('Connected')
    s.sendall(b"Hello, world")
    data = s.recv(1024)
    print('Received')
    print(data)

