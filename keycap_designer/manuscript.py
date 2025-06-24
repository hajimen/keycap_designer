import typing as ty
import collections.abc as abc
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import inspect
import numpy as np
from numpy.typing import NDArray
import PIL.Image as PILImageModule
import PIL.ImageDraw as PILImageDrawModule
import PIL.ImageFont as PILImageFontModule
import cv2
from keycap_designer.constants import *
from keycap_designer.profile import CapBase, PROFILES, Profile as JigProfile
from keycap_designer.color_management import DEFAULT_CC, RenderingIntent
from keycap_designer.image import alpha_composite, float_uint16, ColorBase, sRGBColor, DisplayP3Color, DeviceRGBColor  # noqa


def here():
    '''
    Returns a pathlib.Path object representing the folder which contains the caller's source file.
    '''
    return Path(os.path.dirname(inspect.stack()[1].filename))


class ColorConversionIntent(Enum):
    '''
    Intent of ICC profile colorspace conversion.
    '''
    Perceptual = auto()
    Relative = auto()
    RelativeNoBpc = auto()
    Saturation = auto()

    def rendering_intent(self):
        return {
            ColorConversionIntent.Perceptual: RenderingIntent.Perceptual,
            ColorConversionIntent.Relative: RenderingIntent.Relative,
            ColorConversionIntent.RelativeNoBpc: RenderingIntent.Relative,
            ColorConversionIntent.Saturation: RenderingIntent.Saturation,
        }[self]

    def bpc(self):
        return {
            ColorConversionIntent.Perceptual: False,
            ColorConversionIntent.Relative: True,
            ColorConversionIntent.RelativeNoBpc: False,
            ColorConversionIntent.Saturation: False,
        }[self]


@dataclass(frozen=True)
class Style:
    '''
    Represents legend's style.

    Parameters
    ----------
    size: float
        Font size by mm.
    x_loc: float
        Horizontal distance from the origin. See ``h_o`` and ``align`` too. The unit is mm.
    y_loc: float
        Vertical distance from the origin. See ``v_o`` too. The unit is mm.
    font: pathlib.Path
        Font path.
    h_o: Orientation = Left
        If ``Right``, the layout coordinate system is horizontally mirrored. ``x_loc`` means the distance from the right edge.
        ``Center`` is available too. In the case, the layout coordinate origin is placed at the center of the layout area.
    v_o: Orientation = Top
        If ``Bottom``, the layout coordinate system is vertically mirrored. ``y_loc`` means the distance from the bottom edge.
        ``Center`` is available too. In the case, the layout coordinate origin is placed at the center of the layout area.
    align: Orientation = Left
        If ``Center``, the legend placing point comes into the horizontal center of the legend area.
        No way to specify vertical center. 'Vertical center' of latin alphabet is a problematic idea.
    color: ColorBase = sRGBColor('#000000')
        Legend's color.
    side: Side = TopSide
        Printing side.
    variation_name: str | None = None
        The style name of variable font. See: https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.FreeTypeFont.set_variation_by_name
    variation_axes: abc.Iterable[float] | None = None
        The axes of variable font. See: https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.FreeTypeFont.set_variation_by_axes
    '''
    size: float
    x_loc: float
    y_loc: float
    font: Path
    h_o: Orientation = Left
    v_o: Orientation = Top
    align: Orientation = Left
    color: ColorBase = sRGBColor('#000000')
    side: Side = TopSide
    variation_name: str | None = None
    variation_axes: abc.Iterable[float] | None = None

    def mod(self,
            size: float | None = None,
            x_loc: float | None = None,
            y_loc: float | None = None,
            font: Path | None = None,
            h_o: Orientation | None = None,
            v_o: Orientation | None = None,
            align: Orientation | None = None,
            color: ColorBase | None = None,
            side: Side | None = None,
            variation_name: str | None = None,
            variation_axes: abc.Iterable[float] | None = None):
        '''
        Copies this object, overwrites some properties, and returns the new object.

        Parameters
        ----------
        size: float | None = None
            Font size by mm.
        x_loc: float | None = None
            Horizontal distance from the origin. See ``h_o`` and ``align`` too. The unit is mm.
        y_loc: float | None = None
            Vertical distance from the origin. See ``v_o`` too. The unit is mm.
        font: pathlib.Path | None = None
            Font path.
        h_o: Orientation | None = None
            If ``Right``, the layout is right justification and ``x_loc`` means the distance from right edge. ``Center`` is available too.
        v_o: Orientation | None = None
            If ``Bottom``, the legend comes into the bottom of printable area. ``Center`` is available too.
        align: Orientation | None = None
            If ``Center``, the origin comes into the horizontal center of the legend.
        color: ColorBase | None = None
            Legend's color
        side: Side | None = None
            Printing side.
        variation_name: str | None = None
            The style name of variable font. See: https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.FreeTypeFont.set_variation_by_name
        variation_axes: abc.Iterable[float] | None = None
            The axes of variable font. See: https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.FreeTypeFont.set_variation_by_axes
        '''
        ret = self.__dict__.copy()
        for n, t in [
                ('size', float),
                ('x_loc', float),
                ('y_loc', float),
                ('font', Path),
                ('h_o', Orientation),
                ('v_o', Orientation),
                ('align', Orientation),
                ('color', ColorBase),
                ('side', Side),
                ('variation_name', str),
                ('variation_axes', abc.Iterable),
        ]:
            a = locals()[n]
            if a is not None:
                if isinstance(a, t):
                    ret[n] = a
                else:
                    ret[n] = t(a)
        return Style(**ret)

    def shift(self, x=0., y=0.):
        '''
        Copies this object, adds [xy] from [xy]_loc, and returns the new object.
        
        Parameters
        ----------
        x: float = 0.
        y: float = 0.
            The unit is mm.
        '''
        ret = self.__dict__.copy()
        ret['x_loc'] += x
        ret['y_loc'] += y
        return Style(**ret)


@dataclass
class ImageFile:
    '''
    Specifies an image file and its image processing policy.

    Parameters
    ----------
    path: pathlib.Path
        Image file path.
    fit : ImageFit = Aspect
        `Aspect`, `Crop`, `Expand`, or `PixelWise`.
    interpolate : ImageInterpolate = Cubic
        `Cubic` or `Nearest`.
    trim : ImageTrim = TrimInner
        `TrimInner` or `TrimOuter`.
    '''
    path: Path
    fit: ImageFit = Aspect
    interpolate: ImageInterpolate = Cubic
    trim: ImageTrim = TrimInner


MDT = ty.Union['Manuscript', 'Descriptor']
MDST = abc.Sequence[MDT]


def _manuscript_matmul(self: 'Descriptor', r, synth: bool):
    k = self.m_name
    if synth or isinstance(r, type(self)):
        return Manuscript(**{k: self % r})  # type: ignore
    elif isinstance(r, Manuscript):
        ret = r.dict()
        if k in ret:
            ret[k] = ret[k] % self
        else:
            ret[k] = self
        return Manuscript(**ret)
    elif isinstance(r, Descriptor):
        return Manuscript(**{k: self, r.m_name: r})  # type: ignore
    else:
        raise Exception('Bad code')


class Descriptor:
    m_name = ''

    def __matmul__(self, r) -> 'Manuscript':
        raise NotImplementedError()

    def __rshift__(self, r: MDST):
        return [self @ v for v in r]

    def __mod__(self, r) -> 'Descriptor':
        raise NotImplementedError()


@dataclass
class Manuscript:
    background_color: 'BackgroundColor | None' = None
    profile: 'Profile | None' = None
    specifier: 'Specifier | None' = None
    layout: 'Layout | None' = None
    row: 'Row | None' = None
    col: 'Col | None' = None
    comment: 'Comment | None' = None
    group: 'Group | None' = None
    legend: 'Legend | None' = None
    image: 'Image | None' = None
    repeat: 'Repeat | None' = None
    rotation: 'Rotation | None' = None
    background_image: 'BackgroundImage | None' = None
    cci: 'CCI | None' = None
    side_color: 'SideColor | None' = None
    skip: 'Skip | None' = None

    def dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def __matmul__(self: 'Manuscript', r: MDT):
        ld: dict[str, Descriptor] = self.dict()
        ret = ld.copy()
        if isinstance(r, Manuscript):
            rd: dict[str, Descriptor] = r.dict()
            ret.update(rd)
            for k in set(ld.keys()) | set(rd.keys()):
                if k in ld and k in rd:
                    ret[k] = ld[k] % rd[k]
            return Manuscript(**ret)  # type: ignore
        elif isinstance(r, Descriptor):
            k = r.m_name
            if k in ret:
                ret[k] = ret[k] % r
            else:
                ret[k] = r
            return Manuscript(**ret)  # type: ignore
        else:
            raise Exception('@ rvalue should be Manuscript or Descriptor.')

    def __rshift__(self, r: MDST):
        return [ty.cast(Manuscript, self @ v) for v in r]


K = ty.TypeVar('K')
V = ty.TypeVar('V')


class DictCombinable(Descriptor, ty.Generic[K, V]):
    kv: list[type] = []

    def __init__(self, d: dict[K, V] | None = None) -> None:
        self.d: dict[K, V] = {} if d is None else d

    def __matmul__(self, r: tuple | MDT):
        return _manuscript_matmul(self, r, isinstance(r, tuple))

    def __mod__(self, r: 'tuple | Descriptor'):
        ret = self.d.copy()
        if isinstance(r, type(self)):
            ret.update(r.d)
        elif isinstance(r, tuple) and isinstance(r[0], self.kv[0]) and isinstance(r[1], self.kv[1]):
            ret[r[0]] = r[1]
        else:
            raise Exception(f'% rvalue should be the same Descriptor or tuple[{self.kv[0]}, {self.kv[1]}].')
        o = self.__class__.__new__(self.__class__)
        self.__class__.__init__(o, ret)
        return o

    def __eq__(self, r) -> bool:
        return isinstance(r, type(self)) and r.d == self.d

    def __repr__(self) -> str:
        cn = self.__class__.__name__
        ret = []
        for k, v in self.d.items():
            ret.append(f'{repr(k)}: {repr(v)}')
        return cn + '({' + ', '.join(ret) + '})'


class Legend(DictCombinable[Style, str]):
    '''
    Specifies legends. The key should be a Style object, and the value should be a legend str.
    '''
    kv = [Style, str]
    m_name = 'legend'


class Image(DictCombinable[Side, ImageFile]):
    kv = [Side, ImageFile]
    m_name = 'image'


def TopImage(path: Path, fit: ImageFit = Aspect, interpolate: ImageInterpolate = Cubic, trim: ImageTrim = TrimInner):
    '''
    Specifies an image file printing on top and its image processing policy.

    Parameters
    ----------
    path : pathlib.Path
        Image file path.
    fit : ImageFit = Aspect
        `Aspect`, `Crop`, `Expand`, or `PixelWise`.
    interpolate : ImageInterpolate = Cubic
        `Cubic` or `Nearest`.
    trim : ImageTrim = TrimInner
        `TrimInner` or `TrimOuter`.
    '''
    return Image({TopSide: ImageFile(path, fit, interpolate, trim)})


def FrontImage(path: Path, fit: ImageFit = Aspect, interpolate: ImageInterpolate = Cubic, trim: ImageTrim = TrimInner):
    '''
    Specifies an image file printing on front-side and its image processing policy.

    Parameters
    ----------
    path : pathlib.Path
        Image file path.
    fit : ImageFit = Aspect
        `Aspect`, `Crop`, `Expand`, or `PixelWise`.
    interpolate : ImageInterpolate = Cubic
        `Cubic` or `Nearest`.
    trim : ImageTrim = TrimInner
        `TrimInner` or `TrimOuter`.
    '''
    return Image({FrontSide: ImageFile(path, fit, interpolate, trim)})


class StrCombinable(Descriptor):
    def __init__(self, v: str) -> None:
        self.v = v

    def __matmul__(self, r: MDT):
        return _manuscript_matmul(self, r, False)

    def __mod__(self, r: 'Descriptor'):
        if isinstance(r, type(self)):
            ret = self.v
            ret += '\n' + r.v
            o = self.__class__.__new__(self.__class__)
            self.__class__.__init__(o, ret)
            return o
        else:
            raise Exception(r'% rvalue should be the same Descriptor.')

    def __eq__(self, r) -> bool:
        return isinstance(r, type(self)) and r.v == self.v

    def __repr__(self) -> str:
        cn = self.__class__.__name__
        return f"{cn}('{repr(self.v)}')"


class Comment(StrCombinable):
    '''
    Adds comment. Shown in preview.
    '''
    m_name = 'comment'


class Group(StrCombinable):
    '''
    Adds group. Shown in preview.
    '''
    m_name = 'group'


class Overlay(Descriptor, ty.Generic[V]):
    def __init__(self, v: V) -> None:
        self.v = v

    def __matmul__(self, r: MDT):
        return _manuscript_matmul(self, r, False)

    def __mod__(self, r: 'Descriptor'):
        if isinstance(r, type(self)):
            return r
        else:
            raise Exception(r'% rvalue should be the same Descriptor.')

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self.v == other.v

    def __repr__(self) -> str:
        cn = self.__class__.__name__
        return f'{cn}({repr(self.v)})'


class Repeat(Overlay[int]):
    '''
    Denotes a number of same keycaps by a Manuscript object.
    '''
    m_name = 'repeat'

    def __mod__(self, r: 'Descriptor'):
        ret = self.v
        if isinstance(r, Repeat):
            ret *= r.v
        elif isinstance(r, int):
            ret *= r
        else:
            raise Exception(r'% rvalue should be Repeat or int.')
        return Repeat(ret)


class BackgroundColor(Overlay[ColorBase]):
    '''
    Affects to margin area, all sides, and legends' outline color. It is alike "keycap's color".
    '''
    m_name = 'background_color'


class BackgroundImage(Overlay[ImageFile]):
    '''
    Specifies image tiling on all sides including their margin area.
    '''
    m_name = 'background_image'


def Wallpaper(path: Path, **kwargs):
    '''
    Shorthand of BackgroundImage. kwargs is passed to ImageFile().
    BackgroundImage specifies image tiling on all sides including their margin area.
    '''
    return BackgroundImage(ImageFile(path, **kwargs))


class SideColor(DictCombinable[Side, ColorBase]):
    '''
    Fills a side by a color. Not affects to margin area or legends' outline.
    See BackgroundColor and Wallpaper for the purpose.
    '''
    kv = [Side, ColorBase]
    m_name = 'side_color'


class Profile(Overlay[str]):
    '''
    Profile of keycap. ``XDA`` or ``Junana``.
    '''
    m_name = 'profile'


class Specifier(Overlay[str]):
    '''
    Specifier string. ``1u`` denotes the most common regular-sized keycap.
    ``Homing 1u`` denotes 1u with bump. ``Convex 1u`` denotes convex-formed keycap.
    ``15u`` denotes Tab-key size. No period between 1 and 5.
    '''
    m_name = 'specifier'


class Layout(Overlay[str]):
    '''
    Specifies layout by KLE JSON file's name. No '.json' in the name.
    The KLE JSON file should be in ./layout folder.
    '''
    m_name = 'layout'


def _pow_rc(self: 'Row | Col', r: MDST):
    skip_offset = 0
    ret: list[MDT] = []
    for i, v in enumerate(r):
        if isinstance(v, Skip) and v.v > 0:
            skip_offset += v.v - 1
        elif isinstance(v, Manuscript) and v.skip is not None and v.skip.v > 0:
            skip_offset += v.skip.v - 1
        else:
            ret.append(self.__class__(self.v + i + skip_offset) @ v)
    return ret


class Row(Overlay[int]):
    '''
    Specifies row in the KLE JSON file.
    '''
    m_name = 'row'

    def __pow__(self, r: MDST):
        return _pow_rc(self, r)


class Col(Overlay[int]):
    '''
    Specifies column in the KLE JSON file.
    '''
    m_name = 'col'

    def __pow__(self, r: MDST):
        return _pow_rc(self, r)


class RotationAngle(Enum):
    CW = auto()
    Flip = auto()
    CCW = auto()
    Right = auto()

    def cv2_rot_inv(self):
        if self == RotationAngle.CW:
            return cv2.ROTATE_90_COUNTERCLOCKWISE
        elif self == RotationAngle.Flip:
            return cv2.ROTATE_180
        elif self == RotationAngle.CCW:
            return cv2.ROTATE_90_CLOCKWISE
        else:
            raise Exception('Check Right or not.')

    def pil_rot(self):
        if self == RotationAngle.CW:
            return PILImageModule.Transpose.ROTATE_90
        elif self == RotationAngle.Flip:
            return PILImageModule.Transpose.ROTATE_180
        elif self == RotationAngle.CCW:
            return PILImageModule.Transpose.ROTATE_270
        else:
            raise Exception('Check Right or not.')

    def inv(self):
        if self == RotationAngle.CW:
            return RotationAngle.CCW
        elif self == RotationAngle.Flip:
            return RotationAngle.Flip
        elif self == RotationAngle.CCW:
            return RotationAngle.CW
        else:
            raise Exception('Check Right or not.')

    def is_swap(self):
        return self == RotationAngle.CW or self == RotationAngle.CCW

    def is_rot(self):
        return self != RotationAngle.Right


class Rotation(Overlay[RotationAngle]):
    '''
    Rotates keycap. `RotationAngle.CW`, `RotationAngle.Flip`, `RotationAngle.CCW`, or `RotationAngle.Right`.
    '''
    m_name = 'rotation'


class CCI(Overlay[ColorConversionIntent]):
    '''
    Chooses color conversion intent of ICC profile. `Perceptual`, `Relative`, `RelativeNoBpc`, or `Saturation`
    '''
    m_name = 'cci'


Perceptual = CCI(ColorConversionIntent.Perceptual)
Relative = CCI(ColorConversionIntent.Relative)
RelativeNoBpc = CCI(ColorConversionIntent.RelativeNoBpc)
Saturation = CCI(ColorConversionIntent.Saturation)


class Skip(Overlay[int]):
    def __init__(self, v: int = 1) -> None:
        '''
        Increments Row/Col ** operation index and vanishes.
        ``v`` is the increment number.
        '''
        super().__init__(v)

    m_name = 'skip'


@dataclass
class ArtWork:
    profile: JigProfile
    cb: CapBase
    group: str
    comment: str
    rank: int
    side_image: abc.Mapping[Side, NDArray]
    cci: ColorConversionIntent
    repeat: int
    layout: str
    row: int
    col: int
    specifier: str


def bg_composition(img: NDArray[np.uint16], bg: NDArray[np.uint16]):
    alpha = img[:, :, 3]
    mask = alpha > 0
    am = alpha[mask, np.newaxis].astype(np.uint32)
    img = img[:, :, :3]
    bg[mask] = ((img[mask] * am + bg[mask] * (65535 - am)) // 65535).astype(np.uint16)
    return bg


def manuscript_to_artwork(m: Manuscript):
    if m.profile is None:
        raise Exception('Profile not specified.')
    if m.profile.v not in PROFILES:
        raise Exception(f'Profile {m.profile.v} not found.')
    jig_profile = PROFILES[m.profile.v]
    sp_cb = jig_profile.sp_cb_dict
    if m.specifier is None:
        raise Exception('Specifier not specified.')
    if m.specifier.v not in sp_cb:
        raise Exception(f'Specifier {m.specifier.v} not found.')
    cb = sp_cb[m.specifier.v]
    rot = RotationAngle.Right if m.rotation is None else m.rotation.v

    background_color = sRGBColor(255, 255, 255) if m.background_color is None else m.background_color.v

    side_fg_image: dict[Side, NDArray[np.uint16]] = {}
    for side, aperture in cb.items():
        if m.side_color is not None and side in m.side_color.d:
            side_color = m.side_color.d[side]
        else:
            side_color = background_color

        ipw, iph = aperture.wh
        opw, oph = aperture.outer_wh
        a_wh = np.array(aperture.wh) / DPM
        mask = PILImageModule.open(str(aperture.mask_path))
        ma = np.array(mask.getchannel('A'))
        ml = np.array(mask.getchannel('L'))
        offset_x, offset_y = aperture.offset
        outer_offset_x, outer_offset_y = aperture.outer_offset
        outer_inner_offset_x, outer_inner_offset_y = offset_x - outer_offset_x, offset_y - outer_offset_y
        inner_mask = np.bitwise_not(((ma > 0) & (ml > 0))[outer_offset_y:outer_offset_y + oph, outer_offset_x:outer_offset_x + opw])
        outer_mask = np.bitwise_not(((ma > 0))[outer_offset_y:outer_offset_y + oph, outer_offset_x:outer_offset_x + opw])

        def mask_alpha(img: NDArray[np.uint16] | cv2.Mat, inner_to_outer: bool):
            if inner_to_outer:
                new_img = np.zeros((oph, opw, 4), np.uint16)
                new_img[outer_inner_offset_y: outer_inner_offset_y + iph, outer_inner_offset_x: outer_inner_offset_x + ipw] = img
                img = new_img
            ach = img[:, :, 3].copy()
            ach[inner_mask if inner_to_outer else outer_mask] = 0
            img[:, :, 3] = ach
            return ty.cast(NDArray[np.uint16], img)

        if m.image is not None and side in m.image.d:
            f = m.image.d[side]
            if not f.path.exists():
                raise FileNotFoundError(f'{f.path} not exist.')
            pil_image_from_file = PILImageModule.open(str(f.path))
            if 'RGB' not in pil_image_from_file.mode:
                pil_image_from_file = pil_image_from_file.convert('RGBA')
                if 'icc_profile' in pil_image_from_file.info:
                    del pil_image_from_file.info['icc_profile']
            elif pil_image_from_file.mode != 'RGBA':
                pil_image_from_file = pil_image_from_file.convert('RGBA')
            if rot.is_rot():
                pil_image_from_file = pil_image_from_file.transpose(rot.pil_rot())
            img_from_file = DEFAULT_CC.source_to_workspace(pil_image_from_file)
            uh, uw = img_from_file.shape[:2]
            rx, ry = 0, 0
            pw, ph = (ipw, iph) if f.trim == TrimInner else (opw, oph)
            rw, rh = pw, ph
            if f.fit == PixelWise:
                rx = (uw - pw) // 2
                if rx < 0:
                    rw = uw
                ry = (uh - ph) // 2
                if ry < 0:
                    rh = uh
            else:
                if f.fit == Crop:
                    if uh * pw > uw * ph:
                        rh = (uh * pw) // uw
                        ry = (rh - ph) // 2
                    elif uh * pw < uw * ph:
                        rw = (uw * ph) // uh
                        rx = (rw - pw) // 2
                elif f.fit == Aspect:
                    if uh * pw > uw * ph:
                        rw = (uw * ph) // uh
                        rx = (rw - pw) // 2
                    elif uh * pw < uw * ph:
                        rh = (uh * pw) // uw
                        ry = (rh - ph) // 2
                else:  # Expand
                    pass

                flag = (cv2.INTER_CUBIC if f.interpolate == Cubic else cv2.INTER_NEAREST) if (rw > uw) or (rh > uh) else cv2.INTER_AREA
                img_from_file = ty.cast(NDArray[np.uint16], cv2.resize(img_from_file, (rw, rh), interpolation=flag))

            img = np.zeros((ph, pw, 4), np.uint16)
            if rx > 0:
                if ry > 0:
                    img = img_from_file[ry:ry + rh, rx:rx + pw]
                else:
                    img[-ry:rh - ry] = img_from_file[:, rx:rx + pw]
            else:
                if ry > 0:
                    img[:, -rx:rw - rx] = img_from_file[ry:ry + ph]
                else:
                    img[-ry:rh - ry, -rx:rw - rx] = img_from_file
            img_from_file = mask_alpha(img, f.trim == TrimInner)
        else:
            img_from_file = None

        legends: list[tuple[Style, str]] = []
        if m.legend is not None:
            for style, s in m.legend.d.items():
                if style.side == side:
                    legends.append((style, s))
        if len(legends) > 0:
            pil_image_legend = PILImageModule.new('RGBA', (ipw, iph), _get_pil_color(side_color, 0))
            if rot.is_rot():
                pil_image_legend = pil_image_legend.transpose(rot.inv().pil_rot())
            a_w, a_h = (a_wh[1], a_wh[0]) if rot.is_swap() else (a_wh[0], a_wh[1])
            d = PILImageDrawModule.Draw(pil_image_legend)
            # antialias
            d.fontmode = 'L'  # type: ignore
            for style, s in legends:
                _draw_style(d, style, s, a_w, a_h, side_color)
            if rot.is_rot():
                pil_image_legend = pil_image_legend.transpose(rot.pil_rot())
            img_legend = mask_alpha(DEFAULT_CC.source_to_workspace(pil_image_legend), True)
        else:
            img_legend = None

        if img_from_file is None and img_legend is None:
            img = None
        elif img_from_file is None:
            img = img_legend
        elif img_legend is None:
            img = img_from_file
        else:
            img = alpha_composite(img_legend, img_from_file)
        if side_color != background_color:
            sc_img = np.full((oph, opw, 4), _get_workspace_color(side_color), dtype=np.uint16)
            ach = sc_img[:, :, 3].copy()
            ach[inner_mask] = 0
            sc_img[:, :, 3] = ach
            if img is None:
                img = sc_img
            else:
                img = alpha_composite(img, sc_img)

        if img is not None:
            side_fg_image[side] = img

    if jig_profile.modify_side_fg_image is not None:
        side_fg_image = jig_profile.modify_side_fg_image(cb, side_fg_image)

    def generate_bg(wh, xy) -> NDArray[np.uint16]:
        w, h = wh
        if m.background_image is None:
            return np.full((h, w, 4), _get_workspace_color(background_color), dtype=np.uint16)
        else:
            x, y = xy
            pil_image = PILImageModule.open(str(m.background_image.v.path))
            pil_image = pil_image.convert('RGBA')
            if rot.is_rot():
                pil_image = pil_image.transpose(rot.pil_rot())
            bg_img = DEFAULT_CC.source_to_workspace(pil_image)
            bh, bw, _ = bg_img.shape
            if bh < h or bw < w or bh // 2 < y or bh // 2 < h - y or bw // 2 < x or bw // 2 < w - x:
                rep_y = (h // bh) + 2
                rep_x = (w // bw) + 2
                rep_img = np.tile(bg_img, (rep_y, rep_x, 1))
                return rep_img[bh - (y % bh): bh + h - (y % bh), bw - (x % bw): bw + w - (x % bw)]
            else:
                ox = bw // 2 - x
                oy = bh // 2 - y
                return bg_img[oy: oy + h, ox: ox + w]

    side_image: dict[Side, NDArray[np.uint16]] = {}
    for side, img in side_fg_image.items():
        oph, opw, _ = img.shape
        aperture = cb[side]
        ma = np.array(PILImageModule.open(str(aperture.mask_path)).getchannel('A'))
        outer_offset_x, outer_offset_y = aperture.outer_offset
        outer_mask_center_x, outer_mask_center_y = aperture.outer_mask_center
        a_img = generate_bg(wh=ma.shape[::-1], xy=(outer_mask_center_x + outer_offset_x, outer_mask_center_y + outer_offset_y))
        a_img[ma == 0] = (65535, 65535, 65535, 0)
        a_img[outer_offset_y:outer_offset_y + oph, outer_offset_x:outer_offset_x + opw, :3] = bg_composition(img, a_img[outer_offset_y:outer_offset_y + oph, outer_offset_x:outer_offset_x + opw, :3])
        side_image[side] = a_img

    rank = 0
    if m.row is not None:
        rank = m.row.v * 1000 * 1000
    if m.col is not None:
        rank += m.col.v * 1000
    comment = '' if m.comment is None else m.comment.v
    if m.specifier.v in jig_profile.sp_comment_dict:
        if comment != '':
            comment = '\r' + comment
        comment = jig_profile.sp_comment_dict[m.specifier.v] + comment

    return ArtWork(
        jig_profile,
        cb,
        '' if m.group is None else m.group.v,
        comment,
        rank, side_image, ColorConversionIntent.Perceptual if m.cci is None else m.cci.v,
        1 if m.repeat is None else m.repeat.v,
        '' if m.layout is None else m.layout.v,
        -1 if m.row is None else m.row.v,
        -1 if m.col is None else m.col.v,
        m.specifier.v)


def _get_pil_color(color: ColorBase, alpha: int | None = 255):
    if color.cs.name == 'sRGBColor':
        c = color
    else:
        c = sRGBColor(color)
    t = ty.cast(tuple[int, int, int], tuple(int(v) for v in c.values()))
    return t if alpha is None else t + (alpha,)


def _get_workspace_color(color: ColorBase):
    if color.cs.name == 'DisplayP3Color':
        c = color
    else:
        c = DisplayP3Color(color)
    linear_channels = np.zeros(4, dtype=float)
    linear_channels[0] = 1.
    linear_channels[1:] = c.linear_values()
    return float_uint16(linear_channels[::-1])


def _ndarray_to_float_tuple(arr: NDArray):
    return ty.cast(tuple[float, float], tuple(arr.astype(float)))


def _draw_style(d: PILImageDrawModule.ImageDraw, style: Style, s: str, w: float, h: float, background_color: ColorBase):
    if not style.font.exists():
        raise Exception(f'Cannot find font file: {style.font}')

    psize = int(style.size * DPM)
    font = PILImageFontModule.truetype(str(style.font), psize)
    if style.variation_name is not None:
        try:
            font.set_variation_by_name(style.variation_name)
        except OSError as e:
            raise Exception(f'Error: {font.getname()[0]} is not a variable font.') from e
        except ValueError as e:
            raise Exception(f'Error: {style.variation_name} is not in the list of style names. Choose from: {", ".join([n.decode() for n in font.get_variation_names()])}') from e
    if style.variation_axes is not None:
        font.set_variation_by_axes(list(style.variation_axes))
    bbox = np.array(font.getbbox(s)) / DPM
    if bbox[2] - bbox[0] > w:
        print("width overflow: " + s)
    if bbox[3] - bbox[1] > h:
        print("height overflow: " + s)
    anchor = {
        Right: 'r',
        Center: 'm',
        Left: 'l'
    }[style.align]
    anchor += {
        Bottom: 's',
        Center: 'm',
        Top: 't'
    }[style.v_o]

    loc = np.array([
        style.x_loc if style.h_o == Left else w / 2 + style.x_loc if style.h_o == Center else w - style.x_loc,
        style.y_loc if style.v_o == Top else h / 2 + style.y_loc if style.v_o == Center else h - style.y_loc
    ])

    # surrounding background to readability
    pil_loc = _ndarray_to_float_tuple(loc * DPM)
    pbc = _get_pil_color(background_color)
    d.text(pil_loc, s, pbc, font, anchor, stroke_width=5)

    # legend itself
    d.text(pil_loc, s, _get_pil_color(style.color), font, anchor)
