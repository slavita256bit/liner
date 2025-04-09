import math
import random
import time

import cv2
import numpy as np

from settings import WIDTH, HEIGHT


def compute_angle_with_perp(prev_pt, current_pt, candidate_pt):
    """
    Computes the signed angle (in degrees) between the candidate vector and the perpendicular
    to the previous segment (from prev_pt to current_pt).

    The perpendicular is computed by rotating the previous segment 90° clockwise.

    Uses integer differences for pixel coordinates.

    Parameters:
        prev_pt, current_pt, candidate_pt (tuple): Points as (x, y).

    Returns:
        float: Signed angle in degrees. Positive means the candidate vector is rotated clockwise
               relative to the perpendicular; negative means counterclockwise.
    """
    # Compute vector from previous point to current point (as ints)
    vx = current_pt[0] - prev_pt[0]
    vy = current_pt[1] - prev_pt[1]
    # Perpendicular: rotate 90° clockwise --> (vy, -vx)
    perp_x, perp_y = vy, -vx
    # Vector from current point to candidate point
    cx = candidate_pt[0] - current_pt[0]
    cy = candidate_pt[1] - current_pt[1]

    # Compute norms using math.hypot (still returns float)
    norm_perp = math.hypot(perp_x, perp_y)
    norm_cand = math.hypot(cx, cy)
    if norm_perp == 0 or norm_cand == 0:
        return 0.0

    # Normalize the vectors
    unit_perp_x = perp_x / norm_perp
    unit_perp_y = perp_y / norm_perp
    unit_cand_x = cx / norm_cand
    unit_cand_y = cy / norm_cand

    # Dot product and determinant (2D cross product)
    dot = unit_perp_x * unit_cand_x + unit_perp_y * unit_cand_y
    det = unit_perp_x * unit_cand_y - unit_perp_y * unit_cand_x

    angle_rad = math.atan2(det, dot)
    return math.degrees(angle_rad)


def build_lane_chains(points, max_distance, sure_distance, max_angle_change, min_chain_size):
    """
    Builds chains of points starting from the lower points (largest y) going upward.

    For each unused point (starting from the bottom), the algorithm selects the nearest
    candidate point (by Euclidean distance) that lies above (has a smaller y value) and,
    if the chain already has two points and the candidate is not extremely close (>= sure_distance),
    ensures that the turning angle relative to the perpendicular of the previous segment is within
    a specified range. The candidate is rejected if its computed angle is not close enough to 90°,
    meaning it falls "under" the perpendicular.

    Parameters:
        points (list of tuples): List of points as (x, y).
        max_distance (float): Maximum Euclidean distance to consider connecting points.
        sure_distance (float): If candidate is closer than this, skip angle checks.
        max_angle_change (float): Maximum allowed deviation (in degrees) from 90°.
                                  (Candidate vector angle must be in: 90 - max_angle_change, 90 + max_angle_change).
        min_chain_size (int): Minimum points required in a chain to retain it.

    Returns:
        chains (list of lists): A list of chains; each chain is a list of points.
    """
    if not points:
        return []

    # Sort points by descending y (lower points first)
    sorted_points = sorted(points, key=lambda p: p[1], reverse=True)
    used = [False] * len(sorted_points)
    chains = []

    for i, pt in enumerate(sorted_points):
        if used[i]:
            continue
        chain = [pt]
        used[i] = True
        current_point = pt

        while True:
            candidate_index = None
            candidate_distance = None

            for j, other_pt in enumerate(sorted_points):
                if used[j]:
                    continue
                # Consider only points above the current point
                if other_pt[1] >= current_point[1]:
                    continue
                # Compute Euclidean distance using integer differences.
                dx = other_pt[0] - current_point[0]
                dy = other_pt[1] - current_point[1]
                dist = math.hypot(dx, dy)
                if dist > max_distance:
                    continue

                # For very close candidates, skip the angle check.
                if len(chain) < 2 or dist < sure_distance:
                    angle_ok = True
                else:
                    # Compute the turning angle relative to the perpendicular.
                    # Expected angle should be near 90°.
                    angle = compute_angle_with_perp(chain[-2], current_point, other_pt)
                    # Accept candidate if its angle lies within (90 - max_angle_change, 90 + max_angle_change).
                    angle_ok = (90 - max_angle_change) < angle < (90 + max_angle_change)
                if not angle_ok:
                    continue
                # Select candidate with smallest distance.
                if candidate_index is None or dist < candidate_distance:
                    candidate_index = j
                    candidate_distance = dist

            if candidate_index is None:
                break  # No candidate found; finish this chain.
            used[candidate_index] = True
            next_point = sorted_points[candidate_index]
            chain.append(next_point)
            current_point = next_point

        if len(chain) >= min_chain_size:
            chains.append(chain)
    return chains