import unittest
import numpy as np
from keycap_designer.color_management import DEFAULT_CC, RenderingIntent


class TestColorManagement(unittest.TestCase):
    def test_loopback(self):
        d = np.array([2000, 65535, 2000], np.uint16).reshape((1, 1, 3))
        ws = DEFAULT_CC.device_rgb_as_cv2_to_workspace(d)
        d_loop = DEFAULT_CC.workspace_to_device_rgb_as_cv2(ws, RenderingIntent.Relative, bpc=True)
        self.assertTrue(np.allclose(d, d_loop, atol=6000), msg='DeviceRGB loopback failed.')
