import time
from threading import Thread

import cv2
import numpy as np

from signs_algorithm import sign_process
from threaded_camera import ThreadedCamera


class ThreadedProcessor:
    def __init__(self, camera: ThreadedCamera):
        self.camera = camera

        self.thread = Thread(target=self.update, args=())
        self.thread.start()

        self.frame = None

    def update(self):
        while True:
            if self.camera.frame is not None:
                self.frame = sign_process(self.camera.frame)

