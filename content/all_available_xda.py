from keycap_designer.manuscript import *


def generate():
    '''
    This content shows all available XDA keycaps/sides on DecentKeyboards custom printing service.
    '''
    m = Profile('XDA')
    style = Style(2.5, 1.5, 1., APP_FONT_DIR / 'damase_v.2.ttf')
    front = style.mod(side=FrontSide)

    ms = [
        m @ Specifier(s) @ Legend({style: s})
        for s in [
            '1u',
            'Homing 1u',
            '125u',
            '15u',
            '175u',
            '2u',
            '225u',
            '275u',
        ]
    ]
    ms[0] @= Legend({front: '1u'})
    ms[1] @= Legend({front: 'Homing 1u'})

    return ms


CONTENT = generate()
