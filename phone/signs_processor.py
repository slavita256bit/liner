import time

import cv2
import numpy as np

threshold = 0.8
frames_count = 0
templates = {}
circle_masks = []
circle_signs = ['left', 'right', 'block']
for sign in circle_signs:
    templates[sign] = []
    circle_masks = []
    for scale in np.linspace(0.4, 0.8, 5):
        new_size = (int(100 * scale), int(100 * scale))

        image = cv2.cvtColor(cv2.imread(f'signs/{sign}.png'), cv2.COLOR_BGR2GRAY)
        mask = cv2.cvtColor(cv2.imread('signs/circle_mask.png'), cv2.COLOR_BGR2GRAY)

        # templates[sign].append(cv2.blur(cv2.resize(image, new_size), (10, 10)))
        templates[sign].append(cv2.resize(image, new_size))
        circle_masks.append(cv2.resize(mask, new_size))


def signs_processor(rgb_image):
    global frames_count

    frames_count += 1
    start_time = time.time()

    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

    result = rgb_image.copy()
    for signi, sign in enumerate(circle_signs):
        if frames_count % len(circle_signs) == signi % len(circle_signs):
            all_max_val = 0
            max_w = 0
            max_h = 0
            all_max_loc = None

            for i, template in enumerate(templates[sign]):
                res = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED, None, circle_masks[i])
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                if max_val > all_max_val:
                    all_max_val = max_val
                    all_max_loc = max_loc
                    max_w, max_h = template.shape[:2]

            if all_max_val > threshold:
                cv2.rectangle(result, all_max_loc, (all_max_loc[0] + max_w, all_max_loc[1] + max_h), (255 * (signi == 0), 255 * (signi == 1), 255 * (signi == 2)), 2)

    total_time = time.time() - start_time
    print(f'Total time: {total_time:.2f}')
    return result
