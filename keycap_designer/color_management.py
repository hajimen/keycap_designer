import typing as ty
from enum import Enum, auto
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from numpy.typing import NDArray
from PIL import Image as PILImageModule
import cv2
import cmm
from .overwrite_reportlab import overwrite_reportlab

ICC_DIR = Path(__file__).parent / 'icc'
WORKSPACE_PROFILE_PATH = ICC_DIR / 'Linear P3D65.icc'
WS_HP = None
with open(ICC_DIR / 'sRGBz.icc', 'rb') as f:
    SRGB_PROF = f.read()
overwrite_reportlab()


class RenderingIntent(Enum):
    Perceptual = cmm.INTENT_PERCEPTUAL
    Relative = cmm.INTENT_RELATIVE_COLORIMETRIC
    Saturation = cmm.INTENT_SATURATION
    Absolute = cmm.INTENT_ABSOLUTE_COLORIMETRIC


class _ColorSpaceType(Enum):
    SRGB = auto()
    WORKSPACE = auto()
    DEVICE_RGB = auto()
    DEVICE_RGB_16 = auto()


_CST_FMT = {
    _ColorSpaceType.SRGB: cmm.get_transform_formatter(0, cmm.PT_RGB, 3, 1, 0, 0),
    _ColorSpaceType.WORKSPACE: cmm.get_transform_formatter(0, cmm.PT_RGB, 3, 2, 0, 0),
    _ColorSpaceType.DEVICE_RGB: cmm.get_transform_formatter(0, cmm.PT_RGB, 3, 1, 0, 0),
    _ColorSpaceType.DEVICE_RGB_16: cmm.get_transform_formatter(0, cmm.PT_RGB, 3, 2, 0, 0)
}


with open(WORKSPACE_PROFILE_PATH, 'rb') as f:
    WS_HP = cmm.open_profile_from_mem(f.read())
del f


def check_ws_img(ws_img: NDArray[np.uint16]):
    if ws_img.shape[2] != 3:
        raise Exception('ws_img should be BGR image')


@dataclass(frozen=True)
class _ColorConversionType:
    source: _ColorSpaceType
    target: _ColorSpaceType
    bpc: bool
    soft_proof: bool = False
    soft_proof_cs: _ColorSpaceType = _ColorSpaceType.SRGB


class ColorConverter:
    def __init__(self, device_rgb_profile_path: Path) -> None:
        self._transform_cache: dict[tuple[_ColorConversionType, RenderingIntent], ty.Any] = {}
        with open(device_rgb_profile_path, 'rb') as f:
            hp = cmm.open_profile_from_mem(f.read())
        self.cst_hp = {
            _ColorSpaceType.SRGB: cmm.create_srgb_profile(),
            _ColorSpaceType.WORKSPACE: WS_HP,
            _ColorSpaceType.DEVICE_RGB: hp,
            _ColorSpaceType.DEVICE_RGB_16: hp
        }

    def _get_transform(self, cct: _ColorConversionType, rendering_intent: RenderingIntent):
        if (cct, rendering_intent) in self._transform_cache:
            return self._transform_cache[cct, rendering_intent]
        bpc = cmm.cmsFLAGS_BLACKPOINTCOMPENSATION if cct.bpc else 0
        if cct.soft_proof:
            tr = cmm.create_proofing_transform(
                self.cst_hp[cct.source], _CST_FMT[cct.source],
                self.cst_hp[cct.soft_proof_cs], _CST_FMT[cct.soft_proof_cs],
                self.cst_hp[_ColorSpaceType.DEVICE_RGB],
                rendering_intent.value, cmm.INTENT_RELATIVE_COLORIMETRIC,
                bpc)
        else:
            tr = cmm.create_transform(
                self.cst_hp[cct.source], _CST_FMT[cct.source],
                self.cst_hp[cct.target], _CST_FMT[cct.target],
                rendering_intent.value,
                bpc)
        self._transform_cache[cct, rendering_intent] = tr
        return tr

    def workspace_to_device_rgb(self, ws_img: NDArray[np.uint16], rendering_intent: RenderingIntent, bpc=True):
        check_ws_img(ws_img)
        trg_img = np.zeros(ws_img.shape, dtype=np.uint8)
        tr = self._get_transform(_ColorConversionType(_ColorSpaceType.WORKSPACE, _ColorSpaceType.DEVICE_RGB, bpc), rendering_intent)
        cmm.do_transform_16_8(tr, cv2.cvtColor(ws_img, cv2.COLOR_BGR2RGB), trg_img, ws_img.size // 3)
        return PILImageModule.fromarray(trg_img)

    def workspace_to_device_rgb_as_cv2(self, ws_img: NDArray[np.uint16], rendering_intent: RenderingIntent, bpc=True) -> NDArray[np.uint16]:
        check_ws_img(ws_img)
        trg_img = np.zeros(ws_img.shape, dtype=np.uint16)
        tr = self._get_transform(_ColorConversionType(_ColorSpaceType.WORKSPACE, _ColorSpaceType.DEVICE_RGB_16, bpc), rendering_intent)
        cmm.do_transform_16_16(tr, cv2.cvtColor(ws_img, cv2.COLOR_BGR2RGB), trg_img, ws_img.size // 3)
        return cv2.cvtColor(trg_img, cv2.COLOR_RGB2BGR)  # type: ignore

    def device_rgb_as_cv2_to_workspace(self, device_rgb_img: NDArray[np.uint16]) -> NDArray[np.uint16]:
        trg_img = np.zeros(device_rgb_img.shape, dtype=np.uint16)
        tr = self._get_transform(_ColorConversionType(_ColorSpaceType.DEVICE_RGB_16, _ColorSpaceType.WORKSPACE, True), RenderingIntent.Relative)
        cmm.do_transform_16_16(tr, cv2.cvtColor(device_rgb_img, cv2.COLOR_BGR2RGB), trg_img, device_rgb_img.size // 3)
        return cv2.cvtColor(trg_img, cv2.COLOR_RGB2BGR)  # type: ignore

    def source_to_workspace(self, pil_img: PILImageModule.Image) -> NDArray[np.uint16]:
        src_fmt = cmm.get_transform_formatter(0, cmm.PT_RGB, 3, 1, 0, 0)
        src_hp = None
        if 'icc_profile' in pil_img.info:
            profile_mem = pil_img.info['icc_profile']
            src_hp = cmm.open_profile_from_mem(profile_mem)
            tr = cmm.create_transform(
                src_hp, src_fmt,
                self.cst_hp[_ColorSpaceType.WORKSPACE], _CST_FMT[_ColorSpaceType.WORKSPACE],
                cmm.INTENT_RELATIVE_COLORIMETRIC, 0)
        else:
            tr = self._get_transform(_ColorConversionType(_ColorSpaceType.SRGB, _ColorSpaceType.WORKSPACE, False), RenderingIntent.Relative)
        src_img = np.array(pil_img.convert('RGB'))
        trg_img = np.zeros(src_img.shape, dtype=np.uint16)
        cmm.do_transform_8_16(tr, src_img, trg_img, src_img.size // 3)
        if src_hp is not None:
            cmm.close_profile(src_hp)
        ret = cv2.cvtColor(trg_img, cv2.COLOR_RGB2BGR)
        if 'A' in pil_img.mode:
            ret = cv2.cvtColor(ret, cv2.COLOR_BGR2BGRA)
            ret[:, :, 3] = np.array(pil_img.getchannel('A'), np.uint16) * 257
        return ret  # type: ignore

    def workspace_to_soft_proof(self, ws_img: NDArray[np.uint16], rendering_intent: RenderingIntent, bpc=True):
        '''
        The result is sRGB.
        '''
        check_ws_img(ws_img)
        trg_img = np.zeros(ws_img.shape, dtype=np.uint8)
        tr = self._get_transform(_ColorConversionType(_ColorSpaceType.WORKSPACE, _ColorSpaceType.DEVICE_RGB, bpc, soft_proof=True), rendering_intent)
        cmm.do_transform_16_8(tr, cv2.cvtColor(ws_img, cv2.COLOR_BGR2RGB), trg_img, ws_img.size // 3)
        pimg = PILImageModule.fromarray(trg_img)
        pimg.info['icc_profile'] = SRGB_PROF
        return pimg

    def workspace_to_soft_proof_as_workspace(self, ws_img: NDArray[np.uint16], rendering_intent: RenderingIntent, bpc=True) -> NDArray[np.uint16]:
        check_ws_img(ws_img)
        trg_img = np.zeros(ws_img.shape, dtype=np.uint16)
        tr = self._get_transform(_ColorConversionType(_ColorSpaceType.WORKSPACE, _ColorSpaceType.DEVICE_RGB, bpc, soft_proof=True, soft_proof_cs=_ColorSpaceType.WORKSPACE), rendering_intent)
        cmm.do_transform_16_16(tr, cv2.cvtColor(ws_img, cv2.COLOR_BGR2RGB), trg_img, ws_img.size // 3)
        return cv2.cvtColor(trg_img, cv2.COLOR_RGB2BGR)  # type: ignore

    def workspace_to_srgb_as_cv2(self, ws_img: NDArray[np.uint16]) -> NDArray[np.uint8]:
        check_ws_img(ws_img)
        trg_img = np.zeros(ws_img.shape, dtype=np.uint8)
        tr = self._get_transform(_ColorConversionType(_ColorSpaceType.WORKSPACE, _ColorSpaceType.SRGB, False), RenderingIntent.Relative)
        cmm.do_transform_16_8(tr, cv2.cvtColor(ws_img, cv2.COLOR_BGR2RGB), trg_img, ws_img.size // 3)
        return cv2.cvtColor(trg_img, cv2.COLOR_RGB2BGR)  # type: ignore

    def workspace_to_srgb(self, ws_img: NDArray[np.uint16]):
        '''
        For debugging.
        '''
        if ws_img.shape[2] == 4:
            ws_img = ws_img[:, :, :3]
        trg_img = np.zeros(ws_img.shape, dtype=np.uint8)
        tr = self._get_transform(_ColorConversionType(_ColorSpaceType.WORKSPACE, _ColorSpaceType.SRGB, False), RenderingIntent.Relative)
        cmm.do_transform_16_8(tr, cv2.cvtColor(ws_img, cv2.COLOR_BGR2RGB), trg_img, ws_img.size // 3)
        pimg = PILImageModule.fromarray(trg_img)
        pimg.info['icc_profile'] = SRGB_PROF
        return pimg


DEFAULT_CC = ColorConverter(ICC_DIR / 'sublinova-epson4pigment-PBT-20231121_srgb.icc')
