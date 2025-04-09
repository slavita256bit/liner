#!/usr/bin/env micropython

import time

from ev3dev2._platform.ev3 import INPUT_4
from ev3dev2.led import Leds
from ev3dev2.motor import MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor.lego import UltrasonicSensor

from filters import KalmanFilter1D, MovingAverage, ExponentialSmoothing
from pid import PID
from redis_communication import send_redis_command, parse_redis_response


def start_motors(speed = 20):
    motor1.on(SpeedPercent(-speed))
    motor2.on(SpeedPercent(-speed))


def stop_motors():
    motor1.off()
    motor2.off()


leds = Leds()
us = UltrasonicSensor(INPUT_4)
motor1 = MediumMotor(OUTPUT_B)
motor2 = MediumMotor(OUTPUT_C)
motor = MediumMotor(OUTPUT_A)

stop_motors()

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

pid = PID(1.3, 0, 25, setpoint=0, sample_time=50, output_limits=(-min_max_deg, min_max_deg))
# filter = KalmanFilter1D(process_noise=1, measurement_noise=5)
# filter1 = MovingAverage(5)
filter = ExponentialSmoothing(alpha=1, initial_value=0)

start_motors()


def set_angle(new_angle):
    new_angle = min(new_angle, min_max_deg)
    new_angle = max(new_angle, -min_max_deg)

    cur_angle = start_deg - motor.degrees
    motor_delta = abs(cur_angle - new_angle)

    direction = 1 if new_angle < cur_angle else -1
    # print(cur_angle, delta, direction)
    motor.on_for_degrees(SpeedPercent(100 * direction), motor_delta)


try:
    while True:
        if us.distance_centimeters < 30:
            print("BRICK FOUND")
            stop_motors()

            time.sleep(0.5)
            set_angle(-min_max_deg)
            start_motors(20)
            time.sleep(1)
            set_angle(min_max_deg)
            time.sleep(1)

            stop_motors()
            time.sleep(1)
            start_motors()
        else:
            response = send_redis_command("MGET delta curvature")
            delta, curvature = parse_redis_response(response)

            angle = -float(delta)
            # print("delta received:", angle)

            angle = filter.update(angle)
            pid_value = pid.update(angle)

            if pid_value is not None:
                set_angle(pid_value)
except KeyboardInterrupt:
    print()
    print("Off motors...")
    motor1.off(brake=False)
    motor2.off(brake=False)
    motor.off(brake=False)
    print("Bue!")

