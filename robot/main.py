#!/usr/bin/env python3

import socket
import time

from ev3dev2.led import Leds
from ev3dev2.motor import MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank


def send_redis_command(command, host='127.0.0.1', port=6379):
    """
    Sends a raw Redis command using the RESP protocol.
    """
    # Connect to Redis
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Convert the command into RESP format
    command_parts = command.split()
    resp_command = "*{}\r\n".format(len(command_parts))
    for part in command_parts:
        resp_command += "${}\r\n{}\r\n".format(len(part), part)

    # Send the command
    client.sendall(resp_command.encode())

    # Read the response
    response = client.recv(4096).decode()
    client.close()

    return response


def parse_redis_response(response):
    """
    Parses a RESP response and extracts the actual value.
    """
    # Check the first character to identify the type of response
    if response.startswith('+'):  # Simple string
        return response[1:].strip()
    elif response.startswith('$'):  # Bulk string
        # Example response: "$7\r\nmyvalue\r\n"
        lines = response.split("\r\n")
        if lines[0] == "$-1":  # Null bulk string
            return None
        return lines[1]  # Actual value is in the second line
    elif response.startswith(':'):  # Integer
        return int(response[1:].strip())
    elif response.startswith('-'):  # Error
        return "Error: {}".format(response[1:].strip())
    else:
        return "Unknown response: {}".format(response.strip())

# # Updated example usage
# response = send_redis_command("SET mykey myvalue")
# print("SET Response:", parse_redis_response(response))


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

motor1.on(SpeedPercent(-10))
motor2.on(SpeedPercent(-10))

def move(angle):
    cur_angle = start_deg - motor.degrees
    delta = min(abs(cur_angle - angle), min_max_deg)

    direction = 1 if angle < cur_angle else -1
    # print(cur_angle, delta, direction)
    motor.on_for_degrees(SpeedPercent(100 * direction), delta)


# move(-40)
# time.sleep(2)
# move(40)
# time.sleep(2)
# move(70)
# time.sleep(2)
# move(-70)

try:
    while True:
        delta = float(parse_redis_response(send_redis_command("GET delta")))
        print(delta, motor.degrees - start_deg)
        move(delta)
except KeyboardInterrupt:
    motor1.off()
    motor2.off()

