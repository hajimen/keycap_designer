from keycap_designer.manuscript import *

NW = Style(4., 2., 2., DESC_FONT_PATH)
SW = Style(4., 2., 2., DESC_FONT_PATH, v_o=Bottom)


def leg(t: str, b=''):
    return Legend({NW: t, SW: b})


def generate():
    r5 = []
    r5.append(leg('Esc') @ Col(0))
    r5.extend(Col(2) ** ([leg(f'F{i + 1}') for i in range(12)] + [
        leg('PrtSc'),
        leg('ScrLk'),
        leg('Pause'),
    ]))

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
        leg('Enter') @ Specifier('225u'),
        Skip(4),
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
        Skip(3),
        leg('↑'),
        Skip(1),
        leg('1'),
        leg('2'),
        leg('3'),
        leg('Enter') @ Specifier('2u') @ Rotation(RotationAngle.CW),
    ]

    r0 = (Specifier('125u') >> Col(0) ** [
        leg('Ctrl'),
        leg('Win'),
        leg('Alt'),
        Skip(6),
        leg('Alt'),
        leg('Win'),
        Skip(1),
        leg('Menu'),
        leg('Ctrl'),
    ]) + Col(14) ** [
        leg('←'),
        leg('↓'),
        leg('→'),
    ] + [
        leg('0') @ Specifier('2u') @ Col(17),
        leg('.') @ Col(19),
    ]

    ms = (Row(5) >> r5) + (Row(4) >> r4) + (Row(3) >> r3) + (Row(2) >> r2) + (Row(1) >> r1) + (Row(0) >> r0)
    return Profile('XDA') @ Specifier('1u') @ BackgroundColor(sRGBColor(180, 180, 180)) @ Layout('ansi-104') >> ms


CONTENT = generate()
