import numpy as np

W, H = 683, 151
CX = W // 2
CY = 75
L1 = 80

LEFT = np.array([
    [[0, 5], [0, 0]],
    [[20, CY], [0, CY + 20]],
    [[20, H], [0, H + 65]],

    [[L1, 0], [L1 - 0, 0]],
    [[L1, CY], [L1 - 2, CY + 7]],
    [[L1 - 1, H], [L1 - 5, H + 30]],
])

RIGHT = np.stack([W - LEFT[:, :, 0], LEFT[:, :, 1]], axis=2)

CENTER = np.array([
    [[CX, 0], [CX, 10]],
    [[CX, CY], [CX, CY + 10]],
    [[CX, H], [CX, H + 30]],
])

TABLE = np.vstack([
    LEFT, RIGHT, CENTER
])
