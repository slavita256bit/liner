import math
import random
import time

import cv2
import numpy as np

from settings import WIDTH, HEIGHT


def find_candidates(img, yl, yr, step, radius, color_threshold, max_x_dist):
    """
    Optimized candidate finder that uses a pre-blurred image to compute local average color.

    Parameters:
        img (np.ndarray): Input image (BGR).
        yl (int): Starting y coordinate.
        yr (int): Ending y coordinate.
        step (int): Step size for iterating y values.
        radius (int): Radius of the square window.
        color_threshold (array-like): Threshold for each channel.
        max_x_dist (int): Maximum distance between candidate x positions for merging.

    Returns:
        list: List of merged candidate points as (x, y) tuples.
    """
    merged_points = []
    height, width, _ = img.shape

    # Precompute blurred image with kernel size (2*radius+1, 2*radius+1)
    kernel_size = (2 * radius + 1, 2 * radius + 1)
    blurred = cv2.blur(img, kernel_size)

    # Process rows from yl to yr with given step
    for y in range(yl, min(yr, height), step):
        # Get the blurred row; shape: (width, channels)
        row = blurred[y]
        # Create a boolean mask where all channels exceed the threshold.
        # Assuming color_threshold is an array-like of 3 values.
        mask = np.all(row > color_threshold, axis=1)
        # Find candidate x indices using the mask
        candidates = np.where(mask)[0]
        if candidates.size == 0:
            continue

        # Merge candidates: group x values that are close together (difference <= max_x_dist)
        diff = np.diff(candidates)
        groups = np.split(candidates, np.where(diff > max_x_dist)[0] + 1)
        for group in groups:
            merged_x = int(np.mean(group))
            merged_points.append((merged_x, y))

    return merged_points

