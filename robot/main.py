#!/usr/bin/env micropython

import time

from ev3dev2.led import Leds
from ev3dev2.motor import MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor.lego import UltrasonicSensor
from ev3dev2.auto import *

from pid import PID
from redis_communication import send_redis_command, parse_redis_response

leds = Leds()
motor1 = MediumMotor(OUTPUT_B)
motor2 = MediumMotor(OUTPUT_C)
motor = MediumMotor(OUTPUT_A)

motor1.off()
motor2.off()

motor.on_for_seconds(SpeedPercent(50), 1)
start_deg = motor.degrees
time.sleep(1)
motor.on_for_seconds(SpeedPercent(-50), 1)
finish_deg = motor.degrees
min_max_deg = (start_deg - finish_deg) / 2
print(min_max_deg)
time.sleep(1)
motor.on_for_degrees(SpeedPercent(50), min_max_deg)
motor.off()
start_deg = motor.degrees
time.sleep(1)

motor1.on(SpeedPercent(-30))
motor2.on(SpeedPercent(-30))

pid = PID(1.3, 0, 25, setpoint=0, sample_time=50, output_limits=(-min_max_deg, min_max_deg))

us = UltrasonicSensor(INPUT_4)


def move(new_angle):
    cur_angle = start_deg - motor.degrees
    motor_delta = min(abs(cur_angle - new_angle), min_max_deg)

    direction = 1 if new_angle < cur_angle else -1
    # print(cur_angle, delta, direction)
    motor.on_for_degrees(SpeedPercent(100 * direction), motor_delta)


try:
    while True:
        print(us.distance_centimeters)

        response = send_redis_command("MGET delta curvature")
        delta, curvature = parse_redis_response(response)

        angle = -float(delta)
        # print("delta received:", angle)

        pid_value = pid.update(angle)
        if pid_value is not None:
            move(pid_value)
except KeyboardInterrupt:
    print()
    print("Off motors...")
    motor1.off(brake=False)
    motor2.off(brake=False)
    motor.off(brake=False)
    print("Bue!")

