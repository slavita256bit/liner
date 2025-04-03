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


def hough_transform(canny_img, rho=1, theta=np.pi/180, threshold=10, minLineLength=5, maxLineGap=10):
    lines = cv2.HoughLinesP(canny_img, rho, theta, threshold,
                            np.array([]), minLineLength, maxLineGap)
    return lines


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


def compute_curvature(lines, image_shape, xm_per_pix=1.0, ym_per_pix=1.0):
    if lines is None:
        return None

    # Collect all endpoints of the detected line segments.
    points = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            points.append((x1, y1))
            points.append((x2, y2))

    # Check if we have enough points to fit a polynomial.
    if len(points) < 10:
        return None

    points = np.array(points)
    x = points[:, 0]
    y = points[:, 1]

    # If needed, convert from pixel space to real-world space.
    x = x * xm_per_pix
    y = y * ym_per_pix

    # Fit a second order polynomial: x = A*y^2 + B*y + C.
    fit = np.polyfit(y, x, 2)
    A, B, _ = fit

    # Evaluate curvature at the bottom of the image.
    # In a bird's-eye view, y typically increases from top to bottom.
    y_eval = image_shape[0] * ym_per_pix

    # Calculate the curvature using the formula:
    # R = (1 + (2*A*y_eval + B)^2)^(3/2) / |2*A|
    curvature = ((1 + (2 * A * y_eval + B) ** 2) ** 1.5) / np.abs(2 * A)
    return curvature


def draw_debug_info(image, lines):
    debug_image = image.copy()

    # Draw detected lines
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(debug_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return debug_image


def road_processor(rgb_image):
    start_time = time.time()

    # rgb_image = region_selection(rgb_image)
    rgb_image = make_bird_view(rgb_image)
    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

    canny = cv2.Canny(gray_image, 220, 255)
    lines = hough_transform(canny)

    # center_x = 205
    # left_lanes = []
    # right_lanes = []
    #
    # if lines is not None:
    #     for line in lines:
    #         color = (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
    #
    #         mx1, my1, mx2, my2 = line[0]
    #         for x1, y1, x2, y2 in line:
    #             mx1 = min(mx1, x1)
    #             mx2 = max(mx2, x2)
    #             my1 = min(my1, y1)
    #             my2 = max(my2, y2)
    #
    #         if abs(mx2 - mx1) - abs(my2 - my1) > 10:
    #             continue
    #
    #         if mx1 < center_x:
    #             left_lanes.append(mx1)
    #         else:
    #             right_lanes.append(mx1)
    #
    #         cv2.line(rgb_image, (mx1, my1), (mx2, my2), color, 2)
    #
    # not_exist_offset = 200
    #
    # if len(left_lanes) == 0:
    #     avg_left_lane = center_x - not_exist_offset
    # else:
    #     avg_left_lane = sum(left_lanes) / len(left_lanes)
    #
    # if len(right_lanes) == 0:
    #     avg_right_lane = center_x + not_exist_offset
    # else:
    #     avg_right_lane = sum(right_lanes) / len(right_lanes)
    #
    # pt1 = (center_x - 10, height)
    # pt2 = (center_x, height - 10)
    # pt3 = (center_x + 10, height)
    #
    # triangle_cnt = np.array([pt1, pt2, pt3])
    #
    # cv2.drawContours(rgb_image, [triangle_cnt], 0, (0, 255, 0), -1)
    #
    # delta = (avg_right_lane + avg_left_lane) // 2 - center_x
    #
    # cv2.line(rgb_image, (int(delta + center_x), height), (int(delta + center_x), height - 100), (0, 0, 255), 2)

    curvature = compute_curvature(lines, rgb_image.shape)

    debug_image = draw_debug_info(rgb_image, lines)

    return curvature, 0, debug_image, time.time() - start_time
