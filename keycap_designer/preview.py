import re
from collections import defaultdict, abc
from pathlib import Path
import datetime as dt
import io
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.graphics import renderPDF, shapes
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph
from reportlab.platypus.tables import Table, TableStyle
from reportlab.platypus.flowables import Image
import numpy as np
from numpy.typing import NDArray
import PIL.Image as PILImageModule
from PIL.Image import Image as PILImage
from keycap_designer.profile import Profile as JigProfile
from keycap_designer.constants import Side, DPM, DESC_FONT_PATH, CURRENT_DIR
from keycap_designer.manuscript import ArtWork, ColorConversionIntent
from keycap_designer.profile import Aperture
from keycap_designer.color_management import DEFAULT_CC
import pykle_serial as kle_serial


KleMap = dict[tuple[int, int], tuple[NDArray[np.float64], float]]
PAPER_WIDTH = 297.
MARGIN = 10.
LIVE_WIDTH = PAPER_WIDTH - MARGIN * 2
LIVE_HEIGHT = 190.
pdfmetrics.registerFont(TTFont("OpenSans", str(DESC_FONT_PATH)))
DEFAULT_PITCH = 19.
SIMULATE_ANTI_BLEED = False


def set_simulate_anti_bleed(enable: bool):
    global SIMULATE_ANTI_BLEED
    SIMULATE_ANTI_BLEED = enable


def _generate_map(kle_json_filepath: Path):
    with open(kle_json_filepath, 'r', encoding='utf-8') as f:
        keyboard = kle_serial.parse(f.read())
    ret: KleMap = {}
    for k in keyboard.keys:
        left = k.x
        right = k.x + k.width
        top = k.y
        bottom = k.y + k.height
        wh = sorted([k.width, k.height])
        if wh[0] == 1 and k.width2 == k.width and k.height == k.height2 and k.x2 == 0 and k.y2 == 0:
            vs = np.array([
                [left, top], [left, bottom], [right, bottom], [right, top]
            ])
        else:
            left2 = k.x + k.x2
            right2 = k.x + k.x2 + k.width2
            top2 = k.y + k.y2
            bottom2 = k.y + k.y2 + k.height2
            if left == left2:
                if top == top2:
                    vs = np.array([
                        [left, top], [left, bottom], [right, bottom], [right, bottom2], [right2, bottom2], [right2, top]
                    ])
                else:  # bottom == bottom2
                    vs = np.array([
                        [left, top], [left, bottom], [right2, bottom], [right2, top2], [right, top2], [right, top]
                    ])
            else:  # right == right2
                if top == top2:
                    vs = np.array([
                        [left2, top], [left2, bottom2], [left, bottom2], [left, bottom], [right, bottom], [right, top]
                    ])
                else:  # bottom == bottom2
                    vs = np.array([
                        [left, top], [left, top2], [left2, top2], [left2, bottom], [right, bottom], [right, top]
                    ])

        if k.rotation_angle != 0:
            vs = np.insert(vs, 2, 1., axis=1)
            orig_mat = np.array([[1., 0., -k.rotation_x], [0., 1., -k.rotation_y], [0., 0., 1.]])
            trans_mat = np.array([[1., 0., k.rotation_x], [0., 1., k.rotation_y], [0., 0., 1.]])
            r = k.rotation_angle * np.pi / 180
            rot_mat = np.array([[np.cos(r), -np.sin(r), 0.], [np.sin(r), np.cos(r), 0.], [0., 0., 1.]])
            vst = trans_mat @ rot_mat @ orig_mat @ vs.transpose(1, 0)
            vs = vst.transpose(1, 0)[:, :2]

        try:
            r = int(k.labels[9])
            c = int(k.labels[10])
        except Exception as e:
            raise Exception(f'layout KLE file lacks row-col label. filename:{kle_json_filepath.name}', e)

        ret[r, c] = (vs, k.rotation_angle)  # type: ignore

    return ret, keyboard.meta


def _shape_polygon(vertices: NDArray, fillColor=colors.transparent, strokeColor=colors.black):
    return shapes.Polygon(list((vertices * mm).flatten()), fillColor=fillColor, strokeColor=strokeColor)


def _calc_map_size(kle_map: KleMap):
    xs = []
    ys = []
    for (r, c), (vs, angle) in kle_map.items():
        xs.extend(vs[:, 0])
        ys.extend(vs[:, 1])
    x = min(xs)
    y = min(ys)
    w = max(xs) - x  # type: ignore
    h = max(ys) - y  # type: ignore
    return w, h, np.array([x, y])


def print_rc_map(kle_json_filepath: Path, rc_map_filepath: Path, unit_test=False):
    doc = Document(rc_map_filepath)
    if unit_test:
        doc.timestamp = '-'
    doc.canvas.setAuthor("keycap-designer")
    doc.canvas.setTitle('RC map')
    doc.canvas.setSubject('RC map')
    doc.init_page()

    kle_map, _ = _generate_map(kle_json_filepath)
    w, h, kle_lt = _calc_map_size(kle_map)
    pitch = DEFAULT_PITCH
    if w * pitch > LIVE_WIDTH:
        pitch = LIVE_WIDTH / w
    if h * pitch > LIVE_HEIGHT - 15.:
        pitch = (LIVE_HEIGHT - 15.) / h

    doc.canvas.setFont('OpenSans', 7 * mm)
    doc.canvas.drawCentredString((LIVE_WIDTH / 2) * mm, (LIVE_HEIGHT - 10.) * mm, 'RC map: ' + kle_json_filepath.stem)
    doc.canvas.translate(((LIVE_WIDTH - w * pitch) / 2) * mm, ((LIVE_HEIGHT - 15. - h * pitch) / 2) * mm)
    doc.canvas.setFont('OpenSans', (pitch / 3) * mm)
    d = shapes.Drawing()
    for (r, c), (vs, angle) in kle_map.items():
        vs = np.array([0., h]) + np.array([1., -1.]) * (vs - kle_lt)
        d.add(_shape_polygon(vs * pitch))
        center = (vs.max(axis=0) + vs.min(axis=0)) / 2
        center = center - np.array([0., 1 / 10])
        doc.canvas.drawCentredString(*tuple(center * pitch * mm), text=f'{r},{c}')  # type: ignore
    doc.draw_shape(d)
    doc.canvas.save()


def _margin_simulation(img: NDArray, cci: ColorConversionIntent, aperture: Aperture):
    img3 = img[:, :, :3]
    mask = PILImageModule.open(str(aperture.mask_path))
    ml = np.array(mask.getchannel('L')) == 0
    ma = np.array(mask.getchannel('A')) == 0
    ml = ml & (np.bitwise_not(ma))
    img3[ml] = ((img3[ml].astype(np.uint32) + 30000 * 3) / 4).astype(np.uint16)
    if SIMULATE_ANTI_BLEED:
        from kp3.anti_bleed import simulation as simulation_anti_bleed  # type: ignore
        return simulation_anti_bleed(img3, cci)
    else:
        return DEFAULT_CC.workspace_to_soft_proof(img3, cci.rendering_intent(), cci.bpc())


def print_preview(aws: abc.Sequence[ArtWork], preview_filepath: Path, unit_test=False):
    doc = Document(preview_filepath, preview=True)
    if unit_test:
        doc.timestamp = '-'
    doc.canvas.setAuthor("keycap-designer")
    doc.canvas.setTitle('preview')
    doc.canvas.setSubject('preview')
    doc.init_page()

    # group by profile, group, layout
    layout_aws: dict[tuple[JigProfile, str, str], list[ArtWork]] = defaultdict(list)
    non_layout_aws: dict[tuple[JigProfile, str, str], list[ArtWork]] = defaultdict(list)
    has_layout = False
    for aw in aws:
        non_layout_aws[aw.profile, aw.group, aw.specifier].append(aw)
        if aw.layout == '':
            continue
        layout_aws[aw.profile, aw.group, aw.layout].append(aw)
        has_layout = True
    simulation_cache: dict[int, PILImage] = {}
    first_page = True
    doc.canvas.setLineWidth(0.1 * mm)
    for (jig_prof, group, layout), saws in layout_aws.items():
        rc_d: dict[int, dict[int, ArtWork]] = defaultdict(dict)
        sides: set[Side] = set()
        for aw in saws:
            detail = [f'Profile:{aw.profile.name}']
            if len(aw.group) > 0:
                detail.append(f'Group:{aw.group}')
            detail.append(f'Layout:{aw.layout}')
            if aw.row == -1 or aw.col == -1:
                raise Exception('Layout specified but Row-Col not found:  ' + '  '.join(detail))
            detail.append(f'Row:{aw.row}')
            detail.append(f'Col:{aw.col}')
            if aw.col in rc_d[aw.row]:
                raise Exception('Row-Col collision:  ' + '  '.join(detail))
            rc_d[aw.row][aw.col] = aw
            sides |= aw.side_image.keys()
        layout_kle_filepath = CURRENT_DIR / f'layout/{layout}.json'
        if not layout_kle_filepath.exists():
            raise Exception(f'KLE file not found.  Layout:{layout}')
        kle_map, meta = _generate_map(layout_kle_filepath)
        ma = re.search(r'pitch:(\d+(?:\.\d+)?)', meta.notes)
        pitch = float(ma.groups()[0]) if ma is not None else DEFAULT_PITCH
        w, h, kle_lt = _calc_map_size(kle_map)
        mag = 1.
        if w * pitch > LIVE_WIDTH:
            mag = LIVE_WIDTH / (w * pitch)
        if h * pitch * mag > LIVE_HEIGHT - 15.:
            mag = (LIVE_HEIGHT - 15.) / h * pitch
        inv_mag_percent = int(np.ceil(100 / mag))
        mag = 100 / inv_mag_percent

        doc.canvas.setFont('OpenSans', 3 * mm)
        for side in sorted(sides):
            if not first_page:
                doc.canvas.showPage()
                doc.init_page()
            doc.canvas.setFont('OpenSans', 7 * mm)
            details = [f'profile: {jig_prof.name}']
            if group != "":
                details.append(f'group: {group}')
            details.append(f'layout: {layout}')
            details.append(f'side:{side.name}')
            if inv_mag_percent != 100:
                details.append(f'scale:{inv_mag_percent}%')
            doc.canvas.drawCentredString((LIVE_WIDTH / 2) * mm, (LIVE_HEIGHT - 12.) * mm, '   '.join(details))
            doc.canvas.translate(((LIVE_WIDTH - w * pitch * mag) / 2) * mm, ((LIVE_HEIGHT - 15. - h * pitch * mag) / 2) * mm)
            doc.canvas.scale(mag, mag)
            COMMENT_REPEAT_FONT_SIZE = 2
            doc.canvas.setFont('OpenSans', COMMENT_REPEAT_FONT_SIZE * mm)
            first_page = False
            d = shapes.Drawing()
            for (r, c), (vs, angle) in kle_map.items():
                vs = np.array([0., h]) + np.array([1., -1.]) * (vs - kle_lt)
                if r in rc_d and c in rc_d[r] and side in rc_d[r][c].side_image:
                    pass
                else:
                    d.add(_shape_polygon(vs * pitch))
            doc.draw_shape(d)
            d = shapes.Drawing()
            for (r, c), (vs, angle) in kle_map.items():
                vs = np.array([0., h]) + np.array([1., -1.]) * (vs - kle_lt)
                if r in rc_d and c in rc_d[r] and side in rc_d[r][c].side_image:
                    aw = rc_d[r][c]
                    img = aw.side_image[side]
                    iwh = (np.array(img.shape[:2]) / DPM)[::-1]
                    iw, ih = iwh
                    aperture = aw.cb[side]
                    if id(img) in simulation_cache:
                        sim = simulation_cache[id(img)]
                    else:
                        sim = _margin_simulation(img, aw.cci, aperture)
                        simulation_cache[id(img)] = sim
                    center = ((vs.max(axis=0) + vs.min(axis=0)) / 2) * pitch
                    doc.canvas.saveState()
                    doc.canvas.translate(center[0] * mm, center[1] * mm)
                    if angle != 0.:
                        doc.canvas.rotate(-angle)
                    white_back = PILImageModule.fromarray((img[:, :, 3] // 257).astype(np.uint8), 'L').convert('RGB')
                    doc.canvas.drawImage(ImageReader(white_back),
                                         (- iw / 2.) * mm, (- ih / 2.) * mm,
                                         iw * mm, ih * mm, [0] * 6, True)
                    doc.canvas.drawImage(ImageReader(sim),
                                         (- iw / 2.) * mm, (- ih / 2.) * mm,
                                         iw * mm, ih * mm, [254, 255] * 3, True)
                    if aw.comment != '':
                        ch = ih / 2 - (aperture.outer_offset[1] + aperture.outer_wh[1]) / DPM - COMMENT_REPEAT_FONT_SIZE
                        doc.canvas.drawCentredString(0., ch * mm, aw.comment.replace('\r', ' '))
                    if aw.repeat != 1:
                        rh = ih / 2 - aperture.outer_offset[1] / DPM
                        doc.canvas.drawCentredString(0., rh * mm, f'{aw.repeat} pcs')
                    doc.canvas.restoreState()
            doc.draw_shape(d)
    y = 0.
    ts = TableStyle(
        [('ALIGN', (0, 0), (-1, -1), 'CENTER'),
         ('BOX', (0, 0), (-1, -1), 2, colors.black)]
    )
    ps = ParagraphStyle('foo', **{
        "fontName": "OpenSans",
        "fontSize": 2.5 * mm,
        "leading": 4 * mm,
        'alignment': TA_CENTER
    })
    next_page = not first_page
    y = 5.
    for (jig_prof, group, specifier), nl_aws in non_layout_aws.items():
        if next_page:
            doc.canvas.showPage()
            doc.init_page()
            next_page = False
        x = 0.
        rh = 0.
        first_row = True
        first_cap = True
        nl_aws = sorted(nl_aws, key=lambda x: x.rank)

        def _draw_caption(continued: bool):
            doc.canvas.setFont('OpenSans', 5 * mm)
            details = [f'profile: {jig_prof.name}']
            if group != "":
                details.append(f'group: {group}')
            details.append(f'specifier: {specifier}')
            s = '  '.join(details)
            if continued:
                s = 'continued from previous page.   ' + s
            doc.canvas.drawString(0., (LIVE_HEIGHT - y - 5.) * mm, s)

        def _draw_row(to_draw: list[tuple[Table, float, float]]):
            for t, x, th in to_draw:
                t.drawOn(doc.canvas, x * mm, (LIVE_HEIGHT - y - th) * mm)

        tables = []
        for i, aw in enumerate(nl_aws):
            content = []
            mw = 0.
            mh = 0.
            if aw.repeat > 1:
                content.append([Paragraph(f'{aw.repeat} pcs', ps), ])
            for side in sorted(aw.side_image):
                img = aw.side_image[side]
                aperture = aw.cb[side]
                iwh = (np.array(img.shape[:2]) / DPM)[::-1]
                iw, ih = iwh
                mw = max(iw, mw)
                mh = max(ih, mh)
                if id(img) in simulation_cache:
                    sim = simulation_cache[id(img)]
                else:
                    sim = _margin_simulation(img, aw.cci, aperture)
                    simulation_cache[id(img)] = sim
                buf = io.BytesIO()
                sim.save(buf, format='PNG', compress_level=0)
                buf.seek(0)
                content.append([Image(buf, iw * mm, ih * mm), ])
            if len(aw.side_image) == 0:
                content.append([Paragraph('blank keycap found', ps), ])
                mw = 15.
            if aw.comment != '' or has_layout:
                comments = aw.comment.split('\r')
                comments = [c for c in comments if c != 'homing' and c != '']
                if aw.layout == '':
                    comments.append('not in layout')
                content.append([Paragraph('\r'.join(comments), ps), ])
            t = Table(content, style=ts)
            tw, th = t.wrap(mw * mm + 12, mh * mm)  # The '12' is bug workaround of ReportLab.
            tw /= mm
            th /= mm
            if x + tw > LIVE_WIDTH:
                if LIVE_HEIGHT - y < rh:
                    doc.canvas.showPage()
                    doc.init_page()
                    first_row = True
                    y = 5.
                if first_row:
                    _draw_caption(not first_cap)
                    first_cap = False
                    first_row = False
                    y += 7.
                _draw_row(tables)
                tables = []
                y += rh
                rh = 0.
                x = 0.
            tables.append((t, x, th))
            rh = max(rh, th)
            if i + 1 == len(nl_aws):
                if LIVE_HEIGHT - y < rh + 7.:
                    doc.canvas.showPage()
                    doc.init_page()
                    first_row = True
                    y = 5.
                if first_row:
                    _draw_caption(not first_cap)
                    first_cap = False
                    first_row = False
                    y += 7.
                _draw_row(tables)
                tables = []
                y += rh
                rh = 0.
                x = 0.
            else:
                x += tw
        y += 2.
    doc.canvas.save()

    from safetensors.numpy import save
    from pikepdf import Pdf, AttachedFileSpec
    pdf = Pdf.open(preview_filepath, allow_overwriting_input=True)
    import json
    from dataclasses import asdict
    import zlib
    from keycap_designer import version
    jd = {}
    for i, aw in enumerate(aws):
        d = asdict(aw)
        del d['profile']
        del d['cb']
        del d['cci']
        del d['side_image']
        d['color_conversion_intent'] = aw.cci.value
        d['profile_name'] = aw.profile.name
        json_d = json.dumps(d).encode('utf8')
        jd[f'property_json_{i}'] = np.array(list(json_d), np.uint8)
        for side, img in aw.side_image.items():
            jd[f'{side.name}_{i}'] = img
    b = zlib.compress(save(jd), level=3)
    filespec = AttachedFileSpec(pdf, b, mime_type='binary/octet-stream')  # type: ignore
    pdf.attachments[f'keycap-designer-{version}.safetensors'] = filespec
    pdf.save()
    pdf.close()


class Document:
    def __init__(self, filepath: Path, preview=False) -> None:
        self.timestamp = dt.datetime.now().strftime("%Y/%m/%d %H:%M")
        self.canvas = canvas.Canvas(str(filepath))
        self.i_page = 0
        self.preview = preview

    def init_page(self):
        self.canvas.setPageSize(((LIVE_WIDTH + MARGIN * 2) * mm, (LIVE_HEIGHT + MARGIN * 2) * mm))
        self.canvas.translate(MARGIN * mm, MARGIN * mm)
        self.canvas.saveState()
        self.canvas.setFont('OpenSans', 5 * mm)
        self.canvas.drawRightString(LIVE_WIDTH * mm, (LIVE_HEIGHT - 5.) * mm, self.timestamp + f'   #{self.i_page + 1}')
        if self.preview:
            self.canvas.drawRightString(LIVE_WIDTH * mm, 2. * mm, 'To order custom printed keycaps, send this PDF file to hajime@kaoriha.org.')
        self.i_page += 1

    def draw_shape(self, d: shapes.Drawing):
        renderPDF.draw(d, self.canvas, 0, 0)
