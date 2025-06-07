import numpy as np

def calculate_field(magnets, X, Y, intensity):
    Bx = np.zeros_like(X)
    By = np.zeros_like(Y)
    points_grid = np.vstack((X.flatten(), Y.flatten())).T

    for magnet in magnets:
        M_dir = magnet.negative_pole - magnet.positive_pole
        M_dir = M_dir / np.linalg.norm(M_dir)

        inner_x = np.linspace(-6, 6, 40)
        inner_y = np.linspace(-6, 6, 40)
        IX, IY = np.meshgrid(inner_x, inner_y)
        I_points = np.vstack((IX.flatten(), IY.flatten())).T
        inside = magnet.polygon.contains_points(I_points)
        internal_sources = I_points[inside]

        for source in internal_sources:
            dx = X - source[0]
            dy = Y - source[1]
            r2 = dx**2 + dy**2 + 0.3
            r = np.sqrt(r2)
            rx = dx / r
            ry = dy / r
            dot = rx * M_dir[0] + ry * M_dir[1]

            Bx += intensity * (3 * dot * rx - M_dir[0]) / r2**1.5
            By += intensity * (3 * dot * ry - M_dir[1]) / r2**1.5

        mask = ~magnet.polygon.contains_points(points_grid).reshape(X.shape)
        Bx[~mask] = np.nan
        By[~mask] = np.nan

    return Bx, By
