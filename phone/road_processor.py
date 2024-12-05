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
    bottom_left  = [cols * 0, rows * 0.6]
    top_left     = [cols * 0.1, rows * 0.3]
    bottom_right = [cols * 1, rows * 0.6]
    top_right    = [cols * 0.9, rows * 0.3]
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
    threshold = 20
    # Line segments shorter than that are rejected.
    minLineLength = 1
    # Maximum allowed gap between points on the same line to link them
    maxLineGap = 30
    # function returns an array containing dimensions of straight lines
    # appearing in the input image
    return cv2.HoughLinesP(image, rho=rho, theta=theta, threshold=threshold,
                           minLineLength=minLineLength, maxLineGap=maxLineGap)


def make_bird_view(image):
    x_offset = 105
    y_offset = 40
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
    rgb_image = make_bird_view(rgb_image)
    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

    canny = cv2.Canny(gray_image, 220, 255)
    # region = region_selection(canny)
    # region = canny
    lines = hough_transform(canny)

    # for line in lines:
    #     for x1, y1, x2, y2 in line:
    #         color = (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
    #         cv2.line(rgb_image, (x1, y1), (x2, y2), color, 2)

    # if lines is not None:
    #     mid = average_slope_intercept(gray_image.shape[1], lines)
    #     print(mid)

    center_x = 205

    pt1 = (center_x - 10, height)
    pt2 = (center_x, height - 10)
    pt3 = (center_x + 10, height)

    triangle_cnt = np.array([pt1, pt2, pt3])

    cv2.drawContours(canny, [triangle_cnt], 0, (0, 255, 0), -1)

    print("done")
    return canny
