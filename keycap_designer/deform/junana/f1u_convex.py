import numpy as np

W_L, H_L = 430 + 20, 150
W_R, H_R = 430, 156
CX_L = W_L // 2
CX_R = W_R // 2
CY = 75
L1_L = 90
L1_R = 80
L2_L = 140
L2_R = 130

LEFT = np.array([
    [[0, 25], [-1, 0]],
    [[20, CY], [-1, CY + 10]],
    [[20, H_L], [-1, H_R + 41]],

    [[L1_L, 0], [L1_R - 1, -14]],
    [[L1_L, CY], [L1_R - 1, CY - 12]],
    [[L1_L - 1, H_L], [L1_R - 2, H_R + 7]],

    [[L2_L, 0], [L2_R - 1, -25]],
    [[L2_L, CY], [L2_R - 1, CY - 15]],
    [[L2_L - 1, H_L], [L2_R - 2, H_R + 3]],
])

RIGHT = np.stack([[W_L - LEFT[:, 0, 0], LEFT[:, 0, 1]], [W_R - LEFT[:, 1, 0], LEFT[:, 1, 1]]], axis=2).transpose(1, 2, 0)

CENTER = np.array([
    [[CX_L, 0], [CX_R, -36]],
    [[CX_L, CY], [CX_R, CY - 19]],
    [[CX_L, H_L], [CX_R, H_R - 1]],
])

TABLE = np.vstack([
    LEFT, RIGHT, CENTER
])
