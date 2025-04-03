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
    target_width = width
    target_height = height
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


import cv2
import numpy as np


def find_black_candidates(img, yl, yr, step, radius, black_threshold, max_x_dist):
    merged_points = []  # To store the merged (x, y) candidates.
    height, width = img.shape

    # Process rows from yl to yr with given step
    for y in range(yl, min(yr, height), step):
        candidates = []  # Temporary list for candidate x positions on this y-line

        # Process every x in the row
        for x in range(width):
            # Define the square boundaries ensuring we don't go out of image bounds.
            x_start = max(0, x - radius)
            x_end = min(width, x + radius + 1)
            y_start = max(0, y - radius)
            y_end = min(height, y + radius + 1)

            # Extract the region and compute the average intensity.
            region = img[y_start:y_end, x_start:x_end]
            avg_intensity = np.mean(region)

            # If the region is dark enough, mark x as a candidate.
            if avg_intensity < black_threshold:
                candidates.append(x)

        # Merge candidates that are within max_x_dist
        if candidates:
            merged_candidates = []
            # Initialize the first group
            group = [candidates[0]]

            for curr in candidates[1:]:
                # If the distance from the last candidate in the group is small enough, add to group
                if curr - group[-1] <= max_x_dist:
                    group.append(curr)
                else:
                    # Merge the current group: average x coordinate
                    merged_candidates.append(int(np.mean(group)))
                    group = [curr]
            # Merge the final group
            if group:
                merged_candidates.append(int(np.mean(group)))

            # Append merged candidates with the current y coordinate.
            for merged_x in merged_candidates:
                merged_points.append((merged_x, y))

    return merged_points


def draw_debug_info(image, lane_points):
    debug_image = image.copy()

    # Draw the points on the image (for visualization)
    for point in lane_points:
        cv2.circle(debug_image, tuple(point), 3, (0, 255, 0), -1)  # Draw green circles

    return debug_image


def road_processor(rgb_image):
    start_time = time.time()
    # rgb_image = region_selection(rgb_image)
    # canny = cv2.Canny(gray_image, 220, 255)
    # lines = hough_transform(canny)

    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

    # rgb_image = make_bird_view(rgb_image)

    points = find_black_candidates(gray_image, 0, height, 10, 5, 20, 10)

    debug_image = draw_debug_info(rgb_image, points)

    return 0, 0, debug_image, time.time() - start_time
