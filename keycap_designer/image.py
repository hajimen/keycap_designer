from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray


def alpha_composite(fg: NDArray[np.uint16], bg: NDArray[np.uint16]):
    fg_a = (fg[:, :, 3] / 65535)[:, :, np.newaxis]
    bg_a = (bg[:, :, 3] / 65535)[:, :, np.newaxis]
    fg[:, :, 3] = 65535
    bg[:, :, 3] = 65535
    img_f = fg * fg_a + bg * bg_a * (1. - fg_a)
    mask = img_f[:, :, 3] > 0.
    img_g = np.zeros_like(img_f[:, :, :3])
    img_g[mask] = img_f[:, :, :3][mask] / (img_f[:, :, 3][mask] / 65535)[:, np.newaxis]
    img = np.zeros(bg.shape, np.uint16)
    img[:, :, :3] = img_g.astype(np.uint16)
    img[:, :, 3] = img_f[:, :, 3].astype(np.uint16)
    return img


def float_uint16(img: NDArray[np.floating]):
    return (img * 65535).round().clip(0, 65535).astype(np.uint16)


def _calc_rgb_to_xyz_mat(xw: float, yw: float,
                         xr: float, yr: float,
                         xg: float, yg: float,
                         xb: float, yb: float):
    rgb = np.array([
        [xr, xg, xb],
        [yr, yg, yb],
        [1. - xr - yr, 1. - xg - yg, 1. - xb - yb]
    ])
    wp = np.array([xw / yw, 1., (1. - xw - yw) / yw])
    s = np.linalg.inv(rgb) @ wp
    m = rgb @ np.diag(s)
    return m


def _linear1_to_gamma255_py(v: float, f: float, f_a: float, g: float, g_b: float):
    gf = f / f_a
    if v <= gf:
        return v * f_a * 255
    else:
        return ((1. + g_b) * (v ** (1 / g)) - g_b) * 255


def _gamma255_to_linear1_py(v255: float, f: float, f_a: float, g: float, g_b: float):
    v = v255 / 255
    if v <= f:
        return v / f_a
    else:
        return ((v + g_b) / (1. + g_b)) ** g


class _RGBColorSpace:
    def __init__(self,
                 name: str,
                 xw: float, yw: float,
                 xr: float, yr: float,
                 xg: float, yg: float,
                 xb: float, yb: float,
                 f: float, f_a: float,
                 g: float, g_b: float) -> None:
        self.name = name
        self.linear1_to_gamma255 = np.vectorize(lambda v: _linear1_to_gamma255_py(v, f, f_a, g, g_b))
        self.gamma255_to_linear1 = np.vectorize(lambda v: _gamma255_to_linear1_py(v, f, f_a, g, g_b))
        m = _calc_rgb_to_xyz_mat(xw, yw, xr, yr, xg, yg, xb, yb)
        self.rgb_to_xyz_mat = m
        self.xyz_to_rgb_mat = np.linalg.inv(m)


class _ColorRepresentation(Enum):
    Linear1 = auto()
    Gamma255 = auto()
    XYZ = auto()


class ColorBase:
    def __init__(self, cs: _RGBColorSpace, *args) -> None:
        v: NDArray[np.floating]
        cr: _ColorRepresentation
        an = len(args)
        if an == 1:
            cr = _ColorRepresentation.Gamma255
            o = args[0]
            if isinstance(o, ColorBase):
                cr = _ColorRepresentation.XYZ
                v = o.values(cr)
            elif isinstance(o, str):
                from PIL import ImageColor
                v = np.array(ImageColor.getcolor(o, "RGB"))
            else:
                raise Exception('The arg is wrong')
        elif an == 3:
            cr = _ColorRepresentation.Gamma255
            v = np.array(args, float)
        else:
            raise Exception('The arg is wrong')
        self._v = v
        self._cr = cr
        self.cs = cs

    def values(self, cr: _ColorRepresentation = _ColorRepresentation.Gamma255) -> NDArray[np.floating]:
        if cr == self._cr:
            return self._v
        match (self._cr, cr):
            case (_ColorRepresentation.Linear1, _ColorRepresentation.Gamma255):
                return self.cs.linear1_to_gamma255(self._v)
            case (_ColorRepresentation.Gamma255, _ColorRepresentation.Linear1):
                return self.cs.gamma255_to_linear1(self._v)
            case (_ColorRepresentation.Gamma255, _ColorRepresentation.XYZ) | (_ColorRepresentation.Linear1, _ColorRepresentation.XYZ):
                l1 = self._v if self._cr == _ColorRepresentation.Linear1 else self.cs.gamma255_to_linear1(self._v)
                return self.cs.rgb_to_xyz_mat @ l1
            case (_ColorRepresentation.XYZ, _ColorRepresentation.Gamma255) | (_ColorRepresentation.XYZ, _ColorRepresentation.Linear1):
                l1 = self.cs.xyz_to_rgb_mat @ self._v
                return l1 if cr == _ColorRepresentation.Linear1 else self.cs.linear1_to_gamma255(l1)
            case _:
                raise Exception()

    def linear_values(self):
        return self.values(_ColorRepresentation.Linear1)

    def __str__(self) -> str:
        v = self.values()
        return self.cs.name + f'({v[0]:.1f}, {v[1]:.1f}, {v[2]:.1f})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ColorBase) and str(other) == str(self)

    def __hash__(self) -> int:
        return hash(str(self))


_sRGBColorSpace = _RGBColorSpace('sRGBColor',
                                 0.3127, 0.329,
                                 0.64, 0.33,
                                 0.30, 0.60,
                                 0.15, 0.06,
                                 0.04045, 12.92,
                                 2.4, 0.055)


_DisplayP3ColorSpace = _RGBColorSpace('DisplayP3Color',
                                      0.3127, 0.329,
                                      0.68, 0.32,
                                      0.265, 0.69,
                                      0.15, 0.06,
                                      0.04045, 12.92,
                                      2.4, 0.055)


_AdobeRGBColorSpace = _RGBColorSpace('AdobeRGBColor',
                                     0.3127, 0.329,
                                     0.64, 0.33,
                                     0.21, 0.71,
                                     0.15, 0.06,
                                     0., 0.,
                                     2.19921875, 0.)


def sRGBColor(*args):
    '''
    Returns a ColorBase object.

    Parameters
    ----------
    (r, g, b) : 0-255 int or float of RGB values of the color in sRGB colorspace.
    or
    s : str
        A color string like "#FF0000".
    or
    c : ColorBase
        A ColorBase object. You can convert colorspace by this.
    '''
    return ColorBase(_sRGBColorSpace, *args)


def DisplayP3Color(*args):
    '''
    Returns a ColorBase object.

    Parameters
    ----------
    (r, g, b) : 0-255 int or float of RGB values of the color in DisplayP3 colorspace.
    or
    s : str
        A color string like "#FF0000".
    or
    c : ColorBase
        A ColorBase object. You can convert colorspace by this.
    '''
    return ColorBase(_DisplayP3ColorSpace, *args)


def AdobeRGBColor(*args):
    '''
    Returns a ColorBase object.

    Parameters
    ----------
    (r, g, b) : 0-255 int or float of RGB values of the color in AdobeRGB colorspace.
    or
    s : str
        A color string like "#FF0000".
    or
    c : ColorBase
        A ColorBase object. You can convert colorspace by this.
    '''
    return ColorBase(_AdobeRGBColorSpace, *args)


def DeviceRGBColor(*args):
    '''
    Returns a ColorBase object. Always use with `Relative`.

    Parameters
    ----------
    (r, g, b) : 0-255 int or float of RGB values of the color in device RGB colorspace.
    or
    s : str
        A color string like "#FF0000".
    or
    c : ColorBase
        A ColorBase object. You can convert colorspace by this.
    '''
    import typing as ty
    from keycap_designer.color_management import DEFAULT_CC

    tmp = ColorBase(_sRGBColorSpace, *args)
    source = ty.cast(NDArray[np.uint16], tmp.values()[::-1].astype(np.uint16) * 257)
    ws = DEFAULT_CC.device_rgb_as_cv2_to_workspace(source.reshape(1, 1, 3))
    srgb = DEFAULT_CC.workspace_to_srgb_as_cv2(ws)

    return ColorBase(_sRGBColorSpace, *tuple(srgb.reshape((3,))))
