from threading import Thread
import cv2, time

from settings import WEBCAM_URL


class ThreadedCamera(object):
    def __init__(self):
        self.capture = cv2.VideoCapture(WEBCAM_URL)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 5)

        self.frame = None
        self.thread = Thread(target=self.update, args=())
        self.thread.running = True
        self.thread.start()

        print('Waiting for camera...')
        while self.frame is None:
            time.sleep(0.5)
        print('Camera is ready.')

    def update(self):
        while getattr(self.thread, "running", True):
            if self.capture.isOpened():
                _, self.frame = self.capture.read()

    def stop(self):
        self.thread.running = False
