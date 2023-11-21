import typing as ty
from collections import abc
import numpy as np
from numpy.typing import NDArray
from frozendict import frozendict
from importlib import import_module
from skimage.transform import PiecewiseAffineTransform, warp
from keycap_designer.profile import Aperture, CapBase
from keycap_designer.profile import Profile
from keycap_designer.constants import *
from keycap_designer.image import alpha_composite, float_uint16


def _ap(image_name: str):
    return Aperture(RESOURCE_DIR / f'area/junana/{image_name}.png')


def _cb(d: abc.Mapping[Side, Aperture]):
    return CapBase(d)


cb1u = _cb({
    TopSide: _ap('1u-top'),
    FrontSide: _ap('1u-front'),
    Side.TopFront: _ap('1u-tf'),
})

cb1u_convex = _cb({
    TopSide: _ap('1u-convex-top'),
    FrontSide: _ap('1u-convex-front'),
    Side.TopFront: _ap('1u-convex-tf'),
})


cb15u = _cb({
    TopSide: _ap('15u-top'),
    FrontSide: _ap('15u-front'),
    Side.TopFront: _ap('15u-tf'),
})

cb15u_convex = _cb({
    TopSide: _ap('15u-convex-top'),
    FrontSide: _ap('15u-convex-front'),
    Side.TopFront: _ap('15u-convex-tf'),
})

cb225u = _cb({
    TopSide: _ap('225u-top'),
    FrontSide: _ap('225u-front'),
    Side.TopFront: _ap('225u-tf'),
})


cb225u_convex = _cb({
    TopSide: _ap('225u-convex-top'),
    FrontSide: _ap('225u-convex-front'),
    Side.TopFront: _ap('225u-convex-tf'),
})


ANTI_DEFORM_CACHE: dict[str, tuple[PiecewiseAffineTransform, tuple[int, int], tuple[int, int]]] = {}


CB_DEFORM = {
    cb1u: 'f1u',
    cb1u_convex: 'f1u_convex',
    cb15u: 'f15u',
    cb15u_convex: 'f15u_convex',
    cb225u: 'f225u',
    cb225u_convex: 'f225u_convex',
}


def anti_deform(cb: CapBase, img: NDArray[np.uint16]):
    name = CB_DEFORM[cb]
    if name in ANTI_DEFORM_CACHE:
        tf, src_shape, dst_shape = ANTI_DEFORM_CACHE[name]
    else:
        landmarks = import_module(f'keycap_designer.deform.junana.{name}').TABLE
        dst = landmarks[:, 0]
        src = landmarks[:, 1]

        tf = PiecewiseAffineTransform()
        tf.estimate(dst, src)
        src_shape = ty.cast(tuple[int, int], tuple(src.max(axis=0)[::-1].astype(int)))
        dst_shape = ty.cast(tuple[int, int], tuple(dst.max(axis=0)[::-1].astype(int)))
        ANTI_DEFORM_CACHE[name] = (tf, src_shape, dst_shape)

    front_aperture = cb[FrontSide]
    src_img = np.full(front_aperture.mask_wh[::-1] + (4, ), 65535, np.uint16)
    src_img[:, :, 3] = 0
    img_offset_x, img_offset_y = front_aperture.outer_offset
    src_img[img_offset_y: img_offset_y + img.shape[0], img_offset_x: img_offset_x + img.shape[1]] = img
    dst_img = np.full(dst_shape + (4, ), 65535, np.uint16)
    dst_img[:, :, :3] = float_uint16(warp(src_img[:, :, :3], tf, output_shape=dst_shape, cval=1., order=3))
    a_img = float_uint16(warp(src_img[:, :, 3], tf, output_shape=dst_shape, cval=0., order=1))
    a_bit = a_img < 32768
    a_img[a_bit] = 0
    a_img[~a_bit] = 65535
    dst_img[:, :, 3] = a_img
    return dst_img


CB_FRONT_Y_OFFSET = {
    cb1u: 191,
    cb1u_convex: 191 + 4,
    cb15u: 442 - 98 - 141,
    cb15u_convex: 442 - 98 + 117 - 20 - 242,
    cb225u: 124 + 83 - 7,
    cb225u_convex: 124 + 83 - 7,
}


def modify_side_fg_image(cb: CapBase, side_fg_image: dict[Side, NDArray[np.uint16]]) -> dict[Side, NDArray[np.uint16]]:
    if Side.TopFront not in cb:
        return side_fg_image

    aperture = cb[Side.TopFront]
    center_x, center_y = [(wh // 2) - o for wh, o in zip(aperture.mask_wh, aperture.outer_offset)]
    img_shape = aperture.outer_wh[::-1] + (4, )
    img = side_fg_image[Side.TopFront] if Side.TopFront in side_fg_image else np.zeros(img_shape, np.uint16)
    for side in [TopSide, FrontSide]:
        if side not in side_fg_image:
            continue
        fg_image = side_fg_image[side]
        if side == FrontSide:
            fg_image = anti_deform(cb, fg_image)
            offset_y = center_y + CB_FRONT_Y_OFFSET[cb] - (fg_image.shape[0] // 2)
        else:
            offset_y = center_y - (fg_image.shape[0] // 2)
        offset_x = center_x - (fg_image.shape[1] // 2)
        place = np.zeros(img_shape, np.uint16)
        h = min(place.shape[0] - offset_y, fg_image.shape[0])
        if offset_x < 0:
            fg_image = fg_image[:, -offset_x: img_shape[1] - offset_x]
            offset_x = 0
        place[offset_y: offset_y + h, offset_x: offset_x + fg_image.shape[1]] = fg_image[:h]
        img = alpha_composite(place, img)

    return {Side.TopFront: img}


PROFILE = Profile(
    'Junana',
    frozendict({
        '1u': cb1u,
        'Homing 1u': cb1u,
        '15u': cb15u,
        '225u': cb225u,
        'Convex 1u': cb1u_convex,
        'Convex 15u': cb15u_convex,
        'Convex 225u': cb225u_convex,
    }),
    frozendict({
        'Homing 1u': 'homing',
    }),
    modify_side_fg_image
)
