from keycap_designer.manuscript import *


def generate():
    '''
    DecentKeyboard custom printing can do much for Junana.
    Let's see the difference.
    Unlike XDA, I can print all five sides of keycaps.
    '''
    ms: list[Manuscript] = []
    m = Profile('Junana') @ Specifier('1u')

    style = Style(2, 1, 1., APP_FONT_DIR / 'damase_v.2.ttf')
    front = style.mod(x_loc=1.5, y_loc=1.5, side=FrontSide)

    pale_red = sRGBColor(255, 180, 180)
    pale_blue = sRGBColor(180, 180, 255)
    pale_red_bc = BackgroundColor(pale_red)
    pale_red_tsc = SideColor({TopSide: pale_red})
    pale_blue_tsc = SideColor({TopSide: pale_blue})
    pale_blue_fsc = SideColor({FrontSide: pale_blue})

    ms.append(m @ Legend({style: 'BC'}) @ pale_red_bc)
    # BackgroundColor object affects all five sides.

    ms.append(m @ Legend({style: 'Top SC'}) @ pale_red_tsc)
    # If you just fill top-side, use SideColor object.

    ms.append(m @ Legend({front: 'Front SC'}) @ pale_blue_fsc)
    # SideColor object of front-side becomes like this.

    ms.append(m @ Legend({style: 'Top SC', front: 'BC'}) @ pale_blue_tsc @ pale_red_bc)
    # You can combine BackgroundColor and SideColor objects.

    # You can see front-side legends are a bit deformed. It is adjusted to look good
    # when it is printed to actual keycaps. Good but not perfect, sorry.

    ms.append(m @ Wallpaper(here() / 'test_pattern.png'))
    # Wallpaper covers all five sides.

    ms.append(m @ Wallpaper(here() / 'test_image.png'))
    # You can print one image file to all five sides.

    return ms


CONTENT = generate()
