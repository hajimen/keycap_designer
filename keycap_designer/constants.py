from enum import Enum, auto
from pathlib import Path
import os
import platform
from ordered_enum.ordered_enum import OrderedEnum


class Orientation(Enum):
    LeftTop = auto()
    Center = auto()
    RightBottom = auto()


Left = Orientation.LeftTop
Center = Orientation.Center
Right = Orientation.RightBottom
Top = Left
Bottom = Right


class ImageFit(Enum):
    KeepAspect = auto()
    Crop = auto()
    Expand = auto()
    PixelWise = auto()


Aspect = ImageFit.KeepAspect
Crop = ImageFit.Crop
Expand = ImageFit.Expand
PixelWise = ImageFit.PixelWise


class ImageInterpolate(Enum):
    Cubic = auto()
    Nearest = auto()


Cubic = ImageInterpolate.Cubic
Nearest = ImageInterpolate.Nearest


class ImageTrim(Enum):
    Inner = auto()
    Outer = auto()


TrimInner = ImageTrim.Inner
TrimOuter = ImageTrim.Outer


class Side(OrderedEnum):
    Top = auto()
    Front = auto()
    TopFront = auto()


TopSide = Side.Top
FrontSide = Side.Front


CURRENT_DIR = Path(os.getcwd())
RESOURCE_DIR = Path(os.path.dirname(__file__))
OS_FONT_DIR = {
    'Windows': Path(r'C:\Windows\Fonts'),
    'Darwin': Path('/Library/Fonts'),
    'Linux': Path('/usr/share/fonts')
}[platform.system()]
APP_FONT_DIR = CURRENT_DIR / 'font'
DESC_FONT_PATH = RESOURCE_DIR / 'font/NotoSansMono-VariableFont_wdth,wght.ttf'
DPI = 720
IPM = 25.4
DPM = DPI / IPM
MAX_RANK = 100
MAX_N_CB = 10
