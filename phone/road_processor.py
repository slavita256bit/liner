import math
import random
import time

import cv2
import numpy as np

from camera_transform import make_bird_view, region_selection
from chains_generator import build_lane_chains
from curvature_computing import compute_curvature
from debug_drawings import draw_points, draw_chains, draw_robot_center_marker
from filter_chains import filter_chains_by_robot_center
from middle_chain import build_middle_chain
from points_finder import find_candidates
from settings import WIDTH, HEIGHT, ROBOT_X_CENTER


def road_processor(rgb_image):
    start_time = time.time()
    # rgb_image = region_selection(rgb_image)
    # canny = cv2.Canny(gray_image, 220, 255)
    # lines = hough_transform(canny)

    # gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

    rgb_image = make_bird_view(rgb_image)

    points = find_candidates(rgb_image, 0, HEIGHT, 5, 2, 180, 10)
    debug_image = draw_points(rgb_image, points, (255, 100, 0))

    max_angle_change = 40
    chains = build_lane_chains(points, 65, 10, max_angle_change, 0)


    chains, left_chain, right_chain = filter_chains_by_robot_center(chains, 50, 8)

    # for chain in chains:
    #     chain.sort(key=lambda pos: pos[1])
    #     last_x, _ = chain[-1]
    #     chain.append((last_x, HEIGHT))

    draw_chains(debug_image, chains)

    avg_curvature = 0
    # for chain in chains:
    #     avg_curvature += compute_curvature(chain)
    #
    # if len(chains) > 0:
    #     avg_curvature /= len(chains)

    MAX_LANE_OFFSET = 100
    middle_chain = build_middle_chain(left_chain, right_chain, ROBOT_X_CENTER - MAX_LANE_OFFSET, ROBOT_X_CENTER + MAX_LANE_OFFSET, 10, HEIGHT)

    draw_robot_center_marker(debug_image)

    draw_chains(debug_image, [middle_chain], point_color=(0, 20, 100), line_color=(20, 100, 0))

    N_TH_POINT = min(3, len(middle_chain)) - 1
    delta = middle_chain[N_TH_POINT][0] - ROBOT_X_CENTER

    # inf_delta = 1000
    # if left_chain is None:
    #     delta = -inf_delta
    #
    # if right_chain is None:
    #     delta = inf_delta

    return avg_curvature, delta, debug_image, time.time() - start_time

