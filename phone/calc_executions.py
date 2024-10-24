import time
import urllib

import cv2
import numpy as np
from flask import make_response, Flask, Response

from threaded_camera import ThreadedCamera
from settings import WEBCAM_URL
from threaded_processor import frame_processor

if __name__ == '__main__':
    num_repetitions = 100
    start_time = time.time()
    camera = ThreadedCamera()
    while camera.frame is None:
        time.sleep(0.1)
    for _ in range(num_repetitions):
        image = camera.frame
    end_time = time.time()
    total_time = end_time - start_time
    average_time_per_execution = total_time / num_repetitions
    executions_per_second = 1 / average_time_per_execution
    print(f"Average time per execution: {average_time_per_execution:.6f} seconds")
    print(f"Executions per second: {executions_per_second:.2f}")