from settings import ROBOT_X_CENTER


def get_nearest_x(chain, target_y):
    """
    Given a chain (list of (x, y) points), returns the x coordinate of the point
    whose y value is closest to target_y.
    """
    # A simple linear search is fine if the chain is short.
    best_pt = min(chain, key=lambda pt: abs(pt[1] - target_y))
    return best_pt[0]


def build_middle_chain(left_chain, right_chain,
                       left_default_x, right_default_x,
                       middle_chain_delta, y_bottom):
    """
    Build a middle chain from the left and right chains.

    Points are generated every middle_chain_delta pixels in y, moving from y_bottom (down)
    to y_top (up). The first point is explicitly set to (ROBOT_X_CENTER, y_bottom).
    For every other point, the x coordinate is computed as the average of the nearest
    left and right x coordinates at that y. If one of the chains is empty, the default
    value (left_default_x or right_default_x) is used.

    Parameters:
        left_chain (list of tuples): Points (x, y) from the left chain, sorted from down to up.
        right_chain (list of tuples): Points (x, y) from the right chain, sorted from down to up.
        left_default_x (number): Default x for the left chain if none exists.
        right_default_x (number): Default x for the right chain if none exists.
        middle_chain_delta (number): Vertical spacing (in pixels) between middle chain points.
        y_bottom (number): Starting y value (bottom of the image).

    Returns:
        list of tuples: The generated middle chain as (x, y) points.
    """
    # Determine y_top based on the available chains
    y_top_candidates = []
    if left_chain:
        y_top_candidates.append(min(y for _, y in left_chain))
    if right_chain:
        y_top_candidates.append(min(y for _, y in right_chain))

    # If both chains are empty, default to stopping immediately
    if not y_top_candidates:
        return [(ROBOT_X_CENTER, y_bottom)]

    y_top = max(y_top_candidates)

    middle_chain = []
    current_y = y_bottom

    # The first point: use ROBOT_X_CENTER.
    middle_chain.append((ROBOT_X_CENTER, current_y))
    current_y -= middle_chain_delta

    while current_y >= y_top:
        if left_chain:
            left_x = get_nearest_x(left_chain, current_y)
        else:
            left_x = left_default_x

        if right_chain:
            right_x = get_nearest_x(right_chain, current_y)
        else:
            right_x = right_default_x

        mid_x = (left_x + right_x) // 2
        middle_chain.append((mid_x, current_y))
        current_y -= middle_chain_delta

    return middle_chain