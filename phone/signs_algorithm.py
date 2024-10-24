import cv2
import numpy as np

threshold = 0.8
left_template = cv2.cvtColor(cv2.imread('signs/left.png'), cv2.COLOR_BGR2GRAY)
w, h = left_template.shape

def sign_process(rgb_image):
    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_image, left_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    result = gray_image.copy()
    if max_val > threshold:
        cv2.rectangle(result, max_loc, (max_loc[0] + w, max_loc[1] + h), (255, 0, 0), 2)

    return result