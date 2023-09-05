from importlib import import_module
from pathlib import Path
import numpy as np
from skimage.transform import PiecewiseAffineTransform, warp
import cv2


AREA_NAME = 'f1u_convex'
DATA_DIR = Path(__file__).parent / "junana"
AREA = True

d = 'area' if AREA else 'pattern'
IMG_FILENAME = str(DATA_DIR / f"{d}/{AREA_NAME}.png")


image = cv2.imread(IMG_FILENAME, cv2.IMREAD_UNCHANGED)
if AREA:
    alpha = image[:, :, 3].copy()
    image[alpha == 0] = 255
    image[:, :, 3] = alpha
else:
    i = np.full(image.shape[:2] + (4, ), 255, np.uint8)
    i[:, :, :3] = image
    image = i
image[:, :, 3] = 255 - image[:, :, 3]  # type: ignore
rows, cols = image.shape[:2]

landmarks = import_module(f'junana.{AREA_NAME}').TABLE
dst = landmarks[:, 0]
src = landmarks[:, 1]
if AREA:
    src, dst = dst, src

out_cols, out_rows = src.max(axis=0)

tform = PiecewiseAffineTransform()
_ = tform.estimate(src, dst)

out = (warp(image, tform, output_shape=(out_rows, out_cols), cval=0.5) * 255).astype(np.uint8)

out[:, :, 3] = 255 - out[:, :, 3]

cv2.imshow('img', out)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('tmp/out.png', out)
