from pathlib import Path
from collections.abc import Iterable
import os
import io
from enum import Enum
from base64 import b64encode
from PIL.Image import Image as PILImage
import PIL.Image as PILImageModule
import PIL.ImageDraw as PILImageDrawModule
import PIL.ImageFont as PILImageFontModule
from keycap_designer.manuscript import Manuscript, manuscript_to_artwork, DictCombinable, Legend, ImageFile, Image, StrCombinable, Layout
from keycap_designer.preview import print_preview, artwork_simulation, _generate_map, _calc_map_size
from keycap_designer.constants import CURRENT_DIR, DPI as ARTWORK_DPI, DESC_FONT_PATH

_OUTPUT_DIR = Path.cwd()
_IS_UNIT_TEST = False
PITCH = 56
DEFAULT_DPI = 192.


def _unit_test_setting(path: Path):
    # overwrite for unit testing
    global _OUTPUT_DIR, _IS_UNIT_TEST
    _OUTPUT_DIR = path
    _IS_UNIT_TEST = True


def _image_to_html(im: PILImage):
    s = '<img src="data:image/png;base64,'
    with io.BytesIO() as buf:
        im.save(buf, format='PNG', compress_level=0)
        s += b64encode(buf.getvalue()).decode("ascii")
    s += '">'
    return s


def _rc_map_to_html(kle_json_filepath: Path):
    import numpy as np

    font = PILImageFontModule.truetype(str(DESC_FONT_PATH), 16)
    kle_map, _ = _generate_map(kle_json_filepath)
    w, h, kle_lt = _calc_map_size(kle_map)
    with PILImageModule.new('RGBA', (int(w * PITCH) + 2, int(h * PITCH) + 2), (255, 255, 255, 0)) as img:
        d = PILImageDrawModule.Draw(img)
        for (r, c), (vs, angle) in kle_map.items():
            d.polygon(list(((vs - kle_lt) * PITCH).flatten()), fill=None, outline=(0, 0, 0))
            center = (vs.max(axis=0) + vs.min(axis=0)) / 2
            center = center - np.array([0., 1 / 10])
            d.text(tuple(center * PITCH), f'{r},{c}', (0, 0, 0), font, anchor='ms')
        return _image_to_html(img)


def _layout_to_html(lo: Layout):
    p = Path(CURRENT_DIR / 'layout' / (lo.v + '.json'))
    return _rc_map_to_html(p)


def _manuscript_to_html(m: Manuscript, dpi: float = 0):
    if dpi == 0:
        dpi = DEFAULT_DPI
    mag = dpi / ARTWORK_DPI
    text_lines: list[tuple[str, str]] = []
    aw_lines: list[tuple[str, str]] = []
    d = m.dict()
    for k, v in d.items():
        if k == 'image':
            continue
        s: str
        if isinstance(v, StrCombinable):
            s = v.v.replace('\n', '<br>')
        elif isinstance(v, Legend):
            s = ''
            for _, vv in v.d.items():
                s += f'Style(...): "{vv}"<br>'
        elif isinstance(v, DictCombinable):
            s = repr(v.d)
        elif isinstance(v.v, str):
            s = v.v
        else:
            s = repr(v.v)
        text_lines.append((k, s))
    if m.profile is None:
        text_lines.append(('profile', '<b>N/A</b>'))
    if m.specifier is None:
        text_lines.append(('specifier', '<b>N/A</b>'))
    else:
        aw = manuscript_to_artwork(m)
        if len(aw.side_image) == 0:
            text_lines.append(('artwork', '<b>N/A</b>'))
        else:
            for side in sorted(aw.side_image):
                sim = artwork_simulation(aw, side)
                sim = sim.resize(list(int(d * mag) for d in sim.size))
                aw_lines.append((f'artwork<br>{side.name}', _image_to_html(sim)))
    html = ''
    for line in text_lines:
        html += '<tr><td style="text-align: right;">'
        html += line[0]
        html += '<td style="text-align: left;">'
        html += line[1]
    for line in aw_lines:
        html += '<tr><td style="text-align: right;">'
        html += line[0]
        html += '<td style="text-align: center;">'
        html += line[1]
    return '<table style="float:left; border: 1px solid;">' + html + '</table>'


def _enum_repr(self):
    cls_name = self.__class__.__name__
    return f'{cls_name}.{self.name}'


def _image_file_repr(image_file: ImageFile):
    text_lines: list[tuple[str, str]] = []
    d = image_file.dict()
    for k, v in d.items():
        if v is None:
            continue
        if not isinstance(v, str):
            v = repr(v)
        text_lines.append((k, v))
    html = ''
    for line in text_lines:
        html += '<tr><td style="text-align: right;">'
        html += line[0]
        html += '<td style="text-align: left;">'
        html += line[1]

    html += '<tr><td colspan="2" style="text-align: center;">'
    with PILImageModule.open(image_file.path) as im:
        html += _image_to_html(im)

    return '<table style="float:left; border: 1px solid;">' + html + '</table>'


def _image_repr(image: Image):
    html = '<tr>'
    for side in sorted(image.d):
        html += '<td style="text-align: center;">'
        html += side.name
    html += '<tr>'
    for side in sorted(image.d):
        html += '<td style="text-align: center;">'
        v = image.d[side]
        html += v._repr_html_()  # type: ignore
    return '<table style="float:left; border: 1px solid;">' + html + '</table>'


def _monkey_patch():
    Manuscript._repr_html_ = _manuscript_to_html  # type: ignore
    Enum.__repr__ = _enum_repr
    ImageFile._repr_html_ = _image_file_repr  # type: ignore
    Image._repr_html_ = _image_repr  # type: ignore
    Layout._repr_html_ = _layout_to_html  # type: ignore


_monkey_patch()


def _check_content(content, name: str) -> list[Manuscript]:
    cs: list[Manuscript] = []
    match content:
        case Manuscript():
            cs.append(content)
        case Iterable():
            if all(isinstance(c, Manuscript) for c in content):
                cs.extend(content)
            else:
                raise ValueError(f"The {name}() argument should be Manuscript or Iterable[Manuscript].")
        case _:
            raise ValueError(f"The {name}() argument should be Manuscript or Iterable[Manuscript].")
    return cs


def generate_pdf(content: Iterable[Manuscript] | Manuscript, pdf_path: os.PathLike | str):
    """
    Generates PDF from manuscript(s).

    Parameters
    ----------
    content: Iterable[Manuscript] | Manuscript, dpi
        Manuscript(s) to include the PDF.
    pdf_path: os.PathLike | str
        The path of the PDF.
    """
    pdf_name = _generate_pdf(content, pdf_path)
    print(f'PDF is generated. See: {pdf_name}')


def _generate_pdf(content: Iterable[Manuscript] | Manuscript, pdf_path: os.PathLike | str):
    cs = _check_content(content, 'generate_pdf')
    pdf_path = (_OUTPUT_DIR / pdf_path).resolve()
    pdf_name = pdf_path.relative_to(CURRENT_DIR)
    try:
        print_preview([manuscript_to_artwork(c) for c in cs], pdf_path, unit_test=_IS_UNIT_TEST)
    except PermissionError:
        raise PermissionError(f'Close the PDF file: "{pdf_name}"') from None
    except FileNotFoundError as e:
        raise FileNotFoundError(f'Failed to save file: "{Path(str(e)).resolve().relative_to(CURRENT_DIR)}"') from None

    return pdf_name


class SurrogateReprHtml:
    def __init__(self, html: str) -> None:
        self.html = html

    def _repr_html_(self) -> str:
        return self.html


def show_inline(content: Iterable[Manuscript] | Manuscript, dpi: float = 0):
    """
    Shows manuscript(s) as inline view.

    Parameters
    ----------
    content: Iterable[Manuscript] | Manuscript, dpi
        Manuscript(s) to show.
    dpi : float
        DPI of artwork.
    """
    ms = _check_content(content, 'show_inline')
    html = ''
    for m in ms:
        html += _manuscript_to_html(m, dpi)
    return SurrogateReprHtml(html)


def change_default_dpi(dpi: float):
    """
    Changes default DPI of artwork.

    Parameters
    ----------
    dpi : float
        Default DPI of artwork.
    """
    global DEFAULT_DPI
    DEFAULT_DPI = dpi
