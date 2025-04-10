import time
from threading import Thread

from road_processor import road_processor
from threaded_camera import ThreadedCamera

import cv2
import numpy as np


class ThreadedSignsProcessor:
    def __init__(self, camera: ThreadedCamera,):
        self.threshold = 0.8
        self.frames_count = 0
        self.templates = {}
        self.circle_masks = []
        self.circle_signs = ['left', 'right', 'block', 'stop', 'tupik', 'forward']
        for sign in self.circle_signs:
            self.templates[sign] = []
            self.circle_masks = []
            for scale in np.linspace(0.4, 0.8, 5):
                new_size = (int(100 * scale), int(100 * scale))

                image = cv2.cvtColor(cv2.imread(f'signs/{sign}.png'), cv2.COLOR_BGR2GRAY)
                mask = cv2.cvtColor(cv2.imread('signs/circle_mask.png'), cv2.COLOR_BGR2GRAY)

                # templates[sign].append(cv2.blur(cv2.resize(image, new_size), (10, 10)))
                self.templates[sign].append(cv2.resize(image, new_size))
                self.circle_masks.append(cv2.resize(mask, new_size))

        self.camera = camera

        self.thread = Thread(target=self.update, args=())
        self.thread.running = True
        self.thread.start()

        self.result = None

    def update(self):
        while getattr(self.thread, "running", True):
            if self.camera.frame is not None:
                self.result = self.signs_processor(self.camera.frame)
                time.sleep(0.2)

    def stop(self):
        self.thread.running = False

    def signs_processor(self, rgb_image):
        self.frames_count += 1
        start_time = time.time()

        gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

        result = rgb_image.copy()
        for signi, sign in enumerate(self.circle_signs):
            if self.frames_count % len(self.circle_signs) == signi % len(self.circle_signs):
                all_max_val = 0
                max_w = 0
                max_h = 0
                all_max_loc = None

                for i, template in enumerate(self.templates[sign]):
                    res = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED, None, self.circle_masks[i])
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                    if max_val > all_max_val:
                        all_max_val = max_val
                        all_max_loc = max_loc
                        max_w, max_h = template.shape[:2]

                if all_max_val > self.threshold:
                    cv2.rectangle(result, all_max_loc, (all_max_loc[0] + max_w, all_max_loc[1] + max_h),
                                  (255 * (signi == 0), 255 * (signi == 1), 255 * (signi == 2)), 2)

        total_time = time.time() - start_time
        print(f'Total time: {total_time:.2f}')
        return result

