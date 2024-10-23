import time
from threading import Thread

import cv2
import numpy as np

from threaded_camera import ThreadedCamera

template = cv2.imread('tests/right_template.png', 0)
h, w = template.shape[:2]

class ThreadedProcessor:
    def __init__(self, camera: ThreadedCamera, fps: int):
        self.camera = camera
        self.fps = fps

        self.thread = Thread(target=self.update, args=())
        self.thread.start()

        self.frame = None

    def update(self):
        while True:
            if self.camera.frame is not None:
                self.frame = self.process(self.camera.frame)
            time.sleep(1 / self.fps)

    def process(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # image = cv2.GaussianBlur(image, (5, 5), 0)
        # image = cv2.Canny(image, 100, 200) q
        # width = image.shape[1] // 4
        # height = image.shape[0] // 4
        # image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

        res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)

        # Draw rectangles around matches
        for pt in zip(*loc[::-1]):
            cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

        # threshold = 0.8

        # for scale in np.linspace(0.8, 1.2, 5):  # You can adjust the scale range and step
        #     # Resize the template to the current scale
        #     resized_template = cv2.resize(template, (int(w * scale), int(h * scale)))
        #
        #     # Get the new dimensions of the resized template
        #     resized_h, resized_w = resized_template.shape[:2]
        #
        #     # Make sure the resized template is smaller than the image
        #     if resized_w > image.shape[1] or resized_h > image.shape[0]:
        #         continue
        #
        #     # Perform template matching
        #     res = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)
        #
        #     # Find the best match location in the result
        #     loc = np.where(res >= threshold)
        #
        #     ok = False
        #     for pt in zip(*loc[::-1]):
        #         ok = True
        #         cv2.rectangle(image, pt, (pt[0] + resized_w, pt[1] + resized_h), (0, 0, 255), 2)
        #         break
        #
        #     if ok:
        #         break

        return image