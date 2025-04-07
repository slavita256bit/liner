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

    The perpendicular is computed by rotating the previous segment by 90° clockwise.

    Parameters:
        prev_pt, current_pt, candidate_pt (tuple): Points as (x, y).

    Returns:
        float: Signed angle in degrees. Positive for candidate vector rotated clockwise
               relative to the perpendicular, negative for counterclockwise.
    """
    # Vector from previous point to current point
    v = np.array(current_pt) - np.array(prev_pt)
    # Compute perpendicular by rotating v by 90° clockwise: (x, y) -> (y, -x)
    perp = np.array([v[1], -v[0]])
    # Vector from current point to candidate point
    cand_vec = np.array(candidate_pt) - np.array(current_pt)

    # Normalize both vectors
    norm_perp = np.linalg.norm(perp)
    norm_cand = np.linalg.norm(cand_vec)
    if norm_perp == 0 or norm_cand == 0:
        return 0.0
    unit_perp = perp / norm_perp
    unit_cand = cand_vec / norm_cand

    # Compute dot and determinant for signed angle
    dot = np.dot(unit_perp, unit_cand)
    # Determinant (2D cross product)
    det = unit_perp[0] * unit_cand[1] - unit_perp[1] * unit_cand[0]

    angle_rad = np.arctan2(det, dot)
    angle_deg = np.degrees(angle_rad)
    return angle_deg

def build_lane_chains(points, max_distance, sure_distance, max_angle_change, min_chain_size):
    """
    Builds chains (chains) of points starting from the lower points.
    For each unused point (starting from the bottom), it attempts to connect upward by
    choosing the nearest point (by Euclidean distance) that lies above and whose connection
    does not exceed the allowed turning angle.

    The turning angle is computed as the angle between the candidate vector and the perpendicular
    to the previous segment. For the first or second point in a chain, the angle is set to zero.

    Additionally, if the chain already has at least two points, the candidate point is rejected
    if it lies "under" the perpendicular (i.e. its vector from the current point projects negatively
    on the perpendicular of the previous segment).

    Parameters:
        points (list of tuples): List of points (x, y).
        max_distance (float): Maximum Euclidean distance between points for connection.
        sure_distance (float): Distance threshold below which we assume points can be connected without angle checks.
        max_angle_change (float): Maximum allowed turning angle (in degrees) between the candidate
                                  vector and the perpendicular of the previous segment.
        min_chain_size (int): Minimum number of points required in a chain; otherwise, it is discarded.

    Returns:
        chains (list of lists): A list of chains, each chain is a list of points.
    """
    if not points:
        return []

    # In image coordinates y increases downward; lower points have larger y.
    sorted_points = sorted(points, key=lambda p: p[1], reverse=True)

    used = [False] * len(sorted_points)
    chains = []

    # For each point (starting from the bottom), if it hasn't been used, build a chain upward.
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
                # Consider only points that lie above (smaller y value)
                if other_pt[1] >= current_point[1]:
                    continue

                dist = np.linalg.norm(np.array(other_pt) - np.array(current_point))
                if dist > max_distance:
                    continue

                # If the points are very close (within sure_distance), we can be more lenient.
                if len(chain) < 2 or dist < sure_distance:
                    angle_ok = True
                else:
                    # Compute the perpendicular vector from the previous segment.
                    prev_pt = chain[-2]
                    v = np.array(current_point) - np.array(prev_pt)
                    perp = np.array([v[1], -v[0]])
                    cand_vec = np.array(other_pt) - np.array(current_point)
                    # Check that candidate is not "under" the perpendicular.
                    # Compute the turning angle relative to the perpendicular.
                    angle = compute_angle_with_perp(prev_pt, current_point, other_pt)
                    angle_ok = (90 - max_angle_change < angle < 90 + max_angle_change)

                if not angle_ok:
                    continue

                # Choose the candidate with the smallest distance among those that pass.
                if candidate_index is None or dist < candidate_distance:
                    candidate_index = j
                    candidate_distance = dist

            if candidate_index is None:
                # No suitable candidate found; finish this chain.
                break

            used[candidate_index] = True
            next_point = sorted_points[candidate_index]
            chain.append(next_point)
            current_point = next_point

        if len(chain) >= min_chain_size:
            chains.append(chain)

    return chains