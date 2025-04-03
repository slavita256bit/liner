import time
from threading import Thread

from road_processor import road_processor
from signs_processor import signs_processor
from threaded_camera import ThreadedCamera


class ThreadedProcessor:
    def __init__(self, camera: ThreadedCamera,):
        self.camera = camera

        self.thread = Thread(target=self.update, args=())
        self.thread.running = True
        self.thread.start()

        self.frame = None

    def update(self):
        while getattr(self.thread, "running", True):
            if self.camera.frame is not None:
                self.frame = road_processor(self.camera.frame)

    def stop(self):
        self.thread.running = False

