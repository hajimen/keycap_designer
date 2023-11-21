from keycap_designer.manuscript import *


def generate():
    '''
    This content shows all available Junana keycaps/sides on DecentKeyboards custom printing service.
    '''
    m = Profile('Junana')
    style = Style(2, 1, 1., APP_FONT_DIR / 'OpenSans-VariableFont_wdth,wght.ttf')
    front = style.mod(x_loc=1.5, side=FrontSide)

    ms = [
        m @ Specifier(s) @ Legend({style: s, front: s})
        for s in [
            '1u',
            'Homing 1u',
            'Convex 1u',
            '15u',
            'Convex 15u',
            '225u',
            'Convex 225u',
        ]
    ]

    return ms


CONTENT = generate()
