import numpy as np

W, H = 441, 157
CX = W // 2
CY = 75
L1 = 80

LEFT = np.array([
    [[0, 0], [0, -8]],
    [[0, H], [3, H + 28]],
    [[L1, 0], [L1 - 3, -7]],
    [[L1, CY], [L1 - 3, CY - 4]],
    [[L1, H], [L1 - 2, H + 27]],
])

RIGHT = np.stack([W - LEFT[:, :, 0], LEFT[:, :, 1]], axis=2)

CENTER = np.array([
    [[CX, 0], [CX, 2]],
    [[CX, CY], [CX, CY - 5]],
    [[CX, H], [CX, H + 21]],
])

TABLE = np.vstack([
    LEFT, RIGHT, CENTER
])
