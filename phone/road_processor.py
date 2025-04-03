import math
import random
import time

import cv2
import numpy as np

from camera_transform import make_bird_view
from points_finder import find_candidates, build_lane_components, draw_components
from settings import WIDTH, HEIGHT


def draw_points(image, lane_points, color):
    # Draw the points on the image (for visualization)
    for point in lane_points:
        cv2.circle(image, tuple(point), 3, color, -1)  # Draw green circles

    return image


def road_processor(rgb_image):
    start_time = time.time()
    # rgb_image = region_selection(rgb_image)
    # canny = cv2.Canny(gray_image, 220, 255)
    # lines = hough_transform(canny)

    # gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

    # rgb_image = make_bird_view(rgb_image)

    points = find_candidates(rgb_image, 0, HEIGHT, 5, 2, 150, 10)
    components = build_lane_components(points, 50, 30, 15)
    debug_image = draw_components(rgb_image, components)

    # debug_image = rgb_image.copy()
    # draw_points(debug_image, points, (0, 255, 0))

    return 0, 0, debug_image, time.time() - start_time

