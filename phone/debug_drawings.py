import math
import random
import time

import cv2
import numpy as np

from settings import WIDTH, HEIGHT, ROBOT_X_CENTER


def draw_chains(image, chains, point_color=(0, 0, 255), line_color=(0, 255, 0), thickness=2):
    """
    Рисует на изображении компоненты, соединяя точки линиями и отмечая точки кружками.

    Параметры:
        image (np.ndarray): Исходное изображение.
        chains (list of lists): Список компонент, каждая – список точек (x, y).
        point_color (tuple): Цвет точек.
        line_color (tuple): Цвет линий.
        thickness (int): Толщина линий.
    """
    for comp in chains:
        # Сортируем компоненты по y, чтобы соединять сверху вниз (если нужно)
        comp_sorted = sorted(comp, key=lambda p: p[1])
        for i in range(len(comp_sorted) - 1):
            cv2.line(image, comp_sorted[i], comp_sorted[i + 1], line_color, thickness)
        for p in comp_sorted:
            cv2.circle(image, p, 3, point_color, -1)
    return image


def draw_points(image, lane_points, color):
    image = image.copy()

    # Draw the points on the image (for visualization)
    for point in lane_points:
        cv2.circle(image, tuple(point), 3, color, -1)  # Draw green circles

    return image


def draw_robot_center_marker(img, triangle_size=20, color=(0, 0, 255)):
    height, width = img.shape[:2]
    base_y = height - 1

    # Define the three triangle points
    pt_top = (ROBOT_X_CENTER, base_y - triangle_size)
    pt_left = (ROBOT_X_CENTER - triangle_size // 2, base_y)
    pt_right = (ROBOT_X_CENTER + triangle_size // 2, base_y)

    # Create triangle using fillPoly
    triangle_cnt = np.array([pt_top, pt_right, pt_left])
    cv2.fillPoly(img, [triangle_cnt], color)
