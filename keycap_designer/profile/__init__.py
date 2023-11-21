import typing as ty
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from numpy.typing import NDArray
import PIL.Image as PILImageModule
from frozendict import frozendict
from keycap_designer.constants import Side


@dataclass(frozen=True)
class _ApertureImpl:
    mask_path: Path
    wh: tuple[int, int]
    outer_wh: tuple[int, int]
    offset: tuple[int, int]
    outer_offset: tuple[int, int]
    mask_center: tuple[int, int]
    outer_mask_center: tuple[int, int]
    mask_wh: tuple[int, int]
    name: str


class Aperture(_ApertureImpl):
    def __init__(self, mask_path: Path, name='') -> None:
        mask = PILImageModule.open(str(mask_path))
        ml = np.array(mask.getchannel('L'))
        ma = np.array(mask.getchannel('A'))
        aperture_mask = (ml > 0) & (ma > 0)
        outer_mask = (ma > 0)
        ayx = aperture_mask.max(axis=0), aperture_mask.max(axis=1)
        oyx = outer_mask.max(axis=0), outer_mask.max(axis=1)
        ab = [(np.argwhere(a).max() + 1, np.argwhere(a).min()) for a in ayx]
        ob = [(np.argwhere(o).max() + 1, np.argwhere(o).min()) for o in oyx]
        wh = ty.cast(tuple[int, int], tuple([int(ma - mi) for ma, mi in ab]))
        outer_wh = ty.cast(tuple[int, int], tuple([int(ma - mi) for ma, mi in ob]))
        offset = ty.cast(tuple[int, int], tuple([int(mi) for _, mi in ab]))
        outer_offset = ty.cast(tuple[int, int], tuple([int(mi) for _, mi in ob]))
        mask_center = ty.cast(tuple[int, int], tuple([int((ms // 2) - mi) for ms, (_, mi) in zip(mask.size, ab)]))
        outer_mask_center = ty.cast(tuple[int, int], tuple([int((ms // 2) - mi) for ms, (_, mi) in zip(mask.size, ob)]))
        super().__init__(mask_path, wh, outer_wh, offset, outer_offset, mask_center, outer_mask_center, mask.size, name)


CapBase = frozendict[Side, Aperture]

Sp_Cb_Dict = ty.Mapping[str, CapBase]
Sp_Comment_Dict = ty.Mapping[str, str]


@dataclass(frozen=True)
class Profile:
    name: str
    sp_cb_dict: Sp_Cb_Dict
    sp_comment_dict: Sp_Comment_Dict
    modify_side_fg_image: ty.Callable[[CapBase, dict[Side, NDArray[np.uint16]]], dict[Side, NDArray[np.uint16]]] | None = None  # bundle multiple sides to one


def _available_profiles() -> dict[str, Profile]:
    from keycap_designer.profile.xda import PROFILE as xda_prof
    from keycap_designer.profile.junana import PROFILE as junana_prof
    return {
        xda_prof.name: xda_prof,
        junana_prof.name: junana_prof
    }


PROFILES = _available_profiles()
