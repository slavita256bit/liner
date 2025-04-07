import math
import random
import time

import cv2
import numpy as np

from settings import WIDTH, HEIGHT, ROBOT_X_CENTER


def filter_chains_by_robot_center(chains):
    best_left_chain = None
    best_right_chain = None
    min_left_dist = float('inf')
    min_right_dist = float('inf')

    robot_ref_point = (ROBOT_X_CENTER, HEIGHT - 1)

    for chain in chains:
        if not chain:
            continue
        # Find the bottom-most point (max y) in the chain
        bottom_point = max(chain, key=lambda pt: pt[1])

        # Euclidean distance to robot's center reference point
        dist = np.linalg.norm(np.array(bottom_point) - np.array(robot_ref_point))

        if bottom_point[0] < ROBOT_X_CENTER:
            if dist < min_left_dist:
                best_left_chain = chain
                min_left_dist = dist
        elif bottom_point[0] > ROBOT_X_CENTER:
            if dist < min_right_dist:
                best_right_chain = chain
                min_right_dist = dist

    filtered = [chain for chain in [best_left_chain, best_right_chain] if chain is not None]
    return filtered, best_left_chain, best_right_chain
