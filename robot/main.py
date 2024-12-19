#!/usr/bin/env python3

import socket
import time

from ev3dev2.led import Leds
from ev3dev2.motor import MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank

leds = Leds()
motor1 = MediumMotor(OUTPUT_A)
motor2 = MediumMotor(OUTPUT_B)
motor = MediumMotor(OUTPUT_D)
# motor1.on(SpeedPercent(30))
# motor2.on(SpeedPercent(30))

# motor.on_for_seconds(SpeedPercent(50), 1)
# start_deg = motor.degrees
# time.sleep(1)
# motor.on_for_seconds(SpeedPercent(-50), 1)
# finish_deg = motor.degrees
# min_max_deg = (start_deg - finish_deg) / 2
# print(min_max_deg)
# time.sleep(1)
# motor.on_for_degrees(SpeedPercent(50), min_max_deg)
# motor.off()
# start_deg = motor.degrees


# def move(angle):
#     if angle > min_max_deg:
#         angle = min_max_deg
#
#     if angle < -min_max_deg:
#         angle = -min_max_deg
#
#     direction = 1 if angle > 0 else -1
#     motor.on_for_degrees(SpeedPercent(50 * direction), abs(angle - (motor.degrees - start_deg)))


# while True:
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect(('localhost', 8765))
    #     print('Connected')
    #     while True:
    #         # s.sendall(b'go')
    #         data = s.recv(1024)
    #         # move(data)
    #         print(data.decode("utf-8"))
    #         time.sleep(0.05)
    #     time.sleep(0.5)

