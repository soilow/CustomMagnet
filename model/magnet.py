import numpy as np
from matplotlib.path import Path

class Magnet:
    def __init__(self, points, positive_pole, negative_pole):
        self.points = points
        self.polygon = Path(points)
        self.positive_pole = np.array(positive_pole)
        self.negative_pole = np.array(negative_pole)
