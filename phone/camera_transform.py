import math
import random
import time

import cv2
import numpy as np

from settings import WIDTH, HEIGHT


def region_selection(image):
    mask = np.zeros_like(image)
    if len(image.shape) > 2:
        channel_count = image.shape[2]
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    rows, cols = image.shape[:2]

    bottom_left  = [cols * 0, rows * 0.8]
    top_left     = [cols * 0, rows * 0]
    bottom_right = [cols * 1, rows * 0.8]
    top_right    = [cols * 1, rows * 0]

    vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image


def hough_transform(canny_img, rho=1, theta=np.pi/180, threshold=10, minLineLength=5, maxLineGap=10):
    lines = cv2.HoughLinesP(canny_img, rho, theta, threshold,
                            np.array([]), minLineLength, maxLineGap)
    return lines


def make_bird_view(image):
    x_offset = 80
    y_offset = 80
    src_points = np.float32([
        [x_offset, 0],  # Top-left corner
        [WIDTH - x_offset, 0],  # Top-right corner
        [WIDTH, HEIGHT - y_offset],  # Bottom-right corner
        [0, HEIGHT - y_offset]  # Bottom-left corner
    ])

    # Define the destination points (where you want the source points to map to)
    # This should be a rectangle
    target_width = WIDTH
    target_height = HEIGHT
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

