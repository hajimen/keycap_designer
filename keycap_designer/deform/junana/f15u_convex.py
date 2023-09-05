import numpy as np

W, H = 678, 145
CX = W // 2
CY = 85
L1 = 80

LEFT = np.array([
    [[0, 25], [0, 0]],
    [[20, CY], [0, CY + 10]],
    [[20, H], [0, H + 55]],

    [[L1, 0], [L1, -10]],
    [[L1, CY], [L1, CY - 5]],
    [[L1 - 1, H], [L1 - 1, H + 10]],
])

RIGHT = np.stack([W - LEFT[:, :, 0], LEFT[:, :, 1]], axis=2)

CENTER = np.array([
    [[CX, 0], [CX, -25]],
    [[CX, CY], [CX, CY - 15]],
    [[CX, H], [CX, H + 5]],
])

TABLE = np.vstack([
    LEFT, RIGHT, CENTER
])
