import dijkstar
import random
import pytest
from tqdm import trange


# The problem to solve is the minimum number of time steps needed
# for a vehicle to drive a distance:
#   The vehicle is a point on a line
#   The positions on the line are quantised to 'scale'
#   The distance is 'distance' in meters
#   The maximum distance the vehicle can travel is 'max_distance'
#   The time step is 'delta_time' in units of seconds
#   The vehicles initial speed is 'initial_speed'
#   The vehicles final speed at 'distance' is 'final_speed'
#   Valid speeds are [-N*ds, -(N-1)ds, -(N-2)ds ... 0 ... (N-1)ds, N*ds]
#       where ds is 'delta_speed'
#       max_speed = delta_speed * N
#       where the total number of valid speeds are 2N + 1
#   In each time step the vehicle may:
#       accelerate at 'acceleration' = delta_speed/delta_time
#       decelerate at 'deceleration' = -delta_speed/delta_time
#           NB: Decelerating to a more negative speed is accelerating in reverse
#       brake at +/- (N * delta_speed) / (1 / delta_time)
#           i.e. come to a stop in 1 second from +/- maximum speed
#       take no action
#           i.e. continue at the same speed
DELTA_TIME = 0.1
ACCELERATION = 2.0
SCALE = 0.05
MAX_DISTANCE = 50.0
assert(1.0 / DELTA_TIME == int(1.0 / DELTA_TIME))
assert(1.0 / SCALE == int (1.0 / SCALE))

N = int(1 * (1 / DELTA_TIME))
DECELERATION = -ACCELERATION
DELTA_SPEED = ACCELERATION * DELTA_TIME
MAX_SPEED = N * DELTA_SPEED
BRAKING_DECELERATION = -MAX_SPEED
MAX_X = int(MAX_DISTANCE / SCALE)
assert(MAX_X < 16384)
assert(N < 128)


# A node number for every position and speed
def xn_to_node_num(x, n):
    return ((x + MAX_X) << 8) | (n + N)


def node_num_to_xn(node_num):
    n = (node_num & 0xFF) - N
    x = ((node_num >> 8) & 0xFFFF) - MAX_X
    return x, n


def create_graph():
    graph = dijkstar.Graph()
    for x in trange(-MAX_X, MAX_X + 1):
        for n in range(-N, N + 1):
            current_node = xn_to_node_num(x, n)

            # Accelerate
            if n != N:
                distance = n * DELTA_SPEED * DELTA_TIME + 0.5 * ACCELERATION * DELTA_TIME ** 2
                distance = round(distance / SCALE)
                next_node = xn_to_node_num(x + distance, n + 1)
                graph.add_edge(current_node, next_node, 1.0)

            # Decelerate
            if n != -N:
                distance = n * DELTA_SPEED * DELTA_TIME + 0.5 * DECELERATION * DELTA_TIME ** 2
                distance = round(distance / SCALE)
                next_node = xn_to_node_num(x + distance, n - 1)
                graph.add_edge(current_node, next_node, 1.0)

            # Brake
            if n != 0:
                braking_time = min((abs(n * DELTA_SPEED / BRAKING_DECELERATION), DELTA_TIME))
                sign = 1.0 if n > 0 else -1.0
                distance = n * DELTA_SPEED * braking_time + 0.5 * sign * BRAKING_DECELERATION * braking_time ** 2
                distance = round(distance / SCALE)
                next_speed = round((n * DELTA_SPEED + BRAKING_DECELERATION * braking_time * sign) / DELTA_SPEED)
                next_node = xn_to_node_num(x + distance, next_speed)
                graph.add_edge(current_node, next_node, 1.0)

            # Do nothing
            distance = n * DELTA_SPEED * DELTA_TIME
            distance = round(distance / SCALE)
            next_node = xn_to_node_num(x + distance, n)
            graph.add_edge(current_node, next_node, 1.0)

    return graph


# Global
graph = create_graph()


@pytest.mark.parametrize("initial_speed, profile", [
    (0, "aaaadddd"),
    (0, "aaaaaaaaaannnnnnnnnnbbbbbbbbbb"),
    (0, "ddddddaaaaaa"),
    (0, "ddddddddddnnnnnnnnnnnnnnnnnnnbbbbbbbbbb"),
    (-4, "bbbbaaaa"),
    (4, "aaaaaannnnnnnnnnbbbbbbbbbbdddd")
])
def test_known_costs(initial_speed, profile):
    s = 0
    u = initial_speed * DELTA_SPEED
    t = DELTA_TIME
    for action in profile:
        if action == 'a':
            s += round((u * t + 0.5 * ACCELERATION * t ** 2) / SCALE)
            u = min(u + ACCELERATION * t, MAX_SPEED)
        if action == 'd':
            s += round((u * t + 0.5 * DECELERATION * t ** 2) / SCALE)
            u = max((u + DECELERATION * t, -MAX_SPEED))
        if action == 'n':
            s += round((u * t) / SCALE)
        if action == 'b':
            braking_time = min((abs(u / BRAKING_DECELERATION), DELTA_TIME))
            sign = 1.0 if u > 0 else -1.0
            s += round((u * braking_time + 0.5 * sign * BRAKING_DECELERATION * braking_time ** 2) / SCALE)
            u = u + sign * BRAKING_DECELERATION * braking_time

    # Now find the shortest path to that same position & speed and verify the cost
    # is the same as the length of the list of actions
    # NOTE: We do not check the actions are the same as some actions have the same effect
    # with certain parameters e.g. braking and deceleration. There is also a rounding effect
    # that may mean that different speeds result in the same positions.
    initial_node = xn_to_node_num(0, initial_speed)
    finish_node = xn_to_node_num(s, round(u / DELTA_SPEED))
    heuristic_func = lambda u, v, prev_e, e: abs((s - node_num_to_xn(v)[0])) / (MAX_SPEED / SCALE)
    path = dijkstar.find_path(graph, initial_node, finish_node, heuristic_func=heuristic_func)
    assert(len(profile) == path[3])
