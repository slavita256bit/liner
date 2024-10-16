import time

import cv2


def frame_processor(image):
    start = time.time()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    width = image.shape[1] // 4
    height = image.shape[0] // 4
    image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    return image, time.time() - start