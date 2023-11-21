from keycap_designer.manuscript import *


def generate():
    '''
    This content shows all available XDA keycaps/sides on DecentKeyboards custom printing service.
    '''
    m = Profile('XDA')
    style = Style(2.5, 1.5, 1., APP_FONT_DIR / 'OpenSans-VariableFont_wdth,wght.ttf')
    front = style.mod(side=FrontSide).shift(x=1.)

    ms = [
        m @ Specifier(s) @ Legend({style: s})
        for s in [
            '1u',
            '125u',
            '15u',
            '175u',
            '2u',
            '225u',
            '275u',
        ]
    ]
    ms[0] @= Legend({front: '1u'})
    s = 'Homing 1u'
    ms.append(
        m @ Specifier(s) @ Legend({
            style.mod(variation_name='Condensed Regular'): s,
            front.mod(variation_name='Condensed Regular'): s})
    )

    return ms


CONTENT = generate()
