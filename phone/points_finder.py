import math
import random
import time

import cv2
import numpy as np

from dsu import DisjointSet
from settings import WIDTH, HEIGHT


def compute_angle(p1, p2):
    """Compute the angle (in degrees) of the line segment from p1 to p2 relative to vertical."""
    # Avoid division by zero: use a small epsilon
    epsilon = 1e-6
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1] + epsilon
    # angle relative to vertical axis:
    angle_rad = math.atan(dx / dy)
    return math.degrees(angle_rad)


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


def build_lane_components(points, max_distance=50, max_angle_change=20, min_component_size=5):
    """
    Строит компоненты (цепочки) точек, начиная с нижних точек.
    Для каждой еще не объединенной точки выбирается следующая точка, лежащая выше (y меньше),
    ближайшая по расстоянию и удовлетворяющая условию на угол между сегментами.

    Параметры:
        points (list of tuples): Список точек (x, y).
        max_distance (float): Максимальное расстояние между точками для соединения.
        max_angle_change (float): Максимальное допустимое изменение угла (в градусах)
                                  между предыдущим сегментом и новым.
        min_component_size (int): Минимальное количество точек в компоненте, иначе она отбрасывается.

    Возвращает:
        components (list of lists): Список компонентов, каждая компонента – список точек.
    """
    if not points:
        return []

    # Отметим, что в координатах изображения y увеличивается вниз,
    # поэтому "нижние" точки – это те, у которых y больше.
    # Сортируем точки по убыванию y (начинаем с самых нижних)
    sorted_points = sorted(points, key=lambda p: p[1], reverse=True)

    used = [False] * len(sorted_points)
    components = []

    # Для каждой точки, начиная с нижней, если она ещё не входит в компоненту,
    # строим цепочку вверх.
    for i, pt in enumerate(sorted_points):
        if used[i]:
            continue
        component = [pt]
        used[i] = True
        current_point = pt
        # Начальное направление можно задать вертикально вверх (например, угол 90°)
        prev_angle = 90

        while True:
            candidate_index = None
            candidate_distance = None
            candidate_angle = None

            # Ищем среди оставшихся точек ту, которая лежит выше (y меньше),
            # находится не слишком далеко и при этом угол между сегментами не слишком большой.
            for j, other_pt in enumerate(sorted_points):
                if used[j]:
                    continue
                # Чтобы точка была выше: её y должно быть меньше текущего.
                if other_pt[1] >= current_point[1]:
                    continue
                # Расстояние между точками
                dist = np.linalg.norm(np.array(other_pt) - np.array(current_point))
                if dist > max_distance:
                    continue
                # Вычисляем угол сегмента от текущей точки к кандидату.
                angle = compute_angle(current_point, other_pt)
                # Если цепочка уже имеет хотя бы 2 точки, проверяем изменение угла.
                if len(component) >= 2:
                    angle_diff = abs(angle - prev_angle)
                    # Если разница углов превышает допустимое значение – пропускаем.
                    if angle_diff > max_angle_change:
                        continue
                # Выбираем ближайшего кандидата, удовлетворяющего условиям.
                if candidate_index is None or dist < candidate_distance:
                    candidate_index = j
                    candidate_distance = dist
                    candidate_angle = angle

            if candidate_index is None:
                # Больше подходящих точек не найдено, завершаем цепочку.
                break
            # Добавляем найденную точку в компоненту и обновляем параметры.
            used[candidate_index] = True
            next_point = sorted_points[candidate_index]
            component.append(next_point)
            prev_angle = candidate_angle
            current_point = next_point

        # Добавляем компоненту, если она содержит достаточное число точек.
        if len(component) >= min_component_size:
            components.append(component)

    return components


def draw_components(image, components, point_color=(0, 0, 255), line_color=(0, 255, 0), thickness=2):
    """
    Рисует на изображении компоненты, соединяя точки линиями и отмечая точки кружками.

    Параметры:
        image (np.ndarray): Исходное изображение.
        components (list of lists): Список компонент, каждая – список точек (x, y).
        point_color (tuple): Цвет точек.
        line_color (tuple): Цвет линий.
        thickness (int): Толщина линий.

    Возвращает:
        output_img (np.ndarray): Изображение с нарисованными компонентами.
    """
    output_img = image.copy()
    for comp in components:
        # Сортируем компоненты по y, чтобы соединять сверху вниз (если нужно)
        comp_sorted = sorted(comp, key=lambda p: p[1])
        for i in range(len(comp_sorted) - 1):
            cv2.line(output_img, comp_sorted[i], comp_sorted[i + 1], line_color, thickness)
        for p in comp_sorted:
            cv2.circle(output_img, p, 3, point_color, -1)
    return output_img

