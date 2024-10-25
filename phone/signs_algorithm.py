import cv2
import numpy as np

threshold = 0.8

left_template = []
circle_mask = []
for scale in np.linspace(0.7, 1.1, 4):
    new_size = (int(100 * scale), int(100 * scale))
    left_template.append(cv2.resize(cv2.cvtColor(cv2.imread('signs/left.png'), cv2.COLOR_BGR2GRAY), new_size))
    circle_mask.append(cv2.resize(cv2.cvtColor(cv2.imread('signs/circle_mask.png'), cv2.COLOR_BGR2GRAY), new_size))


def sign_process(rgb_image):
    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

    all_max_val = 0
    max_w = 0
    max_h = 0
    all_max_loc = None

    for i, template in enumerate(left_template):
        res = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED, None, circle_mask[i])
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val > all_max_val:
            all_max_val = max_val
            all_max_loc = max_loc
            max_w, max_h = template.shape[:2]

    result = gray_image.copy()
    if all_max_val > threshold:
        cv2.rectangle(result, all_max_loc, (all_max_loc[0] + max_w, all_max_loc[1] + max_h), (255, 0, 0), 2)

    return result
