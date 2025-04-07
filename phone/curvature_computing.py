import math
import random
import time

import cv2
import numpy as np

from settings import WIDTH, HEIGHT


def compute_curvature(chain, threshold_angle, max_angle_change, debug_image):
    if len(chain) < 3:
        return 0  # Too few points to calculate curvature

    total_angle_change = 0
    segment_count = 0

    for i in range(1, len(chain) - 1):
        p1, p2, p3 = np.array(chain[i - 1]), np.array(chain[i]), np.array(chain[i + 1])

        # Compute vectors
        v1 = p2 - p1  # Vector from p1 to p2
        v2 = p3 - p2  # Vector from p2 to p3

        # Normalize vectors
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            continue  # Skip degenerate cases

        unit_v1 = v1 / norm_v1
        unit_v2 = v2 / norm_v2

        # Compute angle using dot product
        dot_product = np.clip(np.dot(unit_v1, unit_v2), -1.0, 1.0)  # Avoid precision errors
        angle = np.degrees(np.arccos(dot_product))  # Convert radians to degrees

        # Compute direction using cross product (2D determinant)
        cross_product = np.cross(v1, v2)  # This gives signed area (left or right turn)

        # Assign negative sign if turning left (counterclockwise)
        if cross_product < 0:
            angle = -angle

        if abs(angle) > threshold_angle:
            mult = (p2[1] ** 0.5) / (HEIGHT ** 0.5)
            # print(mult)
            total_angle_change += angle / max_angle_change * mult
            segment_count += 1
            cv2.circle(debug_image, tuple(p2), 3, (255, 0, 255), -1)

    return total_angle_change / segment_count if segment_count > 0 else 0