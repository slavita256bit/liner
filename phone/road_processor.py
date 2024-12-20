import math
import random
import time

import cv2
import numpy as np

width = 320
height = 240


def region_selection(image):
    mask = np.zeros_like(image)
    if len(image.shape) > 2:
        channel_count = image.shape[2]
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255
    rows, cols = image.shape[:2]
    print(image.shape)
    bottom_left  = [cols * 0.3, rows * 1]
    top_left     = [cols * 0.3, rows * 0]
    bottom_right = [cols * 1, rows * 1]
    top_right    = [cols * 1, rows * 0]
    vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image


def hough_transform(image):
    # Distance resolution of the accumulator in pixels.
    rho = 1
    # Angle resolution of the accumulator in radians.
    theta = np.pi / 180
    # Only lines that are greater than threshold will be returned.
    threshold = 10
    # Line segments shorter than that are rejected.
    minLineLength = 6
    # Maximum allowed gap between points on the same line to link them
    maxLineGap = 60
    # function returns an array containing dimensions of straight lines
    # appearing in the input image
    return cv2.HoughLinesP(image, rho=rho, theta=theta, threshold=threshold,
                           minLineLength=minLineLength, maxLineGap=maxLineGap)


def make_bird_view(image):
    x_offset = 100
    y_offset = 75
    src_points = np.float32([
        [x_offset, 0],  # Top-left corner
        [width - x_offset, 0],  # Top-right corner
        [width, height - y_offset],  # Bottom-right corner
        [0, height - y_offset]  # Bottom-left corner
    ])

    # Define the destination points (where you want the source points to map to)
    # This should be a rectangle
    target_width = 320
    target_height = 240
    dst_points = np.float32([
        [0, 0],  # Top-left corner
        [target_width, 0],  # Top-right corner
        [target_width, target_height],  # Bottom-right corner
        [0, target_height]  # Bottom-left corner
    ])

    # Compute the perspective transform matrix
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # Perform the perspective warp
    bird_view = cv2.warpPerspective(image, matrix, (target_width, target_height))
    return bird_view


def road_processor(rgb_image):
    start_time = time.time()

    # rgb_image = region_selection(rgb_image)
    rgb_image = make_bird_view(rgb_image)
    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

    canny = cv2.Canny(gray_image, 220, 255)
    lines = hough_transform(canny)

    center_x = 205
    left_lanes = []
    right_lanes = []

    if lines is not None:
        for line in lines:
            color = (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))

            mx1, my1, mx2, my2 = line[0]
            for x1, y1, x2, y2 in line:
                mx1 = min(mx1, x1)
                mx2 = max(mx2, x2)
                my1 = min(my1, y1)
                my2 = max(my2, y2)

            if abs(mx2 - mx1) - abs(my2 - my1) > 10:
                continue

            if mx1 < center_x:
                left_lanes.append(mx1)
            else:
                right_lanes.append(mx1)

            cv2.line(rgb_image, (mx1, my1), (mx2, my2), color, 2)

    not_exist_offset = 200

    if len(left_lanes) == 0:
        avg_left_lane = center_x - not_exist_offset
    else:
        avg_left_lane = sum(left_lanes) / len(left_lanes)

    if len(right_lanes) == 0:
        avg_right_lane = center_x + not_exist_offset
    else:
        avg_right_lane = sum(right_lanes) / len(right_lanes)

    pt1 = (center_x - 10, height)
    pt2 = (center_x, height - 10)
    pt3 = (center_x + 10, height)

    triangle_cnt = np.array([pt1, pt2, pt3])

    cv2.drawContours(rgb_image, [triangle_cnt], 0, (0, 255, 0), -1)

    delta = (avg_right_lane + avg_left_lane) // 2 - center_x

    cv2.line(rgb_image, (int(delta + center_x), height), (int(delta + center_x), height - 100), (0, 0, 255), 2)

    return 0, delta, rgb_image, time.time() - start_time
