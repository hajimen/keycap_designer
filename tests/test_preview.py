# cSpell:disable
import unittest
import pprint
from keycap_designer.constants import CURRENT_DIR
from keycap_designer.preview import _generate_map, print_rc_map, print_preview
from keycap_designer.manuscript import *
from tests.common import assert_pdf


KLE_FILE = CURRENT_DIR / 'layout/test.json'


class TestPreview(unittest.TestCase):
    def test_generate_map(self):
        kle_map, _ = _generate_map(KLE_FILE)
        oracle = CURRENT_DIR / 'tests/oracle/generate_map.txt'
        txt = pprint.pformat(kle_map)
        # with open(oracle, 'w') as f:
        #     f.write(txt)
        with open(oracle, 'r') as f:
            self.assertEqual(f.read(), txt)

    def test_print_rc_map(self):
        RC_FILE = CURRENT_DIR / 'tmp/rc.pdf'
        print_rc_map(KLE_FILE, RC_FILE, unit_test=True)
        assert_pdf(self, RC_FILE, 'test_print_rc_map')

    def test_preview(self):
        PREVIEW_FILE = CURRENT_DIR / 'tmp/preview.pdf'
        m = Row(2) @ Profile('XDA') @ Specifier('1u') @ BackgroundColor(sRGBColor(220, 220, 220)) @ Layout('test')
        ts = Style(4., 2., 2., DESC_FONT_PATH)
        fs = Style(4., 4., 2., DESC_FONT_PATH, side=FrontSide)
        ms = m >> [Legend({ts: str(i + 1), fs: str(i + 1)}) @ Col(i + 1) for i in range(3)]
        ms[0] = ms[0] @ Specifier('Homing 1u')
        ms[1] = ms[1] @ Repeat(3)
        ms.append(m @ Row(1) @ Specifier('2u') @ Legend({ts: '2u'}) @ Rotation(RotationAngle.CW) @ Col(5))
        m2 = Profile('XDA') @ Specifier('1u') @ BackgroundColor(sRGBColor(220, 220, 220)) @ Legend({ts: 'NL', fs: 'NL'})
        ms.append(m2)
        ms.append(m2 @ Wallpaper(CURRENT_DIR / 'tests/resource/test_pattern.png'))
        ms.append(m2 @ Specifier('125u'))
        ms.append(m2 @ Specifier('15u'))
        ms.append(m2 @ Specifier('175u'))
        ms.append(m2 @ Specifier('2u'))
        ms.append(m2 @ Specifier('225u'))
        ms.extend([m2 @ Specifier('275u') @ Repeat(3) @ Comment(f'Lorem Ipsum {9 - i}') for i in range(21)])
        print_preview([manuscript_to_artwork(i) for i in ms], PREVIEW_FILE, True)
        assert_pdf(self, PREVIEW_FILE, 'test_preview')
