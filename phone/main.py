# import socket
import asyncio
import threading
import time
import urllib

import cv2
import numpy as np
from flask import make_response, Flask, Response, render_template

from processor import frame_processor
from settings import WEBCAM_IP

output_frame = None
lock = threading.Lock()
camera = cv2.VideoCapture(WEBCAM_IP)
app = Flask(__name__)

def generate_video():
    global output_frame, lock
    while True:
        with lock:
            success, frame = camera.read()
            output_frame, generation_time = frame_processor(frame)
            print(generation_time)

def feed():
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None:
                continue
            (flag, encoded_image) = cv2.imencode(".jpg", output_frame)
            if not flag:
                continue
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n'

@app.route('/')
def get_index():
    return render_template('index.html')

@app.route("/video_feed")
def video_feed():
    return Response(feed(), mimetype ="multipart/x-mixed-replace; boundary=frame")


threading.Thread(target=generate_video).start()