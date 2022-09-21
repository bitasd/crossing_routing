import math
from shapely.geometry import LineString
"""
code to calculate accessibility decay based on detour from the shortest path
"""
def decay_func( L_lts4, Lijk):  # add 8000 meter cut-off here
    """
    :param L_lts4: shortest path in meters from the origin to the current point no restriction on LTS or Steepness Level
    :param Lijk: shortest path in meters with restriction on LTS and LS
    :return: decay/ propensity of accessibility
    """
    if not L_lts4: # no shortest path available, topology error or point on highway
        return -8888

    else:

        if Lijk:  # there is a shortest path and there is a path under the current scenario

            L_lts4, Lijk = L_lts4/1609.34, Lijk/1609.34  # transform to miles
            l1 = min(4, 1.2 * L_lts4)  # d1
            l2 = 1.2 * L_lts4   # d2   changed from 1.33
            l3 = 1.6 * L_lts4  # d3   changed from 2

            if Lijk <= l1:
                return 1

            elif Lijk <= l2:
                return math.exp(-0.231*(Lijk - l1))

            elif Lijk <= l3:
                return math.exp(-0.231*(Lijk - l1))*(l3 - Lijk)/(l3 - l2)

            elif Lijk > l3:
                return 0

        elif not Lijk:  # no shortest path under the current scenario
            return -9999


def make_route_line(coords):
        if isinstance(coords, list) and len(coords) > 1:
            return LineString(coords)
        else:
            return None


def short_segments_smoothen(length: float, attr):   # attr can be lts or slope
    if length<51:
        return 0
    else:
        return attr


def midpoint( x1, y1, x2, y2):
    return [(x1 + x2) / 2, (y1 + y2) / 2]