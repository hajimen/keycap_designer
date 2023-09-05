import numpy as np

W, H = 1040, 151
CX = W // 2
CY = 75
L1_X = 80

LEFT = np.array([
    [[-1, 25], [-1, -1]],
    [[20, CY], [-1, CY + 10]],
    [[20, H], [-1, H + 55]],
    [[L1_X, -1], [L1_X, -10]],
    [[L1_X - 1, CY], [L1_X, CY - 5]],
    [[L1_X, H], [L1_X - 1, H + 15]],
])

RIGHT = np.stack([W - LEFT[:, :, 0], LEFT[:, :, 1]], axis=2)

CENTER = np.array([
    [[CX, 0], [CX, -25]],
    [[CX, CY], [CX, CY - 15]],
    [[CX, H], [CX, H + 8]],
])

TABLE = np.vstack([
    LEFT, RIGHT, CENTER
])
