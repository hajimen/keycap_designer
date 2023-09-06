import unittest
from keycap_designer.constants import CURRENT_DIR
from keycap_designer.preview import print_rc_map, print_preview
from keycap_designer.manuscript import *
from tests.common import assert_pdf


NW = Style(4., 2., 2., DESC_FONT_PATH)
SW = Style(4., 2., 2., DESC_FONT_PATH, v_o=Bottom)
FRONT = Style(4, 3., 2., DESC_FONT_PATH, side=FrontSide)


def leg(t: str, b=''):
    return Legend({NW: t, SW: b})


class TestLayout(unittest.TestCase):
    def rc_map(self, layout_name: str):
        RC_FILE = CURRENT_DIR / f'tmp/rc_{layout_name}.pdf'
        print_rc_map(CURRENT_DIR / f'layout/{layout_name}.json', RC_FILE, unit_test=True)
        assert_pdf(self, RC_FILE, f'test_rc_map_{layout_name}')

    def preview(self, layout_name: str, ms: ty.Sequence[Manuscript]):
        PREVIEW_FILE = CURRENT_DIR / f'tmp/{layout_name}.pdf'
        m = Profile('XDA') @ Specifier('1u') @ BackgroundColor(sRGBColor(180, 180, 180)) @ Layout(layout_name)
        print_preview([manuscript_to_artwork(i) for i in m >> ms], PREVIEW_FILE, True)
        assert_pdf(self, PREVIEW_FILE, f'test_layout_preview_{layout_name}')

    def test_starter_kit(self):
        layout_name = 'p2ppcb-starter-kit'
        self.rc_map(layout_name)

        r0 = Col(0) ** [
            leg('F2'),
            leg('Home'),
            leg('PgUp'),
        ]

        r1 = Col(0) ** [
            leg('Del'),
            leg('End'),
            leg('PgDn'),
        ]

        r2 = Col(0) ** [
            leg('←'),
            leg('↑'),
            leg('Ctrl'),
        ]

        r3 = Col(1) ** [
            leg('↓'),
            leg('→'),
        ]

        ms = (Row(0) >> r0) + (Row(1) >> r1) + (Row(2) >> r2) + (Row(3) >> r3)
        self.preview(layout_name, ms)

    def test_ansi_104(self):
        layout_name = 'ansi-104'
        self.rc_map(layout_name)

        r5 = []
        r5.append(leg('Esc') @ Col(0))
        r5.extend(Col(2) ** [leg(f'F{i + 1}') for i in range(12)] +
                  Col(14) ** [leg('PrtSc'), leg('ScrLk'), leg('Pause')])

        r4 = Col(0) ** [
            leg('~', "`"),
            leg('!', '1'),
            leg('@', '2'),
            leg('#', '3'),
            leg('$', '4'),
            leg('%', '5'),
            leg('^', '6'),
            leg('&', '7'),
            leg('*', '8'),
            leg('(', '9'),
            leg(')', '0'),
            leg('_', '-'),
            leg('+', '='),
            leg('BackSp') @ Specifier('2u'),
            leg('Ins'),
            leg('Home'),
            leg('PgUp'),
            leg('NumLk'),
            leg('/'),
            leg('*'),
            leg('-'),
        ]

        r3 = Col(0) ** [
            leg('Tab') @ Specifier('15u'),
            leg('Q'),
            leg('W'),
            leg('E'),
            leg('R'),
            leg('T'),
            leg('Y'),
            leg('U'),
            leg('I'),
            leg('O'),
            leg('P'),
            leg('{', '['),
            leg('}', ']'),
            leg('|', '\\') @ Specifier('15u'),
            leg('Del'),
            leg('End'),
            leg('PgDn'),
            leg('7'),
            leg('8'),
            leg('9'),
            leg('+') @ Specifier('2u') @ Rotation(RotationAngle.CW),
        ]

        r2 = Col(0) ** [
            leg('CapsLk') @ Specifier('175u'),
            leg('A'),
            leg('S'),
            leg('D'),
            leg('F') @ Specifier('Homing 1u'),
            leg('G'),
            leg('H'),
            leg('J') @ Specifier('Homing 1u'),
            leg('K'),
            leg('L'),
            leg(':', ';'),
            leg('"', "'"),
            leg('Enter') @ Specifier('225u')
        ] + Col(17) ** [
            leg('4'),
            leg('5') @ Specifier('Homing 1u'),
            leg('6'),
        ]

        r1 = Col(0) ** [
            leg('Shift') @ Specifier('225u'),
            leg('Z'),
            leg('X'),
            leg('C'),
            leg('V'),
            leg('B'),
            leg('N'),
            leg('M'),
            leg('<', ','),
            leg('>', '.'),
            leg('?', '/'),
            leg('Shift') @ Specifier('275u'),
        ] + [
            leg('↑') @ Col(15),
        ] + Col(17) ** [
            leg('1'),
            leg('2'),
            leg('3'),
            leg('Enter') @ Specifier('2u') @ Rotation(RotationAngle.CW),
        ]

        r0 = (Specifier('125u') >> [
            leg('Ctrl') @ Col(0),
            leg('Win') @ Col(1),
            leg('Alt') @ Col(2),
            leg('Alt') @ Col(9),
            leg('Win') @ Col(10),
            leg('Menu') @ Col(12),
            leg('Ctrl') @ Col(13),
        ]) + Col(14) ** [
            leg('←'),
            leg('↓'),
            leg('→'),
        ] + [
            leg('0') @ Specifier('2u') @ Col(17),
            leg('.') @ Col(19),
        ]

        ms = (Row(5) >> r5) + (Row(4) >> r4) + (Row(3) >> r3) + (Row(2) >> r2) + (Row(1) >> r1) + (Row(0) >> r0)
        self.preview(layout_name, ms)
